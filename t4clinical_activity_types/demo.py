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


class t4_clinical_demo(orm.Model):
    _inherit = 't4.clinical.demo'
    
    
    
## Shorcuts

    

    def complete_patient_placement(self, cr, uid, data={}):
        d = data.copy()
        placement_activities = self.get_activity_browse(cr, uid, 't4.clinical.patient.placement')
        if 'activity_id' in d:
            self.pool['t4.activity'].complete(cr, uid, d['activity_id'])
            return True
                
        if 'patient_id' not in d:
            placement_activities = [pa for pa in placement_activities if not pa.date_terminated]
            activity_id = placement_activities and fake.random_element(placement_activities).id
        else:
            placement_activities = [pa for pa in placement_activities if pa.patient_id.id == d['patient_id'] and not pa.date_terminated]
            activity_id = placement_activities and placement_activities[0]
        
        if not placement_activities:
            _logger.warn('No non-completed placements found in the demo data!')
        else:
            self.pool['t4.activity'].complete(cr, uid, activity_id)
        return True
            
            
    def adt_patient_register(self, cr, uid, data={}):
        register_activity_id = self.create_activity(cr, uid, 't4.clinical.adt.patient.register', {}, data)
        self.pool['t4.activity'].complete(cr, uid, register_activity_id)    
        return register_activity_id
    
    def adt_patient_admit(self, cr, uid, data={}):
        d = data.copy()
        if 'other_identifier' not in d:
            reg_activity = self.get_activity_browse(cr, uid, data_model='t4.clinical.adt.patient.register')
            admit_activity = self.get_activity_browse(cr, uid, data_model='t4.clinical.adt.patient.admit')
            reg_patient_ids = [ra.patient_id.id for ra in reg_activity]
            admit_patient_ids = [aa.patient_id.id for aa in admit_activity]
            not_admitted_pateint_ids = list(set(reg_patient_ids) - set(admit_patient_ids))
            patients = self.pool['t4.clinical.patient'].browse(cr, uid, not_admitted_pateint_ids)
            if not patients:
                _logger("All patients are admitted!")
            else:
                d.update({'other_identifier':fake.random_element(patients).other_identifier})
        admit_activity_id = self.create_activity(cr, uid, 't4.clinical.adt.patient.admit', {}, d)
        self.complete_activity(cr, uid, admit_activity_id)
        return admit_activity_id
        
          
    def data_available_bed_location_id(self, cr, uid, parent_id=None):
        fake.seed(next_seed())
        demo_location_ids = [bed['id'] for bed in self._pos['beds']] 
        location_ids =  self.pool['t4.clinical.api'].location_availability_map(cr, uid, 
                                                                                   ids=demo_location_ids, 
                                                                                   usages=['bed'], 
                                                                                   available_range=[1,1]).keys()
        if parent_id:
            location_ids = self.pool['t4.clinical.location'].search(cr, uid, [['id', 'child_of', parent_id]])   
        res = location_ids and fake.random_element(location_ids) or False
        return res
              
    
    def get_activity_ids(self, cr, uid, data_model=None):
        activity_ids = self._pos['activity_ids']
        if data_model:
            activity_pool = self.pool['t4.activity']
            activity_ids = activity_pool.search(cr, uid, [['id','in',activity_ids],['data_model','=',data_model]])
        return activity_ids
    
    
    
    def get_activity_browse(self, cr, uid, data_model=None):
        activity_pool = self.pool['t4.activity']
        res = activity_pool.browse(cr, uid, self.get_activity_ids(cr, uid, data_model=data_model))
        return res
        
    def get_all_patient_ids(self, cr, uid):
        reg_activity_ids = self.get_activity_ids(cr, uid, 't4.clinical.adt.patient.register')
        activity_pool = self.pool['t4.activity']
        patient_ids = [a.patient_id.id for a in activity_pool.browse(cr, uid, reg_activity_ids)]
        
        return patient_ids
    
    def get_current_patient_ids(self, cr, uid):
        activity_pool = self.pool['t4.activity']
        spell_pool = self.pool['t4.clinical.spell']
        patient_ids = self.get_all_patient_ids(cr, uid)
        spell_ids = spell_pool.search(cr, uid, [['state','=','started'],['patient_id','in',patient_ids]])
        patient_ids = [s.patient_id.id for s in spell_pool.browse(cr, uid, spell_ids)]
        return patient_ids    


