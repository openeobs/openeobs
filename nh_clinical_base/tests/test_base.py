from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv

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

class BaseTest(SingleTransactionCase):
    @classmethod
    def tearDownClass(cls):
        if config['test_commit']:
            cls.cr.commit()
            print "COMMIT"
        else:
            cls.cr.rollback()
            print "ROLLBACK"
        cls.cr.close()
        
    def setUp(self):
        global cr, uid, seed
        global patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
    
        cr, uid = self.cr, self.uid
              
        patient_pool = self.registry('nh.clinical.patient')
        location_pool = self.registry('nh.clinical.location')
        pos_pool = self.registry('nh.clinical.pos')
        activity_pool = self.registry('nh.activity')
        user_pool = self.registry('res.users')
        imd_pool = self.registry('ir.model.data')
        device_type_pool = self.registry('nh.clinical.device.type')
        device_pool = self.registry('nh.clinical.device')
        super(BaseTest, self).setUp()
        
    def create_activity(self, cr, uid, data_model, vals_activity={}, vals_data={}, context=None):
        model_pool = self.registry(data_model)
        activity_id = model_pool.create_activity(cr, uid, vals_activity, vals_data, context)
        _logger.info("Activity created id=%s, data_model=%s\n vals_activity: %s\n vals_data: %s" 
                     % (activity_id, data_model, vals_activity, vals_data))
        activity = activity_pool.browse(cr, uid, activity_id)

        # tests
        self.assertTrue(activity.state == "new", 
                        "activity.state (%s) != 'new'" 
                        % (activity.state)) 
        self.assertTrue(activity.data_model == model_pool._name, 
                        "activity.data_model (%s) != model_pool._name (%s)" 
                        % (activity.data_model, model_pool._name))        
        return activity_id
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        res = activity_pool.submit(cr, uid, activity_id, vals, context)
        # tests
        activity = activity_pool.browse(cr, uid, activity_id)
        model_pool = self.registry(activity.data_model)
        activity_data = model_pool.read(cr, uid, activity.data_ref.id,[])
        self.assertTrue(set(vals.keys()) <= set(activity_data.keys()), 
                        "vals is not a subset of activity data. \n vals: %s\n activity data: %s" 
                        % (vals, activity))         

        return res
    
    def complete(self, cr, uid, activity_id, context=None):    
        res = activity_pool.complete(cr, uid, activity_id, context)
        return res    
       
    def create_pos_environment(self, WARD_QTY=5, BED_PER_WARD=3, DEVICES=5):
        """
        creates 1 pos environment
        """

        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
        _logger.info("Executing create_environment()")
        # Create POS
        pos_id = self.create_pos()
        pos = pos_pool.browse(cr, uid, pos_id)

        # Create wards
        ward_location_ids = [self.create_ward(pos.location_id.id) for i in range(WARD_QTY)]
         
        # Create beds 
        bed_location_ids = []
        for ward_location_id in ward_location_ids:
            bed_location_ids.extend([self.create_bed(ward_location_id) for i in range(BED_PER_WARD)])
         
        # Create ADT user
        adt_user = user_pool.browse(cr, uid, self.create_adt_user(pos.id))
        adt_user_id = adt_user.id
         
        # Create nurse users
        nurse_user_ids = [
             self.create_nurse_user(ward_location_ids),
             self.create_nurse_user(ward_location_ids)
         ]
        
        # Create devices
        device_ids = [self.create_device() for i in range(DEVICES)]
               
        env = {'pos_id': pos_id,
               'pos_location_id': pos_pool.browse(cr, uid, pos_id).location_id.id,
               'adt_user_id': adt_user_id,
               'bed_location_ids': bed_location_ids,
               'ward_location_ids': ward_location_ids,
               'nurse_user_ids': nurse_user_ids,
               'device_ids': device_ids,
               }
        return env
    


    def create_nurse_user(self, location_ids):
        data = self.data_nurse_user(location_ids)
        user_id = user_pool.create(cr, uid, data)
        _logger.info("Nurse user created id=%s\n data: %s" % (user_id, data))
        return user_id  

    def create_adt_user(self, pos_id):
        fake.seed(next_seed())
        adt_group = imd_pool.get_object(cr, uid, "nh_clinical_base", "group_nhc_adt")
        pos = pos_pool.browse(cr, uid, pos_id) 
        data = self.data_adt_user({'pos_id': pos_id})
        user_id = user_pool.create(cr, uid, data)
        _logger.info("ADT user created id=%s\n data: %s" % (user_id, data))
        return user_id

    def create_bed(self, parent_id):
        data = self.data_bed_location(parent_id)
        location_id = location_pool.create(cr, uid, data)
        _logger.info("Bed location created id=%s\n data: %s" % (location_id, data))
        return location_id
        
    def create_ward(self, parent_id):
        data = self.data_ward_location(parent_id)
        location_id = location_pool.create(cr, uid, data)
        _logger.info("Ward location created id=%s\n data: %s" % (location_id, data))
        return location_id        
    
    def create_pos(self):
        fake.seed(next_seed())
        data = self.data_pos()
        pos_id = pos_pool.create(cr, uid, data)
        _logger.info("POS created id=%s\n data: %s" % (pos_id, data))
