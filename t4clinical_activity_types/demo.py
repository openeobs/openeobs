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
from openerp.addons.t4activity.activity import except_if
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed




class t4_clinical_demo_env(orm.Model):
    _inherit = 't4.clinical.demo.env'
    
    _columns = {
        'patient_qty': fields.integer('Patients Qty'),   
        
    }
    _defaults = {
         'patient_qty': 2,
    }
    
    def fake_data(self, cr, uid, env_id, model, data={}):
        """
        This method returns fake data for model
        Extend this method to add fake data for other models 
        """
        data_copy = data.copy()
        method_map = {

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
        res = None
        # FIXME: this need notification if data_method not defined for model
        if method_map.get(model) and hasattr(t4_clinical_demo_env, method_map[model]):
            res = eval("self.{method}(cr, uid, env_id, data=data_copy)".format(method=method_map[model]))
        else:
            res = super(t4_clinical_demo_env, self).fake_data(cr, uid, env_id, model, data_copy)
        except_if(not res, msg="Data method is not defined for model '%s'" % model)
        return res
    

    def random_available_location(self, cr, uid, env_id, parent_id=None, usages=['bed'], available_range=[1,1]):
        fake.seed(next_seed())
        env = self.browse(cr, uid, env_id)
        location_ids = self.pool['t4.clinical.api'].location_map(cr, uid,  
                                                                  available_range=available_range,
                                                                  usages=['bed'],
                                                                  pos_ids=[env.pos_id.id]).keys()
        location_pool = self.pool['t4.clinical.location']
#         if parent_id:
#             domain = [['id', 'child_of', parent_id]]
#             location_ids = location_pool.search(cr, uid, domain)
        if not location_ids:
            _logger.warn("No available locations left!")
        location_id = location_ids and fake.random_element(location_ids) or False
        return location_pool.browse(cr, uid, location_id)

    def get_activity_free_patients(self, cr, uid, env_id, data_models, states):
        # random_observation_available_location
        fake.seed(next_seed())
        env = self.browse(cr, uid, env_id)
        patient_pool = self.pool['t4.clinical.patient']
        api_pool = self.pool['t4.clinical.api']
        all_patient_ids = [a.patient_id.id for a in api_pool.get_activities(cr, SUPERUSER_ID, pos_ids=[env.pos_id.id], data_models=['t4.clinical.spell'], states=['started'])]
        used_patient_ids = [a.patient_id.id for a in api_pool.get_activities(cr, SUPERUSER_ID, data_models=data_models, states=states)]
        patient_ids = list(set(all_patient_ids)-set(used_patient_ids))       
        #patient_id = patient_ids and fake.random_element(patient_ids) or False
        return patient_pool.browse(cr, SUPERUSER_ID, patient_ids)

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
        env = self.browse(cr, SUPERUSER_ID, env_id)
        patient_pool = self.pool['t4.clinical.patient']
        location_pool = self.pool['t4.clinical.location']
        
        reg_patient_ids = self.get_patient_ids(cr, uid, env_id)
        admit_patient_ids = self.get_patient_ids(cr, uid, env_id, 't4.clinical.adt.patient.admit')
        patient_ids = list(set(reg_patient_ids) - set(admit_patient_ids))
#         if not patient_ids:
#             import pdb; pdb.set_trace()
        assert patient_ids, "No patients left to admit!"
        patients = patient_pool.browse(cr, uid, patient_ids)
        locations = self.pool['t4.clinical.api'].get_locations(cr, uid, pos_ids=[env.pos_id.id], usages=['ward'], available_range=[0,999])
        assert locations, "No ward locations to set as admit location"
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
        patients = self.get_activity_free_patients(cr, uid, env_id,['t4.clinical.patient.observation.ews'],['new','scheduled','started'])
        d = {
            'respiration_rate': fake.random_int(min=5, max=34),
            'indirect_oxymetry_spo2': fake.random_int(min=85, max=100),
            'body_temperature': float(fake.random_int(min=350, max=391))/10.0 ,
            'blood_pressure_systolic': fake.random_int(min=65, max=206),
            'pulse_rate': fake.random_int(min=35, max=136),
            'avpu_text': fake.random_element(array=('A', 'V', 'P', 'U')),
            'oxygen_administration_flag': fake.random_element(array=(True, False)),
            'blood_pressure_diastolic': fake.random_int(min=35, max=176),
            'patient_id': patients and fake.random_element(patients).id or False
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
            #import pdb; pdb.set_trace()
            #self.random_available_location(cr, uid, env_id)
        d.update(data)
        return d

                
    def data_observation_gcs(self, cr, uid, env_id, activity_id=None, data={}):    
        fake.seed(next_seed())
        patients = self.get_activity_free_patients(cr, uid, env_id,['t4.clinical.patient.observation.gcs'],['new','scheduled','started']) 
        d = {
            'eyes': fake.random_element(array=('1', '2', '3', '4', 'C')),
            'verbal': fake.random_element(array=('1', '2', '3', '4', '5', 'T')),
            'motor': fake.random_element(array=('1', '2', '3', '4', '5', '6')),
            'patient_id': patients and fake.random_element(patients).id or False
        }
        if not d['patient_id']:
            _logger.warn("No patients available for gcs!")        
        d.update(data)
        return d                

    def get_patient_ids(self, cr, uid, env_id, data_model='t4.clinical.adt.patient.register', domain=[]):
        domain_copy = domain[:]     
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        model_pool = self.pool[data_model]
        domain_copy.append(['activity_id.pos_id','=',env.pos_id.id])
        model_ids = model_pool.search(cr, uid, domain_copy)
        patient_ids = [m.patient_id.id for m in model_pool.browse(cr, uid, model_ids)]       
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

    
    def create(self, cr, uid, vals={},context=None):
        env_id = super(t4_clinical_demo_env, self).create(cr, uid, vals, context)
        #env_id = isinstance(env_id, (int, long)) and env_id or env_id.id
        data = self.read(cr, uid, env_id, [])
        _logger.info("Env created id=%s data: %s" % (env_id, data))
        #import pdb; pdb.set_trace()
        return env_id
        
    def build(self, cr, uid, env_id, return_id=False):
        super(t4_clinical_demo_env, self).build(cr, uid, env_id)
        self.build_patients(cr, uid, env_id)
        if return_id:
            return env_id
        else:
            return self.browse(cr, uid, env_id)
    

 
    
    def build_patients(self, cr, uid, env_id):
        fake.seed(next_seed())
        env = self.browse(cr, SUPERUSER_ID, env_id)
        assert env.pos_id, "POS is not created/set in the env id=%s" % env_id
        activity_pool = self.pool['t4.activity']
        api = self.pool['t4.clinical.api']
        register_pool = self.pool['t4.clinical.adt.patient.register']
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        #import pdb; pdb.set_trace()
        adt_user_id = self.get_adt_user_ids(cr, uid, env_id)[0]
        for i in range(env.patient_qty):
            register_activity = self.create_complete(cr, adt_user_id, env_id, 't4.clinical.adt.patient.register', {}, {})
            admit_data = {'other_identifier': register_activity.data_ref.other_identifier}
            admit_activity = self.create_complete(cr, adt_user_id, env_id, 't4.clinical.adt.patient.admit', {}, admit_data)
            placement_activity = api.get_activities(cr, uid, 
                                                         pos_ids = [env.pos_id.id],
                                                         data_models=['t4.clinical.patient.placement'],
                                                         states=['new'])[0]
            self.submit_complete(cr, adt_user_id, env_id, placement_activity.id) 
        return True
    
    
    
    
    
    
    