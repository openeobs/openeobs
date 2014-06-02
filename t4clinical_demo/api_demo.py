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
        'devices':[
                  {'data': {},'timeline': {}, 'id':None},
                  {'data': {},'timeline': {}, 'id':None},
                  ]
                          
    }
#     _columns = {
#         'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
#         'bed_location_ids': many2many('t4.clinical.location', 'demo_location_rel', 'demo_id', 'location_id', 'Bed Locations'),
#         
#     }
#     
#     def get_pos_id(self, cr, uid, context):
#         pos_pool = self.pool['t4.clinical.pos']
#         pos_id = self.create_pos(cr, uid)
#         return pos_id    
# 
#     def get_bed_location_ids(self, cr, uid, context):
#         location_pool = self.pool['t4.clinical.location']
#         location_ids = self.create_pos(cr, uid)
#         # Create beds 
#         for bed in pos_env['beds']:
#             bed['data'].update({'parent_id': pos.location_id.id})
#             bed.update({'id': self.create_bed_location(cr, uid, bed['data'])})        
#         return pos_id      
#     
#     _defaults = {
#         'pos_id': get_pos_id,
#         'bed_location_ids': get_bed_location_ids,
#      }
    

              
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
        d = self.data_activity_adt_admit(cr, uid, d)
        admit_activity_id = admit_pool.create_activity(cr, uid, {}, d)
        self._pos['admit_activity_ids'].append(admit_activity_id)
        return admit_activity_id

    def data_activity_adt_admit(self, cr, uid, data={}):
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
        d = self.data_activity_adt_register(cr, uid, d)
        register_activity_id = register_pool.create_activity(cr, uid, {}, d)
        self._pos['register_activity_ids'].append(register_activity_id)
        return register_activity_id
        

    def data_activity_adt_register(self, cr, uid, data={}):
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
       

    


 
   





   
    