#         from pprint import pprint as pp
#         location_ids = location_pool.search(cr, uid, [['id','>',25]])
#         records = location_pool.read(cr, uid, location_ids, 
#                                      ['name', 'parent_id', 'pos_id'])
#         pp(records)
        return pos_id

    def create_pos_location(self):
        data = self.data_pos_location()
        location_id = location_pool.create(cr, uid, data)
        _logger.info("POS location created id=%s\n data: %s" % (location_id, data))
        return location_id 
    
    def create_admission_location(self, parent_id=None):
        data = self.data_admission_location(parent_id and {'parent_id': parent_id} or {})
        location_id = location_pool.create(cr, uid, data)
        _logger.info("Admission location created id=%s\n data: %s" % (location_id, data))
        return location_id     
    
    def create_discharge_location(self, parent_id=None):
        data = self.data_discharge_location(parent_id and {'parent_id': parent_id} or {})
        location_id = location_pool.create(cr, uid, data)
        _logger.info("Discharge location created id=%s\n data: %s" % (location_id, data))
        return location_id 

    def create_device_type(self, data={}):
        device_type_id = device_type_pool.create(cr, uid, self.data_device_type())
        _logger.info("Device type created id=%s" % (device_type_id))
        return device_type_id
    
    def create_device(self, data={}):
        device_id = device_pool.create(cr, uid, self.data_device())
        _logger.info("Device created id=%s" % (device_id))
        return device_id

    def data_patient(self, data={}):
        fake.seed(next_seed())
        family_name = data.get('family_name') or fake.last_name()
        given_name = data.get('given_name') or fake.first_name()
        gender = data.get('gender') or fake.random_element(('M','F'))
        other_identifier = data.get('other_identifier') or str(fake.random_int(min=1000001, max=9999999))
        dob = data.get('dob') or fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S")        
        res = {
                'family_name': family_name, 
                'given_name': given_name,
                'other_identifier': other_identifier, 
                'dob': dob, 
                'gender': gender, 
                'sex': gender         
                }    
        return res
    
    def data_adt_user(self, data={}):
        fake.seed(next_seed())
        adt_group = imd_pool.get_object(cr, uid, "nh_clinical_base", "group_nhc_adt")
        pos = pos_pool.browse(cr, uid, pos_id) 
        res = {
            'name': data.get('name') or "ADT user for %s" % pos.name,
            'login': data.get('login') or "adt_%s" % pos.location_id.code.lower(),
            'password': data.get('password') or "adt_%s" % pos.location_id.code.lower(),
            'groups_id': data.get('groups_id') or [(4, adt_group.id)],
            'pos_id': data.get('pos_id') or self.create_pos()
        }  
        return res
    
    def data_bed_location(self, parent_id, data={}):
        fake.seed(next_seed()) 
        code = "BED_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': data.get('name') or code, 
               'code': data.get('code') or code, 
               'type': data.get('type') or 'poc', 
               'usage': data.get('usage') or 'bed', 
               'parent_id': parent_id
               }
        return res               
    
    def data_ward_location(self, parent_id, data={}):
        fake.seed(next_seed()) 
        code = "WARD_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': data.get('name') or code, 
               'code': data.get('code') or code, 
               'type': data.get('type') or 'structural', 
               'usage': data.get('usage') or 'ward', 
               'parent_id': parent_id
               }
        return res            
    
    
    def data_nurse_user(self, location_ids, data={}):
        fake.seed(next_seed())
        nurse_group = imd_pool.get_object(cr, uid, "nh_clinical_base", "group_nhc_nurse")
        name = fake.first_name()
        res = {
            'name': data.get('name') or "Nurse %s" % name,
            'login': data.get('login') or name.lower(),
            'password': data.get('password') or name.lower(),
            'groups_id': data.get('groups_id') and [(4, group_id) for group_id in data['groups_id']] or [(4, nurse_group.id)],
            'location_ids': [(4,location_id) for location_id in location_ids]
        }
        return res      

    def data_pos_location(self, data={}):
        fake.seed(next_seed()) 
        code = "POS_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': data.get('name') or "POS Location (%s)" % code, 
               'code': data.get('code') or code, 
               'type': data.get('type') or 'structural', 
               'usage': data.get('usage') or 'hospital', 
               'parent_id': data.get('parent_id')
               }
        return res 

    def data_admission_location(self, data={}):
        fake.seed(next_seed()) 
        code = "ADMISSION_LOCATION_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': data.get('name') or code, 
               'code': data.get('code') or code, 
               'type': data.get('type') or 'structural', 
               'usage': data.get('usage') or 'room', 
               'parent_id': data.get('parent_id')
               }
        return res      

    def data_discharge_location(self, data={}):
        fake.seed(next_seed()) 
        code = "DISCHARGE_LOCATION_"+str(fake.random_int(min=100, max=999))
        res = {
               'name': data.get('name') or code, 
               'code': data.get('code') or code, 
               'type': data.get('type') or 'structural', 
               'usage': data.get('usage') or 'room', 
               'parent_id': data.get('parent_id')
               }
        return res  

    def data_pos(self, data={}):
        fake.seed(next_seed())
        location_id = data.get('location_id') or self.create_pos_location()
        res = {
                'name': "HOSPITAL_"+str(fake.random_int(min=100, max=999)),
                'location_id': location_id,
                'lot_admission_id': data.get('lot_admission_id') or self.create_admission_location(location_id),
                'lot_discharge_id': data.get('lot_discharge_id') or self.create_discharge_location(location_id)
                }
        return res    
    
    def data_device_type(self, data={}):
        fake.seed(next_seed())
        flow_directions = ['none', 'in', 'out', 'both']
        res = {
                'name': data.get('name') or "DEVICE_TYPE_"+str(fake.random_int(min=100, max=999)),
                'flow_direction': data.get('flow_direction') or flow_directions[fake.random_int(min=0, max=3)],
                }
        return res     
    
    def data_device(self, data={}):
        fake.seed(next_seed())
        type_id = data.get('type_id') or device_type_pool.create(cr, uid, self.data_device_type())
        res = {
               'type_id': type_id
               }
        return res     
    
    
    
    
    
        