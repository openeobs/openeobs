from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv
from pprint import pprint as pp

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
    _name = 't4.clinical.demo'
    
    _pos = {
        'data': {},
        'timeline': {},
        'id': None,
        'register_activity_ids': [],
        'admit_activity_ids': [],
        
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

              
    def create_pos_env(self, cr, uid):
        """
        creates 1 pos environment
        """
        _logger.info("Executing create_environment()")
        pos_pool = self.pool['t4.clinical.pos']
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


        pp(self._pos)
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
                                    and data['flow_direction'] 
                                    or flow_directions[fake.random_int(min=0, max=max)],
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
        'location': fields.text('Location'),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"), 
        'other_identifier': fields.text("Other Identifier"),
        'doctors': fields.text("Doctors"),
        """
        fake.seed(next_seed())
        
        register_activities = self.pool['t4.activity'].browse(cr, uid, self._pos['register_activity_ids'])
        locations = self.pool['t4.clinical.location'].browse(cr, uid, [l['id'] for l in self._pos['wards']])
        
        data['other_identifier'] = 'other_identifier' in data and data['other_identifier'] \
                                   or register_activities[fake.random_int(min=0, max=len(register_activities)-1)].data_ref.other_identifier            
        data['location'] = 'location' in data and data['location'] \
                            or locations[fake.random_int(min=0, max=len(locations)-1)].code
        data['code'] = str(fake.random_int(min=10001, max=99999))
        data['start_date'] = fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S")
        
        if not data.get('doctors'):
            d = [{
                    'code': str(fake.random_int(min=10001, max=99999)),
                    'type': fake.random_element(array=('r','c')),
                    'title': fake.random_element(array=('Mr','Mrs','Ms','Dr')),
                    'family_name': fake.last_name(),
                    'given_name': fake.first_name()
                    },
                   ]
            data['doctors'] = d   
        #import pdb; pdb.set_trace()
        return data  


    def create_activity_adt_register(self, cr, uid, data={}):
        d = data.copy()
        register_pool = self.pool['t4.clinical.adt.patient.register']
        d = self.data_adt_patient_register(cr, uid, d)
        register_activity_id = register_pool.create_activity(cr, uid, {}, d)
        self._pos['register_activity_ids'].append(register_activity_id)
        return register_activity_id
        

    def data_adt_patient_register(self, cr, uid, data={}):
        fake.seed(next_seed())
        family_name = 'family_name' in data and data['family_name'] or fake.last_name()
        given_name = 'given_name' in data and data['given_name'] or fake.first_name()
        gender = 'gender' in data and data['gender'] or fake.random_element(array=('M','F'))
        other_identifier = 'other_identifier' in data and data['other_identifier'] or str(fake.random_int(min=1000001, max=9999999))
        dob = 'dob' in data and data['dob'] or fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S")
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
        ids = activity_pool.search(cr, uid, [['user_ids', 'in', uid], ['date_terminated','=', False]])
        return ids
    
    def process_user_activities(self, cr, uid, activity_ids=[]):
        user_pool = self.pool['res.users']
        activity_pool = self.pool['t4.activity']
        user = user_pool.browse(cr, uid, uid)
        _logger.info("User '%s' started activity processing..." % user.name) 
        activity_ids = activity_ids or self.get_user_activity_ids(cr, uid)
        activities = activity_pool.browse(cr, uid, activity_ids)
        _logger.info("Activities to be processed: %s" % [{'id':a.id, 'data_model':a.data_model} for a in activities])
        data_model_method_map = {
            't4.clinical.patient.placement': 'process_placement_activity',
            't4.clinical.patient.observation.ews': 'process_ews_activity',
            't4.clinical.patient.observation.gcs': 'process_gcs_activity',
            't4.clinical.patient.observation.blood_product': 'process_blood_product_activity'
            
        }
        for activity in activities:
           _logger.info("Processing id=%s, data_model='%s'" % (activity.id, activity.data_model))
           if activity.data_model in data_model_method_map:
               eval("self.%s(cr, uid, activity.id)" % data_model_method_map[activity.data_model])
           else:
              _logger.info("Skipping activity id=%s data_model='%s'. Processing method not implemented." % (activity.id, activity.data_model))
        _logger.info("User '%s' finished activity processing." % user.name)
        return True

    def process_placement_activity(self, cr, uid, activity_id):
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
        if 'location_id' in data:
            location_id = data['location_id']
        else:
            domain = data['suggested_location_id'] and [['id', 'child_of', data['suggested_location_id']]] or []
            location_ids = self.pool['t4.clinical.location'].search(cr, uid, domain)
            location_id = fake.random_element(array=location_ids)
        d.update({'location_id': location_id})
        return d
        
    def process_ews_activity(self, cr, uid, activity_id):
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

        d = {
            'respiration_rate': 'respiration_rate' in d and d['respiration_rate'] or fake.random_int(min=5, max=34),
            'indirect_oxymetry_spo2': 'indirect_oxymetry_spo2' in d and d['indirect_oxymetry_spo2'] or fake.random_int(min=85, max=100),
            'body_temperature': 'body_temperature' in d and d['body_temperature'] or float(fake.random_int(min=350, max=391))/10.0,
            'blood_pressure_systolic': 'blood_pressure_systolic' in d and d['blood_pressure_systolic'] or fake.random_int(min=65, max=206),
            'pulse_rate': 'pulse_rate' in d and d['pulse_rate'] or fake.random_int(min=35, max=136),
            'avpu_text': 'avpu_text' in d and d['avpu_text'] or fake.random_element(array=('A', 'V', 'P', 'U')),
            'oxygen_administration_flag': 'oxygen_administration_flag' in d and d['oxygen_administration_flag'] or fake.random_element(array=(True, False)),   
            'blood_pressure_diastolic': 'blood_pressure_diastolic' in d and d['blood_pressure_diastolic'] or fake.random_int(min=35, max=176)
        }
        if not 'patient_id' in d:
            # FIXME need to decide where we are getting patients from
            # by current logic must be placed ones
            pass
        
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


    def process_gcs_activity(self, cr, uid, activity_id):
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
        data = {
            'eyes': 'eyes' in d and d['eyes'] or fake.random_element(array=('1', '2', '3', '4', 'C')),
            'verbal': 'verbal' in d and d['verbal'] or fake.random_element(array=('1', '2', '3', '4', '5', 'T')),
            'motor': 'motor' in d and d['motor'] or fake.random_element(array=('1', '2', '3', '4', '5', '6')),
        }
        if not 'patient_id' in d:
            # FIXME need to decide where we are getting patients from
            # by current logic must be placed ones
            pass
        
        return d    

    def process_blood_product_activity(self, cr, uid, activity_id):
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
             'vol': 'vol' in d and d['vol'] or float(fake.random_int(min=1, max=10))
        } 
        if not 'patient_id' in d:
            # FIXME need to decide where we are getting patients from
            # by current logic must be placed ones
            pass
        return d   


        
        
#     def create_activity(self, cr, uid, data_model, vals_activity={}, vals_data={}, context=None):
#         model_pool = self.registry(data_model)
#         activity_id = model_pool.create_activity(cr, uid, vals_activity, vals_data, context)
#         _logger.info("Activity created id=%s, data_model=%s\n vals_activity: %s\n vals_data: %s" 
#                      % (activity_id, data_model, vals_activity, vals_data))
#         activity = activity_pool.browse(cr, uid, activity_id)
# 
#         # tests
#         self.assertTrue(activity.state == "new", 
#                         "activity.state (%s) != 'new'" 
#                         % (activity.state)) 
#         self.assertTrue(activity.data_model == model_pool._name, 
#                         "activity.data_model (%s) != model_pool._name (%s)" 
#                         % (activity.data_model, model_pool._name))        
#         return activity_id
#     
#     def submit(self, cr, uid, activity_id, vals, context=None):
#         res = activity_pool.submit(cr, uid, activity_id, vals, context)
#         # tests
#         activity = activity_pool.browse(cr, uid, activity_id)
#         model_pool = self.registry(activity.data_model)
#         activity_data = model_pool.read(cr, uid, activity.data_ref.id,[])
#         self.assertTrue(set(vals.keys()) <= set(activity_data.keys()), 
#                         "vals is not a subset of activity data. \n vals: %s\n activity data: %s" 
#                         % (vals, activity))         
# 
#         return res
#     
#     def complete(self, cr, uid, activity_id, context=None):    
#         res = activity_pool.complete(cr, uid, activity_id, context)
#         return res    
       

    


 
   





   
    
