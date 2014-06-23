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
    _name = 't4.clinical.demo.env'
    
    _columns = {
        'bed_qty': fields.integer('Bed Qty'),
        'ward_qty': fields.integer('Ward Qty'),
        'adt_user_qty': fields.integer('ADT User Qty'),
        'nurse_user_qty': fields.integer('Nurse User Qty'), 
        'ward_manager_user_qty': fields.integer('Ward Manager User Qty'),
        'patient_qty': fields.integer('Patients Qty'),   
        
        'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
        
    }
    _defaults = {
         'bed_qty': 3,
         'ward_qty': 2,
         'adt_user_qty': 1,
         'nurse_user_qty': 2,
         'ward_manager_user_qty': 2,
         'patient_qty': 2,
    }
    
    
    def fake_data(self, cr, uid, env_id, model, data={}):
        """
        This method returns fake data for model
        Extend this method to add fake data for other models 
        """
        method_map = {
            # Base
            
            # Observations
            't4.clinical.patient.observation.ews': 'data_observation_ews',
            't4.clinical.patient.observation.gcs': 'data_observation_gcs',
            't4.clinical.patient.observation.height': 'data_observation_height',
            't4.clinical.patient.observation.weight': 'data_observation_weight',
            't4.clinical.patient.observation.blood_sugar': 'data_observation_blood_sugar',
            't4.clinical.patient.observation.blood_product': 'data_observation_blood_product',
            't4.clinical.patient.observation.stools': 'data_observation_stools',
            
            # ADT
            't4.clinical.adt.patient.register': 'data_adt_patient_register',
            't4.clinical.adt.patient.admit': 'data_adt_patient_admit',
            't4.clinical.adt.patient.cancel_admit': 'data_adt_patient_cancel_admit',
            
            # Operations
            't4.clinical.patient.placement': 'data_placement',                   
        }
        #import pdb; pdb.set_trace()
        res = eval("self.%s(cr, uid, env_id, model, data)" % method_map[model])  
        
        return res
    
    def create_activity(self, cr, uid, env_id, data_model, activity_vals={}, data_vals={}, no_fake=False):
        activity_pool = self.pool['t4.activity']
        data_pool = self.pool[data_model]
        if not no_fake:
            dvals = self.fake_data(cr, uid, env_id, data_model, data_vals)
        else:
            dvals = data_vals.copy()        
        activity_id = data_pool.create_activity(cr, uid, activity_vals, dvals)        
        return activity_pool.browse(cr, uid, activity_id)
    
    def create_complete(self, cr, uid, env_id, data_model, activity_vals={}, data_vals={}, no_fake=False):
        if not no_fake:
            dvals = self.fake_data(cr, uid, env_id, data_model, data_vals)
        else:
            dvals = data_vals.copy()
        data_pool = self.pool[data_model]
        activity_pool = self.pool['t4.activity']
        activity_id = data_pool.create_activity(cr, uid, activity_vals, dvals)
        activity_pool.complete(cr, uid, activity_id)       
        return activity_pool.browse(cr, uid, activity_id)

    def complete(self, cr, uid, env_id, activity_id):  
        assert activity_id
        activity_pool = self.pool['t4.activity']
        activity_pool.complete(cr, uid, activity_id)
        return activity_pool.browse(cr, uid, activity_id)
    
    def submit_complete(self, cr, uid, env_id, activity_id, data_vals={}, no_fake=False):  
        assert activity_id
        activity_pool = self.pool['t4.activity']
        vals = self.pool['t4.clinical.api'].get_activity_data(cr, uid, activity_id)
        vals = {k: v for k, v in vals.items() if v}
        vals.update(data_vals)
        if not no_fake:
            activity = activity_pool.browse(cr, uid, activity_id)
            vals = self.fake_data(cr, uid, env_id, activity.data_model, vals)
        #import pdb; pdb.set_trace()
        activity_pool.submit(cr, uid, activity_id, vals)
        activity_pool.complete(cr, uid, activity_id)
        return activity_pool.browse(cr, uid, activity_id)
    

    def random_available_location(self, cr, uid, env_id, parent_id=None, usages=['bed'], available_range=[1,1]):
        fake.seed(next_seed())
        bed_location_ids = self.get_bed_location_ids(cr, uid, env_id)
        print "demo: map args: ids: %s, available_range: %s, usages: %s" % (bed_location_ids,available_range,usages)
        location_ids = self.pool['t4.clinical.api'].location_availability_map(cr, uid, 
                                                                                  ids=bed_location_ids, 
                                                                                  available_range=available_range,
                                                                                  usages=usages)
        
        location_pool = self.pool['t4.clinical.location']
        location_ids = location_pool.search(cr, uid, [['usage','=','bed'],['is_available','=',True]])
        if parent_id:
            domain = [['id', 'child_of', parent_id]]
            location_ids = location_pool.search(cr, uid, domain)
        if not location_ids:
            _logger.warn("No available locations left!")
        location_id = location_ids and fake.random_element(location_ids) or False
        return location_pool.browse(cr, uid, location_id)

    def random_observation_available_location(self, cr, uid, env_id, data_model):
        fake.seed(next_seed())
        patient_pool = self.pool['t4.clinical.patient']
        all_patient_ids = self.get_current_patient_ids(cr, SUPERUSER_ID, env_id)
        used_patient_ids = self.get_patient_ids(cr, SUPERUSER_ID, env_id,  data_model, domain=[['activity_id.date_terminated','=',False]])
        patient_ids = list(set(all_patient_ids)-set(used_patient_ids))       
        patient_id = patient_ids and fake.random_element(patient_ids) or False
        return patient_pool.browse(cr, uid, patient_id)

    def data_adt_patient_discharge(self, cr, uid, env_id, activity_id=None, data={}):
        fake.seed(next_seed())
        env = self.browse(cr, uid, env_id)
        patient_ids = self.get_patient_ids(cr, uid, env_id, 't4.clinical.spell', [['activity_id.date_terminated','=',False]])
        patient = self.pool['t4.clinical.patient'].browse(cr, uid, fake.random_element(patient_ids))
        d = {
            'other_identifier': patient.other_identifier,
            'pos_id': env.pos_id.id
        }
        d.update(data)
        return d

    def data_adt_patient_cancel_admit(self, cr, uid, env_id, activity_id=None, data={}):
        fake.seed(next_seed())
        env = self.browse(cr, uid, env_id)
        patient_ids = self.get_patient_ids(cr, uid, env_id, 't4.clinical.spell', [['activity_id.date_terminated','=',False]])
        patient = self.pool['t4.clinical.patient'].browse(cr, uid, fake.random_element(patient_ids))
        d = {
            'other_identifier': patient.other_identifier,
            'pos_id': env.pos_id.id
        }
        d.update(data)
        return d

    def data_adt_patient_admit(self, cr, uid, env_id, activity_id=None, data={}):
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


    def data_adt_patient_register(self, cr, uid, env_id, activity_id=None, data={}):
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
        
        

    def data_observation_ews(self, cr, uid, env_id, activity_id=None, data={}):
        
        #import pdb; pdb.set_trace()
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
            'patient_id': self.random_observation_available_location(cr, uid, env_id, 't4.clinical.patient.observation.ews').id
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
        if not d['patient_id']:
            _logger.warn("No patients available for ews!")
        d.update(data)
        return d    
    
    
        
    def adt_patient_register(self, cr, uid, env_id, data={}):
        fake.seed(next_seed())    
        d = self.data_adt_patient_register(cr, uid, env_id, data)
        reg_pool = self.pool['t4.clinical.adt.patient.register']
        activity_id = reg_pool.create_activity(cr, uid, {}, d)
        reg_pool.complete(cr, uid, activity_id)
        activity_pool = self.pool['t4.activity']        
        return activity_pool.browse(cr, uid, activity_id) 
        
    def data_observation_stools(self, cr, uid, env_id, activity_id=None, data={}):
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

    def data_observation_blood_sugar(self, cr, uid, env_id, activity_id=None, data={}):
        fake.seed(next_seed())
        d = data.copy()
        d = {
             'blood_sugar': float(fake.random_int(min=1, max=100)),
             'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d

    def _create(self, cr, uid, env_id, data_model, data_meth, vals_activity={}, vals_data={}):
        vd = vals_data.copy()
        va = vals_activity.copy()
        vd = eval("self.%s(cr, uid, env_id, vd)" % data_meth)
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, vd.get('patient_id'))
        spell_activity and va.update({'parent_id': spell_activity.id})
        model_pool = self.pool[data_model]
        activity_id = model_pool.create_activity(cr, uid, va, vd)
        activity_pool = self.pool['t4.activity']        
        return activity_pool.browse(cr, uid, activity_id) 

    def _complete(self, cr, uid, env_id, data_model, data_meth, activity_id=None, data={}):
        d = data.copy()
        activity_pool = self.pool['t4.activity']
        if activity_id:
            activity = activity_pool.browse(cr, uid, activity_id)
        else:
            patient_ids = self.get_current_patient_ids(cr, uid, env_id)
            activities = self.get_activities(cr, uid, env_id, [['data_model','=',data_model],
                                                           ['patient_id','in',patient_ids],
                                                           ['date_terminated','=',False]])
            activity = fake.random_element(activities)
        if not activity:
            return False
        
        d = eval("self.%s(cr, uid, env_id, activity.id, d)" % data_meth)
        # get existing data
        activity_data = self.pool[activity.data_model].read(cr, uid, activity.data_ref.id)
        activity_data = activity_pool.read(cr, uid, activity.id, [])
        # normalize many2one fields
        #import pdb; pdb.set_trace()
        for k, v in activity_data.items():
            if isinstance(v, (list, tuple)) and len(v)>0:
                activity_data[k] = v[0]
        # update with existing data keeping priority to passed data 'data'
        print "activity-data: %s" % activity_data
        print "data: %s" % d 
        for k, v in d.items():
            d[k] = k not in data and activity_data[k] or d[k]
        #import pdb; pdb.set_trace() 
        
        if d.get('location_id'):
            print "location.is_available: %s" % self.pool['t4.clinical.location'].read(cr, uid, d['location_id'], ['is_available'])
            print "location.is_availablity_map: %s" % self.pool['t4.clinical.api'].location_availability_map(cr, uid, [d['location_id']]) 
