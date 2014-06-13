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
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed




class t4_clinical_demo_env(orm.Model):
    _name = 't4.clinical.demo.pos.env'
    
    _columns = {
        'bed_qty': fields.integer('Bed Qty'),
        'ward_qty': fields.integer('Ward Qty'),
        'adt_user_qty': fields.integer('ADT User Qty'),
        'nurse_user_qty': fields.integer('Nurse User Qty'), 
        'ward_manager_user_qty': fields.integer('Ward Manager User Qty'),  
        
        'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
        
    }
    _defaults = {
         'bed_qty': 3,
         'ward_qty': 2,
         'adt_user_qty': 1,
         'nurse_user_qty': 2,
         'ward_manager_user_qty': 2
    }



    def random_available_location_id(self, cr, uid, env_id, parent_id=None, usages=['bed'], available_range=[1,1]):
        fake.seed(next_seed())
        bed_location_ids = self.get_bed_location_ids(cr, uid, env_id)
        location_ids = self.pool['t4.clinical.api'].location_availability_map(cr, uid, 
                                                                                  ids=bed_location_ids, 
                                                                                  available_range=available_range,
                                                                                  usages=usages).keys()
        if parent_id:
            domain = [['id', 'child_of', parent_id]]
            location_ids = self.pool['t4.clinical.location'].search(cr, uid, domain)
        location_id = fake.random_element(array=location_ids)
        return location_id

    def adt_patient_admit(self, cr, uid, env_id, data={}):
        d = data.copy()
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        d = self.data_adt_patient_admit(cr, uid, env_id, d)
        activity_id = admit_pool.create_activity(cr, uid, {}, d)
        admit_pool.complete(cr, uid, activity_id)
        return activity_id

    def data_adt_patient_admit(self, cr, uid, env_id, data={}):
        """
        """
        fake.seed(next_seed())
        patient_pool = self.pool['t4.clinical.patient']
        location_pool = self.pool['t4.clinical.location']
        reg_patient_ids = self.get_patient_ids(cr, uid, env_id)
        admit_patient_ids = self.get_patient_ids(cr, uid, env_id, 't4.clinical.adt.patient.admit')
        patient_ids = list(set(reg_patient_ids) - set(admit_patient_ids))
