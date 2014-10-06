from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config
from openerp.osv import orm, fields, osv
from pprint import pprint as pp
from openerp import SUPERUSER_ID
import logging
from pprint import pprint as pp
from openerp.addons.nh_activity.activity import except_if
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class nh_clinical_demo_env(orm.Model):
    _name = 'nh.clinical.demo.env'
    
    _columns = {
        'bed_qty': fields.integer('Bed Qty'),
        'ward_qty': fields.integer('Ward Qty'),
        'adt_user_qty': fields.integer('ADT User Qty'),
        'nurse_user_qty': fields.integer('Nurse User Qty'), 
        'ward_manager_user_qty': fields.integer('Ward Manager User Qty'),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS'),
        
    }
    _defaults = {
         'bed_qty': 3,
         'ward_qty': 2,
         'adt_user_qty': 1,
         'nurse_user_qty': 2,
         'ward_manager_user_qty': 2,
    }
    
    def data_unique_login(self, cr, uid, initial_login=None):
        fake.seed(next_seed())
        login = initial_login or fake.first_name().lower()
        sql = "select 1 from res_users where login='%s'"
        cr.execute(sql % login) 
        i = 0
        while cr.fetchone():
            i += 1
            login = fake.first_name().lower() 
            cr.execute(sql % login)
            except_if(i > 100, msg="Can't get unique login after 100 iterations!")
        return login
    
    def fake_data(self, cr, uid, env_id, model, data={}):
        """
        This method returns fake data for model
        Extend this method to add fake data for other models 
        """
        data_copy = data.copy()
        method_map = {
            # Base      
            'nh.clinical.location.bed': 'data_location_bed',
            'nh.clinical.location.ward': 'data_location_ward',
            'nh.clinical.location.pos': 'data_location_pos',
            'nh.clinical.location.admission': 'data_location_admission',
            'nh.clinical.location.discharge': 'data_location_discharge',
            'nh.clinical.pos': 'data_pos',
        }
        #import pdb; pdb.set_trace()
        res = None
        if method_map.get(model) and hasattr(nh_clinical_demo_env, method_map[model]):
            res = eval("self.%s(cr, uid, env_id, data=data_copy)" % method_map[model])  
        except_if(not res, msg="Data method is not defined for model '%s'" % model)
        return res
    
    def data_location_bed(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
        env = self.browse(cr, SUPERUSER_ID, env_id) 
        api_pool = self.pool['nh.clinical.api']
        locations = api_pool.get_locations(cr, uid, pos_ids=[env.pos_id.id], usages=['ward'])
        if not locations:
            _logger.warn("No ward locations found. Beds will remain without parent location!")
        code = "BED_"+str(fake.random_int(min=1000, max=9999))
        d = {
               'name': code,
               'code': code,
               'type': 'poc',
               'usage': 'bed',
               'parent_id': locations and fake.random_element(locations).id or False
        }        
        d.update(data)        
        return d

    def data_location_ward(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
        env = self.browse(cr, SUPERUSER_ID, env_id) 
        code = "WARD_"+str(fake.random_int(min=100, max=999))
        d = {
               'name': code,
               'code': code,
               'type': 'structural',
               'usage': 'ward',
               'parent_id': env.pos_id.location_id.id
        }       
        d.update(data)        
        return d        
        
    def data_location_pos(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())        
        code = "POS_"+str(fake.random_int(min=100, max=999))
        d = {
               'name': "POS Location (%s)" % code,
               'code': code,
               'type': 'structural',
               'usage': 'hospital',
               }        
        d.update(data)
        return d

    def data_location_admission(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())        
        code = "ADMISSION_"+str(fake.random_int(min=100, max=999))
        d = {
               'name': code,
               'code': code,
               'type': 'structural',
               'usage': 'room',
               }        
        d.update(data)
        return d

    def data_location_discharge(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())        
        code = "DISCHARGE_"+str(fake.random_int(min=100, max=999))
        d = {
               'name': code,
               'code': code,
               'type': 'structural',
               'usage': 'room',
               }        
        d.update(data)
        return d

    def data_pos(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())        
        d = {
                'name': "HOSPITAL_"+str(fake.random_int(min=100, max=999)),
            }         
        d.update(data)
        return d
        
    def create_activity(self, cr, uid, env_id, data_model, activity_vals={}, data_vals={}, no_fake=False, return_id=False):
        activity_pool = self.pool['nh.activity']
        data_pool = self.pool[data_model]
        if not no_fake:
            dvals = self.fake_data(cr, uid, env_id, data_model, data_vals)
        else:
            dvals = data_vals.copy()        
        activity_id = data_pool.create_activity(cr, uid, activity_vals, dvals)     
        if return_id:
            return activity_id
        else:   
            return activity_pool.browse(cr, uid, activity_id)
    
    def create_complete(self, cr, uid, env_id, data_model, activity_vals={}, data_vals={}, no_fake=False, return_id=False):
        #import pdb; pdb.set_trace()
        print "activity_vals before fake: %s" %  activity_vals
        print "dvals before fake: %s" %  data_vals        
        print "create_complete.data_model: %s" % data_model
        if not no_fake:
            dvals = self.fake_data(cr, uid, env_id, data_model, data_vals)
        else:
            dvals = data_vals.copy()
        data_pool = self.pool[data_model]
        activity_pool = self.pool['nh.activity']
        print "activity_vals: %s" %  activity_vals
        print "dvals: %s" %  dvals
        
        activity_id = data_pool.create_activity(cr, uid, activity_vals, dvals)
        activity_pool.complete(cr, uid, activity_id)       
        if return_id:
            return activity_id
        else:   
            return activity_pool.browse(cr, uid, activity_id)

    def complete(self, cr, uid, env_id, activity_id, return_id=False):  
        assert activity_id
        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, activity_id)
        if return_id:
            return activity_id
        else:   
            return activity_pool.browse(cr, uid, activity_id)
    
    def submit_complete(self, cr, uid, env_id, activity_id, data_vals={}, no_fake=False, return_id=False):  
        assert activity_id
        activity_pool = self.pool['nh.activity']
        vals = self.pool['nh.clinical.api'].get_activity_data(cr, uid, activity_id)
        vals = {k: v for k, v in vals.items() if v}
        vals.update(data_vals)
        if not no_fake:
            activity = activity_pool.browse(cr, uid, activity_id)
            vals = self.fake_data(cr, uid, env_id, activity.data_model, vals)
        #import pdb; pdb.set_trace()
        activity_pool.submit(cr, uid, activity_id, vals)
        activity_pool.complete(cr, uid, activity_id)
        if return_id:
            return activity_id
        else:   
            return activity_pool.browse(cr, uid, activity_id)
    
    def create(self, cr, uid, vals={},context=None):
        env_id = super(nh_clinical_demo_env, self).create(cr, uid, vals, context)
        data = self.read(cr, uid, env_id, [])
        self.build(cr, uid, env_id)
        _logger.info("Env created id=%s data: %s" % (env_id, data))
        return env_id
        
    def build(self, cr, uid, env_id, return_id=False):
        fake.seed(next_seed())
        env = self.browse(cr, uid, env_id)
        except_if(env.pos_id, msg="Build has already been executed for the env.id=%s" % env_id)
        self.build_pos(cr, uid, env_id)
        self.build_adt_users(cr, uid, env_id)
        self.build_nurse_users(cr, uid, env_id)
        self.build_ward_manager_users(cr, uid, env_id)
        self.build_ward_locations(cr, uid, env_id)
        self.build_bed_locations(cr, uid, env_id)
        if return_id:
            return env_id
        else:
            return self.browse(cr, uid, env_id)

        
    
#     def build_patients(self, cr, uid, env_id):
#         fake.seed(next_seed())
#         env = self.browse(cr, SUPERUSER_ID, env_id)
#         assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
#         activity_pool = self.pool['nh.activity']
#         api_pool = self.pool['nh.clinical.api']
#         register_pool = self.pool['nh.clinical.adt.patient.register']
#         admit_pool = self.pool['nh.clinical.adt.patient.admit']
#         #import pdb; pdb.set_trace()
#         adt_user_id = self.get_adt_user_ids(cr, uid, env_id)[0]
#         for i in range(env.patient_qty):
#             register_activity = self.create_complete(cr, adt_user_id, env_id, 'nh.clinical.adt.patient.register')
#             admit_data = {'other_identifier': register_activity.data_ref.other_identifier}
#             admit_activity = self.create_complete(cr, adt_user_id, env_id, 'nh.clinical.adt.patient.admit', data_vals=admit_data)
#             placement_activity = self.get_activities(cr, uid, env_id, domain=[['data_model','=','nh.clinical.patient.placement'],['date_terminated','=',False]])[0]
#             self.submit_complete(cr, adt_user_id, env_id, placement_activity.id) 
            

    def build_bed_locations(self, cr, uid, env_id):
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        fake.seed(next_seed())     
        location_pool = self.pool['nh.clinical.location']     
        location_ids = []
        for i in range(env.bed_qty): 
            d = self.fake_data(cr, uid, env_id, 'nh.clinical.location.bed') 
            location_ids.append(location_pool.create(cr, uid, d)) 
            _logger.info("Bed location created id=%s data: %s" % (location_ids[-1], d))
        return location_pool.browse(cr, uid, location_ids)
    
    def build_ward_locations(self, cr, uid, env_id):
        fake.seed(next_seed())
        location_pool = self.pool['nh.clinical.location']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id   
        location_ids = []
        for i in range(env.ward_qty): 
            d = self.fake_data(cr, uid, env_id, 'nh.clinical.location.ward') 
            location_ids.append(location_pool.create(cr, uid, d)) 
            _logger.info("Ward location created id=%s data: %s" % (location_ids[-1], d))
        return location_pool.browse(cr, uid, location_ids)
    
    def build_ward_manager_users(self, cr, uid, env_id):
        """
        By default responsible for all env's ward locations
        """
        fake.seed(next_seed())
        location_pool = self.pool['nh.clinical.location']
        imd_pool = self.pool['ir.model.data']
        user_pool = self.pool['res.users']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        group = imd_pool.get_object(cr, uid, "nh_clinical_base", "group_nhc_ward_manager")
        location_ids = location_pool.search(cr, uid, [['usage','=','ward'],['pos_id','=',env.pos_id.id]])
        user_ids = []
        for i in range(env.ward_manager_user_qty):
            name = fake.first_name()          
            data = {
                'name': "Ward Manager %s" % name,
                'login': self.data_unique_login(cr, uid, name.lower()),
                'password': name.lower(),
                'groups_id': [(4, group.id)],
                'location_ids': [(4,location_id) for location_id in location_ids]
            }  
            user_id = user_pool.create(cr, uid, data)  
            user_ids.append(user_id)
            _logger.info("Ward Manager user created id=%s data: %s" % (user_id, data))
        return user_ids
 
    def build_nurse_users(self, cr, uid, env_id):
        """
        By default responsible for all env's ward locations
        """
        fake.seed(next_seed())
        location_pool = self.pool['nh.clinical.location']
        imd_pool = self.pool['ir.model.data']
        user_pool = self.pool['res.users']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        group = imd_pool.get_object(cr, uid, "nh_clinical_base", "group_nhc_nurse")
        location_ids = location_pool.search(cr, uid, [['usage','=','ward'],['pos_id','=',env.pos_id.id]])
        user_ids = []
        for i in range(env.nurse_user_qty):
            name = fake.first_name()          
            data = {
                'name': "Nurse %s" % name,
                'login': self.data_unique_login(cr, uid, name.lower()),
                'password': name.lower(),
                'groups_id': [(4, group.id)],
                'location_ids': [(4,location_id) for location_id in location_ids]
            }  
            user_id = user_pool.create(cr, uid, data)  
            user_ids.append(user_id)
            _logger.info("Nurse user created id=%s data: %s" % (user_id, data))
        return user_ids

    def build_adt_users(self, cr, uid, env_id):
        fake.seed(next_seed())
        imd_pool = self.pool['ir.model.data']
        user_pool = self.pool['res.users']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        group = imd_pool.get_object(cr, uid, "nh_clinical_base", "group_nhc_adt")
        user_ids = []
        for i in range(env.adt_user_qty):
            data = {
                'name': env.pos_id.name,
                'login': self.data_unique_login(cr, uid, env.pos_id.location_id.code.lower()),
                'password': env.pos_id.location_id.code.lower(),
                'groups_id': [(4, group.id)],
                'pos_id': env.pos_id.id
            }  
            user_id = user_pool.create(cr, uid, data)  
            user_ids.append(user_id)
            _logger.info("ADT user created id=%s data: %s" % (user_id, data))
        return user_ids
        
        # POS Location    
    def build_pos(self, cr, uid, env_id):
        fake.seed(next_seed())
        location_pool = self.pool['nh.clinical.location']
        pos_pool = self.pool['nh.clinical.pos']
        env = self.browse(cr, uid, env_id)
        # POS Location
        d = self.fake_data(cr, uid, env_id, 'nh.clinical.location.pos')
        pos_location_id = location_pool.create(cr, uid, d)
        _logger.info("POS location created id=%s data: %s" % (pos_location_id, d))
        # POS Admission Lot
        d = self.fake_data(cr, uid, env_id, 'nh.clinical.location.admission', {'parent_id': pos_location_id})
        lot_admission_id = location_pool.create(cr, uid, d)
        _logger.info("Admission location created id=%s data: %s" % (lot_admission_id, d))
        # POS Discharge Lot
        d = self.fake_data(cr, uid, env_id, 'nh.clinical.location.discharge', {'parent_id': pos_location_id})  
        lot_discharge_id = location_pool.create(cr, uid, d)       
        _logger.info("Discharge location created id=%s data: %s" % (lot_discharge_id, d)) 
        # POS
        d = self.fake_data(cr, uid, env_id, 'nh.clinical.pos',
                            {
                            'location_id': pos_location_id,
                            'lot_admission_id': lot_admission_id,
                            'lot_discharge_id': lot_discharge_id,
                            })   
        pos_id = pos_pool.create(cr, uid, d)
        _logger.info("POS created id=%s data: %s" % (pos_id, d))
        self.write(cr, uid, env_id, {'pos_id': pos_id})
        _logger.info("Env updated pos_id=%s" % (pos_id))
        return pos_id 