#####  OPERATIONS

    def create_activity_adt_admit(self, cr, uid, data={}):
        d = data.copy()
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        d = self.data_adt_patient_admit(cr, uid, d)
        admit_activity_id = admit_pool.create_activity(cr, uid, {}, d)
        self._pos['admit_activity_ids'].append(admit_activity_id)
        return admit_activity_id

    def data_adt_patient_admit(self, cr, uid, data={}):
        """
        """
        d = data.copy()
        fake.seed(next_seed())

        register_activities = self.pool['t4.activity'].browse(cr, uid, self.get_activity_ids(cr, uid, 't4.clinical.adt.patient.register'))
        locations = self.pool['t4.clinical.location'].browse(cr, uid, [l['id'] for l in self._pos['wards']])

        d['other_identifier'] = 'other_identifier' in d and d['other_identifier'] \
                                   or fake.random_element(array=register_activities).data_ref.other_identifier
        d['location'] = 'location' in d and d['location'] or fake.random_element(array=locations).code
        d['code'] = str(fake.random_int(min=10001, max=99999))
        d['start_date'] = fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S")

        if not d.get('doctors'):
            doctors = [{
                    'code': str(fake.random_int(min=10001, max=99999)),
                    'type': fake.random_element(array=('r','c')),
                    'title': fake.random_element(array=('Mr','Mrs','Ms','Dr')),
                    'family_name': fake.last_name(),
                    'given_name': fake.first_name()
                    },
                   ]
            d['doctors'] = doctors
        return d


    def create_activity_adt_register(self, cr, uid, data={}):
        d = data.copy()
        register_pool = self.pool['t4.clinical.adt.patient.register']
        d = self.data_adt_patient_register(cr, uid, d)
        register_activity_id = register_pool.create_activity(cr, uid, {}, d)
        return register_activity_id


    def data_adt_patient_register(self, cr, uid, data={}):
        fake.seed(next_seed())
        d = data.copy()
        family_name = 'family_name' in d and d['family_name'] or fake.last_name()
        given_name = 'given_name' in d and d['given_name'] or fake.first_name()
        gender = 'gender' in d and d['gender'] or fake.random_element(array=('M','F'))
        other_identifier = 'other_identifier' in d and d['other_identifier'] or str(fake.random_int(min=1000001, max=9999999))
        dob = 'dob' in d and d['dob'] or fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S")
        res = {
                'family_name': family_name,
                'given_name': given_name,
                'other_identifier': other_identifier,
                'dob': dob,
                'gender': gender,
                'sex': gender,
                }
        return res

    def get_user_activity_ids(self, cr, uid):
        activity_pool = self.pool['t4.activity']
        domain = [['user_ids', 'in', uid], 
                  ['date_terminated','=', False],
                  # excluding spell as it is allowed to be completed by ward managers  
                  ['data_model','!=', 't4.clinical.spell']]
        ids = activity_pool.search(cr, uid, domain)
        return ids
    
    def complete_activity(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity_pool.complete(cr, uid, activity_id)
        return True

    def submit_activity(self, cr, uid, activity_id, data=None):
        activity_pool = self.pool['t4.activity']
        if data is None:
            activity = activity_pool.browse(cr, uid, activity_id)
#             model_pool = self.pool[activity.data_model]
#             data = 
            data = self.data_activity(cr, uid, activity.data_model)
        activity_pool.submit(cr, uid, activity_id, data)
        return True
        
    def create_activity(self, cr, uid, data_model, vals_activity={}, vals_data={}):
        vd = vals_data.copy()
        va = vals_activity.copy()
        data = self.data_activity(cr, uid, data_model, vd)
        vd = {k: vd.get(k) or v for k,v in data.items()}
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, vd.get('patient_id'))
        spell_activity and va.update({'parent_id': spell_activity.id})
        model_pool = self.pool[data_model]
        #import pdb; pdb.set_trace()

        activity_id = model_pool.create_activity(cr, uid, va, vd)

        self._pos['activity_ids'].append(activity_id)
        return activity_id
        
    def data_activity(self, cr, uid, data_model, data={}):
        d = data.copy()
        # data method name pattern:
        # t4.clinical.patient.observation.ews => data_patient_observation_ews
        data_method = data_model.replace('t4.clinical.','data_').replace('.','_')
        if hasattr(self, data_method):
           d = eval("self.%s(cr, uid, d)" % data_method)
        else:
           _logger.info("Data method '%s' expected, but not implemented." % (data_method))
        return d or {}



    def complete_placement_activity(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id)
        data = {}
        activity.data_ref.suggested_location_id and data.update({'suggested_location_id': activity.data_ref.suggested_location_id.id})
        data = self.data_patient_placement(cr, uid, data)
        activity_pool.submit(cr, uid, activity_id, data)
        activity_pool.complete(cr, uid, activity_id)
        return True


    def data_patient_placement(self, cr, uid, data={}):
        fake.seed(next_seed())
        d = data.copy()
        if 'location_id' in d:
            location_id = d['location_id']
        elif d.get('suggested_location_id'):
            domain = [['id', 'child_of', d['suggested_location_id']]]
            location_ids = self.pool['t4.clinical.location'].search(cr, uid, domain)
            location_id = fake.random_element(array=location_ids)
        else:
            demo_location_ids = [bed['id'] for bed in self._pos['beds']]
            location_ids = self.pool['t4.clinical.api'].location_availability_map(cr, uid, ids=demo_location_ids, usages=['bed']).keys()
            location_id = fake.random_element(array=location_ids)
        d.update({'location_id': location_id})
        return d

    def complete_ews_activity(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id)
        data = {}
        activity.data_ref.patient_id and data.update({'patient_id': activity.data_ref.patient_id.id})
        data = self.data_patient_observation_ews(cr, uid, data)
        activity_pool.submit(cr, uid, activity_id, data)
        activity_pool.complete(cr, uid, activity_id)
        return True


    def data_patient_observation_ews(self, cr, uid, data={}):
        fake.seed(next_seed())
        d = data.copy()
        #import pdb; pdb.set_trace()
        d = {
            'respiration_rate': 'respiration_rate' in d and d['respiration_rate'] or fake.random_int(min=5, max=34),
            'indirect_oxymetry_spo2': 'indirect_oxymetry_spo2' in d and d['indirect_oxymetry_spo2'] or fake.random_int(min=85, max=100),
            'body_temperature': 'body_temperature' in d and d['body_temperature'] or float(fake.random_int(min=350, max=391))/10.0,
            'blood_pressure_systolic': 'blood_pressure_systolic' in d and d['blood_pressure_systolic'] or fake.random_int(min=65, max=206),
            'pulse_rate': 'pulse_rate' in d and d['pulse_rate'] or fake.random_int(min=35, max=136),
            'avpu_text': 'avpu_text' in d and d['avpu_text'] or fake.random_element(array=('A', 'V', 'P', 'U')),
            'oxygen_administration_flag': 'oxygen_administration_flag' in d and d['oxygen_administration_flag'] or fake.random_element(array=(True, False)),
            'blood_pressure_diastolic': 'blood_pressure_diastolic' in d and d['blood_pressure_diastolic'] or fake.random_int(min=35, max=176),
            'patient_id': 'patient_id' in d and d['patient_id'] or fake.random_element(self.get_current_patient_ids(cr, SUPERUSER_ID))
        }
        if d['oxygen_administration_flag']:
            d.update({
                'flow_rate': 'flow_rate' in d and d['flow_rate'] or fake.random_int(min=40, max=60),
                'concentration': 'concentration' in d and d['concentration'] or fake.random_int(min=50, max=100),
                'cpap_peep': 'cpap_peep' in d and d['cpap_peep'] or fake.random_int(min=1, max=100),
                'niv_backup': 'niv_backup' in d and d['niv_backup'] or fake.random_int(min=1, max=100),
                'niv_ipap': 'niv_ipap' in d and d['niv_ipap'] or fake.random_int(min=1, max=100),
                'niv_epap': 'niv_epap' in d and d['niv_epap'] or fake.random_int(min=1, max=100),
            })
        return d


    def complete_gcs_activity(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id)
        data = {}
        activity.data_ref.patient_id and data.update({'patient_id': activity.data_ref.patient_id.id})
        data = self.data_patient_observation_ews(cr, uid, data)
        activity_pool.submit(cr, uid, activity_id, data)
        activity_pool.complete(cr, uid, activity_id)
        return True


    def data_patient_observation_gcs(self, cr, uid, data={}):
        fake.seed(next_seed())
        d = data.copy()
        d = {
            'eyes': 'eyes' in d and d['eyes'] or fake.random_element(array=('1', '2', '3', '4', 'C')),
            'verbal': 'verbal' in d and d['verbal'] or fake.random_element(array=('1', '2', '3', '4', '5', 'T')),
            'motor': 'motor' in d and d['motor'] or fake.random_element(array=('1', '2', '3', '4', '5', '6')),
            'patient_id': 'patient_id' in d and d['patient_id'] or fake.random_element(self.get_current_patient_ids(cr, uid))
        }
        return d

    def complete_blood_product_activity(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id)
        data = {}
        activity.data_ref.patient_id and data.update({'patient_id': activity.data_ref.patient_id.id})
        data = self.data_patient_observation_blood_product(cr, uid, data)
        activity_pool.submit(cr, uid, activity_id, data)
        activity_pool.complete(cr, uid, activity_id)
        return True


    def data_patient_observation_blood_product(self, cr, uid, data={}):
        fake.seed(next_seed())
        d = data.copy()
        d = {
             'product': 'product' in d and d['product'] or fake.random_element(array=('rbc', 'ffp', 'platelets', 'has', 'dli', 'stem')),
             'vol': 'vol' in d and d['vol'] or float(fake.random_int(min=1, max=10)),
             'patient_id': 'patient_id' in d and d['patient_id'] or fake.random_element(self.get_current_patient_ids(cr, uid))
        }
        return d


    def data_patient_observation_height(self, cr, uid, data={}):
        fake.seed(next_seed())
        d = data.copy()
        d = {
             'height': 'height' in d and d['height'] or float(fake.random_int(min=160, max=200))/100.0,
             'patient_id': 'patient_id' in d and d['patient_id'] or fake.random_element(self.get_current_patient_ids(cr, uid))
        }
        return d