#         if not patient_ids:
#             import pdb; pdb.set_trace()
        assert patient_ids, "No patients left to admit!"
        patients = patient_pool.browse(cr, uid, patient_ids)
        location_ids = self.get_ward_location_ids(cr, uid, env_id)
        assert location_ids, "No ward locations to set as admit location"
        locations = location_pool.browse(cr, uid, location_ids)
        d = {
            'other_identifier': fake.random_element(patients).other_identifier,
            'location': fake.random_element(array=locations).code,
            'code': fake.random_int(min=10001, max=99999),
            'start_date': fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S"),
            'doctors': [
                   {
                    'code': str(fake.random_int(min=10001, max=99999)),
                    'type': fake.random_element(array=('r','c')),
                    'title': fake.random_element(array=('Mr','Mrs','Ms','Dr')),
                    'family_name': fake.last_name(),
                    'given_name': fake.first_name()
                    },
                   ]
             }
        d.update(data)
        return d


    def data_adt_patient_register(self, cr, uid, data={}):
        fake.seed(next_seed())
        gender = fake.random_element(array=('M','F'))
        d = {
                'family_name': fake.last_name(),
                'given_name': fake.first_name(),
                'other_identifier': str(fake.random_int(min=1000001, max=9999999)),
                'dob': fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S"),
                'gender': gender,
                'sex': gender,
                }
        d.update(data)
        return d
        
        
        
    def data_observation_ews(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
        d = {
            'respiration_rate': fake.random_int(min=5, max=34),
            'indirect_oxymetry_spo2': fake.random_int(min=85, max=100),
            'body_temperature': float(fake.random_int(min=350, max=391))/10.0 ,
            'blood_pressure_systolic': fake.random_int(min=65, max=206),
            'pulse_rate': fake.random_int(min=35, max=136),
            'avpu_text': fake.random_element(array=('A', 'V', 'P', 'U')),
            'oxygen_administration_flag': fake.random_element(array=(True, False)),
            'blood_pressure_diastolic': fake.random_int(min=35, max=176),
            'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        if d['oxygen_administration_flag']:
            d.update({
                'flow_rate': fake.random_int(min=40, max=60),
                'concentration': fake.random_int(min=50, max=100),
                'cpap_peep': fake.random_int(min=1, max=100),
                'niv_backup': fake.random_int(min=1, max=100),
                'niv_ipap': fake.random_int(min=1, max=100),
                'niv_epap': fake.random_int(min=1, max=100),
            })
        d.update(data)
        return d    
    
    
        
    def adt_patient_register(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())    
        d = self.data_adt_patient_register(cr, uid, data)
        reg_pool = self.pool['t4.clinical.adt.patient.register']
        activity_id = reg_pool.create_activity(cr, uid, {}, d)
        reg_pool.complete(cr, uid, activity_id)
        return activity_id   
        
#     def force_patient_placement(self, cr, uid, env_id, bed_location_id=None):
#         # Ragister
#         reg_activity_id = self.adt_patient_register(cr, uid, env_id)
#         reg_activity = self.pool['t4.activity'].browse(cr, uid, reg_activity_id)
#         # Admit
#         self.adt_patient_admit(cr, uid, env_id, {'other_identifier': reg_activity.data_ref.other_identifier})
#         # Placement
#         self.complete_patient_placement(cr, uid, env_id, [reg_activity.patient_id.id])
#         return reg_activity.patient_id.id

    def create_observation_stools(self, cr, uid, env_id, vals_activity={}, vals_data={}):
        vd = vals_data.copy()
        va = vals_activity.copy()
        vd = self.data_observation_stools(cr, uid, env_id, vd)
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, vd.get('patient_id'))
        spell_activity and va.update({'parent_id': spell_activity.id})
        stools_pool = self.pool['t4.clinical.patient.observation.stools']
        activity_id = stools_pool.create_activity(cr, uid, va, vd)
        return activity_id       
             
    def complete_observation_stools(self, cr, uid, env_id, data={}):
        activity_id = self._complete(cr, uid, env_id, 
                                     't4.clinical.patient.observation.stools', 
                                     'data_observation_stools', 
                                     data=data)
        return activity_id

    def data_observation_stools(self, cr, uid, env_id, data={}):
        fake.seed(next_seed()) 
        d = {
            'bowel_open': fake.random_int(min=0, max=1),
            'nausea': fake.random_int(min=0, max=1),
            'vomiting': fake.random_int(min=0, max=1),
            'quantity': fake.random_element(array=('large', 'medium', 'small')),
            'colour': fake.random_element(array=('brown', 'yellow', 'green', 'black', 'red', 'clay')),
            'bristol_type': str(fake.random_int(min=1, max=7)),
            'offensive': fake.random_int(min=0, max=1),
            'strain': fake.random_int(min=0, max=1),
            'laxatives': fake.random_int(min=0, max=1),
            'samples': fake.random_element(array=('none', 'micro', 'virol', 'm+v')),
            'rectal_exam': fake.random_int(min=0, max=1),
            'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d


    def create_observation_blood_sugar(self, cr, uid, env_id, vals_activity={}, vals_data={}):
        vd = vals_data.copy()
        va = vals_activity.copy()
        vd = self.data_observation_blood_sugar(cr, uid, env_id, vd)
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, vd.get('patient_id'))
        spell_activity and va.update({'parent_id': spell_activity.id})
        blood_sugar_pool = self.pool['t4.clinical.patient.observation.blood_sugar']
        activity_id = blood_sugar_pool.create_activity(cr, uid, va, vd)
        return activity_id       
             
    def complete_observation_blood_sugar(self, cr, uid, env_id, data={}):
        activity_id = self._complete(cr, uid, env_id, 
                                     't4.clinical.patient.observation.blood_sugar', 
                                     'data_observation_blood_sugar', 
                                     data=data)
        return activity_id

    def data_observation_blood_sugar(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
        d = data.copy()
        d = {
             'bllod_sugar': float(fake.random_int(min=1, max=100)),
             'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d

    def _complete(self, cr, uid, env_id, data_model, data_meth, data={}):
        d = data.copy()
        patient_ids = self.get_current_patient_ids(cr, uid, env_id)

        activities = self.get_activity_browse(cr, uid, env_id, 
                                              data_model, 
                                              [['patient_id','in',patient_ids],['activity_id.date_terminated','=',False]])
        activity = fake.random_element(activities)
        d = eval("self.%s(cr, uid, env_id, d)" % data_meth)
        self.submit(cr, uid, env_id, activity.id, d)
        self.complete(cr, uid, env_id, activity.id)
        return activity.id

    def create_observation_blood_product(self, cr, uid, env_id, vals_activity={}, vals_data={}):
        vd = vals_data.copy()
        va = vals_activity.copy()
        vd = self.data_observation_blood_product(cr, uid, env_id, vd)
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, vd.get('patient_id'))
        spell_activity and va.update({'parent_id': spell_activity.id})
        blood_product_pool = self.pool['t4.clinical.patient.observation.blood_product']
        activity_id = blood_product_pool.create_activity(cr, uid, va, vd)
        return activity_id       
             
    def complete_observation_blood_product(self, cr, uid, env_id, data={}):
        activity_id = self._complete(cr, uid, env_id, 
                                     't4.clinical.patient.observation.blood_product', 
                                     'data_observation_blood_product', 
                                     data=data)
        return activity_id

    def data_observation_blood_product(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
        d = {
             'product': fake.random_element(array=('rbc', 'ffp', 'platelets', 'has', 'dli', 'stem')),
             'vol': float(fake.random_int(min=1, max=10)),
             'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d
    
    def create_observation_weight(self, cr, uid, env_id, vals_activity={}, vals_data={}):
        vd = vals_data.copy()
        va = vals_activity.copy()
        vd = self.data_observation_weight(cr, uid, env_id, vd)
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, vd.get('patient_id'))
        spell_activity and va.update({'parent_id': spell_activity.id})
        weight_pool = self.pool['t4.clinical.patient.observation.weight']
        activity_id = weight_pool.create_activity(cr, uid, va, vd)
        return activity_id       
             
    def complete_observation_weight(self, cr, uid, env_id, data={}):
        activity_id = self._complete(cr, uid, env_id, 
                                     't4.clinical.patient.observation.weight', 
                                     'data_observation_weight', 
                                     data=data)
        return activity_id
    
    def data_observation_weight(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
        d = {
             'weight': float(fake.random_int(min=40, max=200)),
             'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d

    def create_observation_height(self, cr, uid, env_id, vals_activity={}, vals_data={}):
        vd = vals_data.copy()
        va = vals_activity.copy()
        vd = self.data_observation_height(cr, uid, env_id, vd)
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, vd.get('patient_id'))
        spell_activity and va.update({'parent_id': spell_activity.id})
        height_pool = self.pool['t4.clinical.patient.observation.height']
        activity_id = height_pool.create_activity(cr, uid, va, vd)
        return activity_id       
             
    def complete_observation_height(self, cr, uid, env_id, data={}):
        activity_id = self._complete(cr, uid, env_id, 
                                     't4.clinical.patient.observation.height', 
                                     'data_observation_height', 
                                     data=data)
        return activity_id

    def data_observation_height(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
        d = {
             'height': float(fake.random_int(min=160, max=200))/100.0,
             'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d

    def complete_placement(self, cr, uid, env_id, data={}):
        activity_id = self._complete(cr, uid, env_id, 
                                     't4.clinical.patient.placement', 
                                     'data_placement', 
                                     data)
        return activity_id
    
    def data_placement(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
  
        d = {
             'location_id': self.random_available_location_id(cr, uid, env_id)
        }
        d.update(data)
        return d
    
    def complete_observation_ews(self, cr, uid, env_id, data={}):
        activity_id = self._complete(cr, uid, env_id, 
                                     't4.clinical.patient.observation.ews', 
                                     'data_observation_ews', 
                                     data=data)
        return activity_id
                
    def data_observation_gcs(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())
        d = {
            'eyes': fake.random_element(array=('1', '2', '3', '4', 'C')),
            'verbal': fake.random_element(array=('1', '2', '3', '4', '5', 'T')),
            'motor': fake.random_element(array=('1', '2', '3', '4', '5', '6')),
            'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d                
                
    def create_observation_gcs(self, cr, uid, env_id, vals_activity={}, vals_data={}):
        vd = vals_data.copy()
        va = vals_activity.copy()
        vd = self.data_observation_gcs(cr, uid, env_id, vd)
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, vd.get('patient_id'))
        spell_activity and va.update({'parent_id': spell_activity.id})
        gcs_pool = self.pool['t4.clinical.patient.observation.gcs']
        activity_id = gcs_pool.create_activity(cr, uid, va, vd)
        return activity_id       
             
    def complete_observation_gcs(self, cr, uid, env_id, data={}):
        activity_id = self._complete(cr, uid, env_id, 
                                     't4.clinical.patient.observation.gcs', 
                                     'data_observation_gcs', 
                                     data=data)
        return activity_id

            
    def complete(self, cr, uid, env_id, activity_id):
        activity_pool = self.pool['t4.activity']
        res = activity_pool.complete(cr, uid, activity_id)
        return res
    
    def submit(self, cr, uid, env_id, activity_id, data={}):
        activity_pool = self.pool['t4.activity']
        res = activity_pool.submit(cr, uid, activity_id, data)
        return res    

    def get_activity_browse(self, cr, uid, env_id, data_model, domain=[]):        
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        activity_ids = self.get_activity_ids(cr, uid, env_id, data_model, domain)
        activity_browse = self.pool['t4.activity'].browse(cr, uid, activity_ids)     
        return activity_browse
    
    def get_activity_ids(self, cr, uid, env_id, data_model, domain=[]):  
        domain_copy = domain[:]
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        model_pool = self.pool[data_model]
        domain_copy.append(['activity_id.pos_id','=',env.pos_id.id])
        model_ids = model_pool.search(cr, uid, domain_copy)
        patient_ids = [m.activity_id.id for m in model_pool.browse(cr, uid, model_ids)]      
        return patient_ids

    def get_patient_ids(self, cr, uid, env_id, data_model='t4.clinical.adt.patient.register', domain=[]):
        domain_copy = domain[:]     
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        model_pool = self.pool[data_model]
        domain_copy.append(['activity_id.pos_id','=',env.pos_id.id])
        model_ids = model_pool.search(cr, uid, domain_copy)
        patient_ids = [m.patient_id.id for m in model_pool.browse(cr, uid, model_ids)]  
#         if not patient_ids:
#             import pdb; pdb.set_trace()     
        return patient_ids
    
    def get_current_patient_ids(self, cr, uid, env_id):
        patient_ids = self.get_patient_ids(cr, uid, env_id, 't4.clinical.spell', [['activity_id.date_terminated','=',False]])
        return patient_ids   
        
    def get_adt_user_ids(self, cr, uid, env_id):
        user_pool = self.pool['res.users']
        imd_pool = self.pool['ir.model.data']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        adt_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_adt")
        ids = user_pool.search(cr, uid, [['groups_id','in',adt_group.id],['pos_id','=',env.pos_id.id]])
        return ids
    
    def get_ward_location_ids(self, cr, uid, env_id):
        location_pool = self.pool['t4.clinical.location']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        ids = location_pool.search(cr, uid, [['usage','=','ward'],['pos_id','=',env.pos_id.id]])
        return ids        

    def get_bed_location_ids(self, cr, uid, env_id):
        location_pool = self.pool['t4.clinical.location']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        ids = location_pool.search(cr, uid, [['usage','=','bed'],['pos_id','=',env.pos_id.id]])
        return ids  
    
    def create(self, cr, uid, vals={},context=None):
        env_id = super(t4_clinical_demo_env, self).create(cr, uid, vals, context)
        data = self._defaults.copy()
        data.update(vals)
        _logger.info("Env created id=%s data: %s" % (env_id, data))
        return env_id
        
    def build(self, cr, uid, env_id):
        fake.seed(next_seed())
        location_pool = self.pool['t4.clinical.location']
        pos_pool = self.pool['t4.clinical.pos']
        env = self.browse(cr, uid, id)
        self.build_pos(cr, uid, env_id)
        self.build_adt_users(cr, uid, env_id)
        self.build_nurse_users(cr, uid, env_id)
        self.build_ward_manager_users(cr, uid, env_id)
        self.build_ward_locations(cr, uid, env_id)
        self.build_bed_locations(cr, uid, env_id)
        return True 

    def build_bed_locations(self, cr, uid, env_id):
        """
        By default random distribution among this pos's wards
        """
        fake.seed(next_seed())
        location_pool = self.pool['t4.clinical.location']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id   
        location_ids = self.get_ward_location_ids(cr, uid, env_id)
        if not location_ids:
            _logger.warn("No ward locations found. Beds will remain without parent location!")
        for i in range(env.bed_qty): 
            code = "BED_"+str(fake.random_int(min=1000, max=9999))
            data = {
                   'name': code,
                   'code': code,
                   'type': 'poc',
                   'usage': 'bed',
                   'parent_id': fake.random_element(location_ids)
            }     
            location_id = location_pool.create(cr, uid, data)  
            location_ids.append(location_id) 
            _logger.info("Bed location created id=%s data: %s" % (location_id, data))
        return location_ids
    
    def build_ward_locations(self, cr, uid, env_id):
        fake.seed(next_seed())
        location_pool = self.pool['t4.clinical.location']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id   
        location_ids = []
        for i in range(env.ward_qty): 
            code = "WARD_"+str(fake.random_int(min=100, max=999))
            data = {
                   'name': code,
                   'code': code,
                   'type': 'structural',
                   'usage': 'ward',
                   'parent_id': env.pos_id.location_id.id
            }     
            location_id = location_pool.create(cr, uid, data)  
            location_ids.append(location_id) 
            _logger.info("Ward location created id=%s data: %s" % (location_id, data))
        return location_ids
    
    def build_ward_manager_users(self, cr, uid, env_id):
        """
        By default responsible for all env's ward locations
        """
        fake.seed(next_seed())
        location_pool = self.pool['t4.clinical.location']
        imd_pool = self.pool['ir.model.data']
        user_pool = self.pool['res.users']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_ward_manager")
        location_ids = location_pool.search(cr, uid, [['usage','=','ward'],['pos_id','=',env.pos_id.id]])
        user_ids = []
        for i in range(env.ward_manager_user_qty):
            name = fake.first_name()          
            data = {
                'name': "Ward Manager %s" % name,
                'login': name.lower(),
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
        location_pool = self.pool['t4.clinical.location']
        imd_pool = self.pool['ir.model.data']
        user_pool = self.pool['res.users']
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_nurse")
        location_ids = location_pool.search(cr, uid, [['usage','=','ward'],['pos_id','=',env.pos_id.id]])
        user_ids = []
        for i in range(env.nurse_user_qty):
            name = fake.first_name()          
            data = {
                'name': "Nurse %s" % name,
                'login': name.lower(),
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
        group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_adt")
        user_ids = []
        for i in range(env.adt_user_qty):
            data = {
                'name': env.pos_id.name,
                'login': env.pos_id.location_id.code.lower(),
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
        location_pool = self.pool['t4.clinical.location']
        pos_pool = self.pool['t4.clinical.pos']
        env = self.browse(cr, uid, id)
        
        # POS Location
        code = "POS_"+str(fake.random_int(min=100, max=999))
        data = {
               'name': "POS Location (%s)" % code,
               'code': code,
               'type': 'structural',
               'usage': 'hospital',
               }
        pos_location_id = location_pool.create(cr, uid, data)
        _logger.info("POS location created id=%s data: %s" % (pos_location_id, data))
        # POS Admission Lot
        code = "ADMISSION_"+str(fake.random_int(min=100, max=999))
        data = {
               'name': code,
               'code': code,
               'type': 'structural',
               'usage': 'room',
               'parent_id': pos_location_id
               }        
        lot_admission_id = location_pool.create(cr, uid, data)
        _logger.info("Admission location created id=%s data: %s" % (lot_admission_id, data))
        # POS Discharge Lot
        code = "DISCHARGE_"+str(fake.random_int(min=100, max=999))
        data = {
               'name': code,
               'code': code,
               'type': 'structural',
               'usage': 'room',
               'parent_id': pos_location_id
               }        
        lot_discharge_id = location_pool.create(cr, uid, data)       
        _logger.info("Discharge location created id=%s data: %s" % (lot_discharge_id, data)) 
        # POS
        data = {
                'name': "HOSPITAL_"+str(fake.random_int(min=100, max=999)),
                'location_id': pos_location_id,
                'lot_admission_id': lot_admission_id,
                'lot_discharge_id': lot_discharge_id,
                }        
        pos_id = pos_pool.create(cr, uid, data)
        _logger.info("POS created id=%s data: %s" % (pos_id, data))
        
        self.write(cr, uid, env_id, {'pos_id': pos_id})
        _logger.info("Env updated pos_id=%s" % (pos_id))
        return pos_id 
 
        
class t4_clinical_demo_patient(orm.Model):
    _name = 't4.clinical.demo.patient'
    
    def _get_name(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['family_name', 'given_name', 'middle_name'], context=context):
            #TODO This needs to be manipulable depending on locale
            result[r['id']] = self._get_fullname(r)
        return result
        
    _columns = {
        'dob': fields.datetime('Date Of Birth'),
        'sex': fields.char('Sex', size=1),
        'gender': fields.char('Gender', size=1),
        'ethnicity': fields.char('Ethnicity', size=20),
        'patient_identifier': fields.char('Patient Identifier', size=100, select=True, help="NHS Number"),
        'other_identifier': fields.char('Other Identifier', size=100, required=True, select=True,
                                        help="Hospital Number"),

        'given_name': fields.char('Given Name', size=200),
        'middle_names': fields.char('Middle Name(s)', size=200),
        'family_name': fields.char('Family Name', size=200, select=True),
        'full_name': fields.function(_get_name, type='text', string="Full Name"),    
    }
    _defaults = {
        'family_name': fake.last_name(),
        'given_name': fake.first_name(),
        'gender': fake.random_element(array=('M','F')),
        'other_identifier': str(fake.random_int(min=1000001, max=9999999)),
        'dob': fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S"),
    }
    

#     def create(self, cr, uid, vals={},context=None):
#         env_id = super(t4_clinical_demo_env, self).create(cr, uid, vals, context)
#         data = self._defaults.copy()
#         data.update(vals)
#         _logger.info("Env created id=%s data: %s" % (env_id, data))
#         return env_id
    
    
    def adt_register(self, cr, uid):
        user_pool = self.pool['res.users']
        user = user_pool.browse(cr, uid, uid)
        assert user.pos_id, "pos_id is not set on user id=%s" % uid
        reg_pool = self.pool['t4.clinical.adt.patient.register']
        activity_pool = self.activity['t4.activity']
        patient = patient_pool.browse(cr, uid, patient_id)
        data = {
            'family_name': patient.family_name,
            'given_name': patient.given_name,
            'gender': patient.gender,
            'other_identifier': patient.other_identifier,
            'dob': patient.dob
        }

#     
#     def is_adt_registered(self, cr, uid):
#         pass
#     
#     def adt_admit(self, cr, uid):
#         pass
#     
#     def placement(self, cr, uid):
#         pass
#     
#     def get_activity_ids(self, cr, uid, data_model, states=None):
#         pass

class t4_clinical_demo(orm.AbstractModel):
    _name = 't4.clinical.demo'
    _pos = {
        'data': {},
        'timeline': {},
        'id': None,
        'activity_ids': [],
        'beds': [
                     {'data': {},'timeline': {}, 'id':None, 'ward_idx': 0},
                     {'data': {},'timeline': {}, 'id':None, 'ward_idx': 1},
                     {'data': {},'timeline': {}, 'id':None, 'ward_idx': 2}
                 ],
        'wards': [
                     {'data': {},'timeline': {}, 'id':None},
                     {'data': {},'timeline': {}, 'id':None},
                     {'data': {},'timeline': {}, 'id':None}
                 ],
        'adt_users':[
                       {'data': {},'timeline': {}, 'id':None},
                     ],
        'nurse_users':[
                       {'data': {},'timeline': {}, 'id':None, 'ward_idxs':[0,1]},
                       {'data': {},'timeline': {}, 'id':None, 'ward_idxs':[1,2]},
                     ],
        'ward_manager_users':[
                       {'data': {},'timeline': {}, 'id':None, 'ward_idxs':[0,1]},
                       {'data': {},'timeline': {}, 'id':None, 'ward_idxs':[1,2]},
                     ],
        'devices':[
                  {'data': {},'timeline': {}, 'id':None},
                  {'data': {},'timeline': {}, 'id':None},
                  ]

    }
    
    def config_pos(self, cr, uid,
                   beds=None,
                   wards=None,
                   adt_users=None,
                   nurse_users=None,
                   ward_manager_user=None,
                   devices=None):
        self._pos['id'] = None
        self._pos['activity_ids'] = []
        keys = ['beds', 'wards', 'adt_users', 'nurse_users', 'ward_manager_users', 'devices']
        for key in keys:
            for e in self._pos[key]:
                e.update({'id':None})
        
                
        
        
    
    def create_pos_env(self, cr, uid):
        """
        creates 1 pos environment
        """
        _logger.info("Executing create_environment()")
        pos_pool = self.pool['t4.clinical.pos']
        # clean self._pos
        self.config_pos(cr, uid)
        
        # Create POS
        pos_id = self.create_pos(cr, uid, self._pos['data'])
        self._pos.update({'id': pos_id})
        pos = pos_pool.browse(cr, uid, pos_id)

        # Create wards
        for ward in self._pos['wards']:
            ward['data'].update({'parent_id': pos.location_id.id})
            ward.update({'id': self.create_ward_location(cr, uid, ward['data'])})

        # Create beds
        for bed in self._pos['beds']:
            parent_id = isinstance(bed['ward_idx'], int) and self._pos['wards'][bed['ward_idx']]['id'] or None
            bed['data'].update({'parent_id': parent_id})
            bed.update({'id': self.create_bed_location(cr, uid, bed['data'])})

        # Create adt users
        for adt_user in self._pos['adt_users']:
            adt_user['data'].update({'pos_id': self._pos['id']})
            adt_user.update({'id': self.create_adt_user(cr, uid, adt_user['data'])})

        # Create nurse users
        for nurse_user in self._pos['nurse_users']:
            location_ids = [self._pos['wards'][idx]['id'] for idx in nurse_user['ward_idxs']]
            nurse_user['data'].update({'location_ids': location_ids})
            nurse_user.update({'id': self.create_nurse_user(cr, uid, nurse_user['data'])})

        # Create ward_manager users
        for ward_manager_user in self._pos['ward_manager_users']:
            location_ids = [self._pos['wards'][idx]['id'] for idx in ward_manager_user['ward_idxs']]
            ward_manager_user['data'].update({'location_ids': location_ids})
            ward_manager_user.update({'id': self.create_ward_manager_user(cr, uid, ward_manager_user['data'])})

        # Create devices
        for device in self._pos['devices']:
            device.update({'id': self.create_device(cr, uid, device['data'])})

        return self._pos


    def create_pos_location(self, cr, uid, data={}):
        d = data.copy()
        d = self.data_pos_location(cr, uid, d)
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.create(cr, uid, d)
        _logger.info("POS location created id=%s\n data: %s" % (location_id, d))
        return location_id

    def data_pos_location(self, cr, uid, data={}):
        fake.seed(next_seed())
        code = "POS_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': 'name' in data.keys() and data['name'] or "POS Location (%s)" % code,
               'code': 'code' in data.keys() and data['code'] or code,
               'type': 'type' in data.keys() and data['type'] or 'structural',
               'usage': 'usage' in data.keys() and data['usage'] or 'hospital',
               'parent_id': data.get('parent_id')
               }
        return res

    def create_bed_location(self, cr, uid, data={}):
        d = data.copy()
        d = self.data_bed_location(cr, uid, d)
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.create(cr, uid, d)
        _logger.info("Bed location created id=%s\n data: %s" % (location_id, d))
        return location_id

    def data_bed_location(self, cr, uid, data={}):
        fake.seed(next_seed())
        code = "BED_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': 'name' in data.keys() and data['name'] or code,
               'code': 'code' in data.keys() and data['code'] or code,
               'type': 'type' in data.keys() and data['type'] or 'poc',
               'usage': 'usage' in data.keys() and data['usage'] or 'bed',
               'parent_id': data.get('parent_id')
               }
        return res

    def create_ward_location(self, cr, uid, data={}):
        d = data.copy()
        d = self.data_ward_location(cr, uid, d)
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.create(cr, uid, d)
        _logger.info("Ward location created id=%s\n data: %s" % (location_id, d))
        return location_id

    def data_ward_location(self, cr, uid, data={}):
        fake.seed(next_seed())
        code = "WARD_"+str(fake.random_int(min=100, max=999))
        pos = self.pool['t4.clinical.pos'].browse(cr, uid, self._pos['id'])
        #import pdb; pdb.set_trace()
        res = {
               'name': 'name' in data.keys() and data['name'] or code,
               'code': 'code' in data.keys() and data['code'] or code,
               'type': 'type' in data.keys() and data['type'] or 'structural',
               'usage': 'usage' in data.keys() and data['usage'] or 'ward',
               'parent_id': 'parent_id' in data and data['parent_id'] or pos.location_id.id
               }

        return res

    def create_admission_location(self, cr, uid, data={}):
        d = data.copy()
        d = self.data_admission_location(cr, uid, d)
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.create(cr, uid, d)
        _logger.info("Admission location created id=%s\n data: %s" % (location_id, d))
        return location_id

    def data_admission_location(self, cr, uid, data={}):
        fake.seed(next_seed())
        code = "ADMISSION_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': 'name' in data.keys() and data['name'] or code,
               'code': 'code' in data.keys() and data['code'] or code,
               'type': 'type' in data.keys() and data['type'] or 'structural',
               'usage': 'usage' in data.keys() and data['usage'] or 'room',
               'parent_id': data.get('parent_id')
               }
        return res

    def create_discharge_location(self, cr, uid, data={}):
        d = data.copy()
        d = self.data_discharge_location(cr, uid, d)
        location_pool = self.pool['t4.clinical.location']
        #import pdb; pdb.set_trace()
        location_id = location_pool.create(cr, uid, d)
        _logger.info("Discharge location created id=%s\n data: %s" % (location_id, d))
        return location_id

    def data_discharge_location(self, cr, uid, data={}):
        #import pdb; pdb.set_trace()
        fake.seed(next_seed())
        code = "DISCHARGE_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': 'name' in data.keys() and data['name'] or code,
               'code': 'code' in data.keys() and data['code'] or code,
               'type': 'type' in data.keys() and data['type'] or 'structural',
               'usage': 'usage' in data.keys() and data['usage'] or 'room',
               'parent_id': data.get('parent_id')
               }
        return res

    def create_adt_user(self, cr, uid, data={}):
        fake.seed(next_seed())
        user_pool = self.pool['res.users']
        d = data.copy()
        d = self.data_adt_user(cr, uid, d)
        user_id = user_pool.create(cr, uid, d)
        _logger.info("ADT user created id=%s\n data: %s" % (user_id, d))
        return user_id

    def data_adt_user(self, cr, uid, data={}):
        fake.seed(next_seed())
        d = data.copy()
        imd_pool = self.pool['ir.model.data']
        pos_pool = self.pool['t4.clinical.pos']
        adt_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_adt")
        pos_id = 'pos_id' in data and data['pos_id'] or self.create_pos(cr, uid)
        pos = pos_pool.browse(cr, uid, pos_id)
        pos = pos_pool.browse(cr, uid, pos_id)
        res = {
            'name': data.get('name') or "ADT user for %s" % pos.name,
            'login': data.get('login') or "adt_%s" % pos.location_id.code.lower(),
            'password': data.get('password') or "adt_%s" % pos.location_id.code.lower(),
            'groups_id': data.get('groups_id') or [(4, adt_group.id)],
            'pos_id': pos_id
        }
        return res

    def create_nurse_user(self, cr, uid, data={}):
        user_pool = self.pool['res.users']
        d = data.copy()
        d = self.data_nurse_user(cr, uid, d)
        user_id = user_pool.create(cr, uid, d)
        _logger.info("Nurse user created id=%s\n data: %s" % (user_id, d))
        return user_id

    def data_nurse_user(self, cr, uid, data={}):
        imd_pool = self.pool['ir.model.data']
        fake.seed(next_seed())
        nurse_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_nurse")
        name = fake.first_name()
        location_ids = 'location_ids' in data and data['location_ids'] or []
        location_ids = hasattr(location_ids, '__iter__') and location_ids or []
        res = {
            'name': data.get('name') or "Nurse %s" % name,
            'login': data.get('login') or name.lower(),
            'password': data.get('password') or name.lower(),
            'groups_id': data.get('groups_id') and [(4, group_id) for group_id in data['groups_id']] or [(4, nurse_group.id)],
            'location_ids': [(4,location_id) for location_id in location_ids]
        }
        return res

    def create_ward_manager_user(self, cr, uid, data={}):
        user_pool = self.pool['res.users']
        d = data.copy()
        d = self.data_ward_manager_user(cr, uid, d)
        user_id = user_pool.create(cr, uid, d)
        _logger.info("ward_manager user created id=%s\n data: %s" % (user_id, d))
        return user_id

    def data_ward_manager_user(self, cr, uid, data={}):
        imd_pool = self.pool['ir.model.data']
        fake.seed(next_seed())
        ward_manager_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_ward_manager")
        name = fake.first_name()
        location_ids = 'location_ids' in data and data['location_ids'] or []
        location_ids = hasattr(location_ids, '__iter__') and location_ids or []
        res = {
            'name': data.get('name') or "ward_manager %s" % name,
            'login': data.get('login') or name.lower(),
            'password': data.get('password') or name.lower(),
            'groups_id': data.get('groups_id') and [(4, group_id) for group_id in data['groups_id']] or [(4, ward_manager_group.id)],
            'location_ids': [(4,location_id) for location_id in location_ids]
        }
        return res


    def create_pos(self, cr, uid, data={}):
        fake.seed(next_seed())
        pos_pool = self.pool['t4.clinical.pos']
        d = data.copy()
        d = self.data_pos(cr, uid, d)
        pos_id = pos_pool.create(cr, uid, d)
        _logger.info("POS created id=%s\n data: %s" % (pos_id, data))
        return pos_id

    def data_pos(self, cr, uid, data={}):
        fake.seed(next_seed())
        location_id = 'location_id' in data and data['location_id'] or self.create_pos_location(cr, uid)
        res = {
                'name': 'name' in data and data['name'] or "HOSPITAL_"+str(fake.random_int(min=100, max=999)),
                'location_id': location_id,
                'lot_admission_id': 'lot_admission_id' in data
                                    and data['lot_admission_id']
                                    or self.create_admission_location(cr, uid, {'parent_id':location_id}),
                'lot_discharge_id': 'lot_discharge_id' in data
                                    and data['lot_discharge_id']
                                    or self.create_admission_location(cr, uid, {'parent_id':location_id}),
                }
        return res


    def create_device_type(self, cr, uid, data={}):
        device_type_pool = self.pool['t4.clinical.device.type']
        d = data.copy()
        d = self.data_device_type(cr, uid, d)
        device_type_id = device_type_pool.create(cr, uid, d)
        _logger.info("Device type created id=%s" % (device_type_id))
        return device_type_id

    def data_device_type(self, cr, uid, data={}):
        fake.seed(next_seed())
        flow_directions = [k for k, v in self.pool['t4.clinical.device.type']._columns['flow_direction'].selection]
        max = len(flow_directions)-1
        res = {
                'name': 'name' in data and data['name'] or "DEVICE_TYPE_"+str(fake.random_int(min=100, max=999)),
                'flow_direction': 'flow_direction' in data
                                    and data['flow_direction'] or fake.random_element(array=flow_directions),
                }
        return res

    def create_device(self, cr, uid, data={}):
        device_pool = self.pool['t4.clinical.device']
        d = data.copy()
        d = self.data_device(cr, uid, d)
        device_id = device_pool.create(cr, uid, d)
        _logger.info("Device created id=%s" % (device_id))
        return device_id


    def data_device(self, cr, uid, data={}):
        fake.seed(next_seed())
        type_id = 'type_id' in data and data['type_id'] or self.create_device_type(cr, uid)
        res = {
               'type_id': type_id
               }
        return res    