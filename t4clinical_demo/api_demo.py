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
    
#     def __init__(self, pool, cr):
#         res = super(t4_clinical_demo, self).__init__(pool, cr)
#         
#         for model in pool.models.keys():
#             if model.startswith('t4.clinical'):
#                 self._pos['activity_ids'].update({model: []})
#         pp(self._pos['activity_ids'])
#         return res
    
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
        admit_activity_ids = self.get_activity_ids(cr, uid, 't4.clinical.adt.patient.admit')
        activity_pool = self.pool['t4.activity']
        patient_ids = [a.patient_id.id for a in activity_pool.browse(cr, uid, admit_activity_ids)]
        return patient_ids
    
    def get_current_patient_ids(self, cr, uid):
        activity_pool = self.pool['t4.activity']
        spell_pool = self.pool['t4.clinical.spell']
        patient_ids = self.get_all_patient_ids(cr, uid)
        spell_ids = spell_pool.search(cr, uid, [['state','=','started'],['patient_id','in',patient_ids]])
        patient_ids = [s.patient_id.id for s in spell_pool.browse(cr, uid, spell_ids)]
        return patient_ids    
    
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
        domain = [['user_ids', 'in', uid], ['date_terminated','=', False], ['data_model','!=', 't4.clinical.spell']]
        ids = activity_pool.search(cr, uid, domain)
        return ids
    
    def complete_activity(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity_pool.complete(cr, uid, activity_id)
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
        try:
            activity_id = model_pool.create_activity(cr, uid, va, vd)
        except:
            pp('vals_activity:')
            pp(va)
            pp('vals_data:')
            pp(vd)            
        # self._pos['activity_ids'][data_model] filled in in the constructor 
        self._pos['activity_ids'].append(activity_id)
        return activity_id
        
    def data_activity(self, cr, uid, data_model, data={}):
        d = data.copy()
        # data method name pattern:
        # t4.clinical.patient.observation.ews => data_patient_observation_ews
        data_method = data_model.replace('t4.clinical.','data_').replace('.','_')
        if hasattr(self, data_method):
           d = eval("self.%s(cr, uid, data)" % data_method)
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
        if 'location_id' in data:
            location_id = data['location_id']
        elif data.get('suggested_location_id'):
            domain = [['id', 'child_of', data['suggested_location_id']]]
            location_ids = self.pool['t4.clinical.location'].search(cr, uid, domain)
            location_id = fake.random_element(array=location_ids)
        else:
            location_ids = self.pool['t4.clinical.location'].get_available_location_ids(cr, uid, usages=['bed'])
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