#         try:
        activity_pool.submit(cr, uid, activity.id, d)
#         except:
#             #import pdb; pdb.set_trace()
        activity_pool.complete(cr, uid, activity.id)
        return activity


    def data_observation_blood_product(self, cr, uid, env_id, activity_id=None, data={}):
        fake.seed(next_seed())
        d = {
             'product': fake.random_element(array=('rbc', 'ffp', 'platelets', 'has', 'dli', 'stem')),
             'vol': float(fake.random_int(min=1, max=10)),
             'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d

    
    def data_observation_weight(self, cr, uid, env_id, activity_id=None, data={}):
        fake.seed(next_seed())
        d = {
             'weight': float(fake.random_int(min=40, max=200)),
             'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d


    def data_observation_height(self, cr, uid, env_id, activity_id=None, data={}):
        fake.seed(next_seed())
        d = {
             'height': float(fake.random_int(min=160, max=200))/100.0,
             'patient_id': fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID, env_id))
        }
        d.update(data)
        return d

    
    def data_placement(self, cr, uid, env_id, activity_id=None, data={}):
        fake.seed(next_seed())
        #import pdb; pdb.set_trace()
        d = {
             'location_id': self.random_available_location(cr, uid, env_id).id
        }
        if not d['location_id']:
            _logger.warn("No available locations left!")
        d.update(data)
        return d

                
    def data_observation_gcs(self, cr, uid, env_id, activity_id=None, data={}):     
        d = {
            'eyes': fake.random_element(array=('1', '2', '3', '4', 'C')),
            'verbal': fake.random_element(array=('1', '2', '3', '4', '5', 'T')),
            'motor': fake.random_element(array=('1', '2', '3', '4', '5', '6')),
            'patient_id': self.random_observation_available_location(cr, uid, env_id, 't4.clinical.patient.observation.gcs').id
        }
        if not d['patient_id']:
            _logger.warn("No patients available for gcs!")        
        d.update(data)
        return d                
    
    def get_activities(self, cr, uid, env_id, domain=[]):  
        domain_copy = domain[:]
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        activity_pool = self.pool['t4.activity']
        domain_copy.append(['pos_id','=',env.pos_id.id])
        activity_ids = activity_pool.search(cr, uid, domain_copy)   
        return activity_pool.browse(cr, uid, activity_ids)

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
        env = self.browse(cr, uid, env_id)
        self.build_pos(cr, uid, env_id)
        self.build_adt_users(cr, uid, env_id)
        self.build_nurse_users(cr, uid, env_id)
        self.build_ward_manager_users(cr, uid, env_id)
        self.build_ward_locations(cr, uid, env_id)
        self.build_bed_locations(cr, uid, env_id)
        self.build_patients(cr, uid, env_id)
        return self.browse(cr, uid, env_id)
 
    
    def build_patients(self, cr, uid, env_id):
        fake.seed(next_seed())
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        register_pool = self.pool['t4.clinical.adt.patient.register']
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
#         import pdb; pdb.set_trace()
        adt_user_id = self.get_adt_user_ids(cr, uid, env_id)[0]
        for i in range(env.patient_qty):
            register_activity = self.create_complete(cr, adt_user_id, env_id, 't4.clinical.adt.patient.register')
            admit_data = {'other_identifier': register_activity.data_ref.other_identifier}
            admit_activity = self.create_complete(cr, adt_user_id, env_id, 't4.clinical.adt.patient.admit', data_vals=admit_data)
            placement_activity = self.get_activities(cr, uid, env_id, domain=[['data_model','=','t4.clinical.patient.placement'],['date_terminated','=',False]])[0]
            self.submit_complete(cr, adt_user_id, env_id, placement_activity.id) 
            

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