from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
#from t4_base.tools import xml2db_id

from openerp import tools
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

class TestADT(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid, seed
        global register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
               activity_id, api_pool, location_pool, pos_pool, user_pool, imd_pool
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
        
        cr, uid = self.cr, self.uid
              
        register_pool = self.registry('t4.clinical.adt.patient.register')
        patient_pool = self.registry('t4.clinical.patient')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        activity_pool = self.registry('t4.clinical.activity')
        transfer_pool = self.registry('t4.clinical.adt.patient.transfer')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        api_pool = self.registry('t4.clinical.api')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        user_pool = self.registry('res.users')
        imd_pool = self.registry('ir.model.data')
        
        super(TestADT, self).setUp()
    
    
    
    def test_adt(self):        
        global cr, uid, seed
        global register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
               activity_id, api_pool, location_pool
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
        
        self.create_environment()
        
        self.register_patient()
        
        
        
        
    def register_patient(self):
        global cr, uid, seed, activity_pool, register_pool, patient_pool
        res = {}
        fake.seed(next_seed()) 
        gender = fake.random_element(array=('M','F'))
        other_identifier = str(fake.random_int(min=1000001, max=9999999))
        dob = fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S")
        data = {
                'family_name': fake.last_name(), 
                'given_name': fake.first_name(),
                'other_identifier': other_identifier, 
                'dob': dob, 
                'gender': gender, 
                'sex': gender         
                }
        # test input
        ##############
        duplicate_ids = patient_pool.search(cr, uid, [['other_identifier','=',data['other_identifier']]])
        register_activity_id = register_pool.create_activity(cr, uid, {},{})
        # test create
        ##############
        register_activity = activity_pool.browse(cr, uid, register_activity_id)
        self.assertTrue(register_activity.data_model == register_pool._name, 
                        "register_activity.data_model != register_pool._name !")
        register_submit_res = activity_pool.submit(cr, uid, register_activity_id, data)
        # test create
        ##############
        
        register_complete_res = activity_pool.complete(cr, uid, register_activity_id)
        # test complete
        ##############
        
        res.update({'register_activity_id': register_activity_id})
        res.update(register_submit_res)
        res.update(register_complete_res)
        # test output
        ###############
        
        return res        
        
        
        
        
    def create_environment(self): 
               
        global cr, uid, seed
        global register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
               activity_id, api_pool, location_pool, pos_pool
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids
        
        WARD_QTY = 5
        BED_PER_WARD = 3
        
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

    def create_nurse_user(self, location_ids):
        global cr, uid, seed, user_pool, imd_pool
        fake.seed(next_seed())
        nurse_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_nurse")   
        name = fake.first_name() 
        data = {
            'name': "Nurse %s" % name,
            'login': name.lower(),
            'password': name.lower(),
            'groups_id': [(4, nurse_group.id)],
            'location_ids': [(4,location_id) for location_id in location_ids]
        }
        #import pdb; pdb.set_trace()
        user_id = user_pool.create(cr, uid, data)
        _logger.info("Nurse user created id=%s\n data: %s" % (user_id, data))
        return user_id  

    def create_adt_user(self, pos_id):
        global cr, uid, seed, user_pool, imd_pool, pos_pool
        fake.seed(next_seed())
        adt_group = imd_pool.get_object(cr, uid, "t4clinical_base", "group_t4clinical_adt")  
        pos = pos_pool.browse(cr, uid, pos_id) 
        data = {
            'name': "ADT user for %s" % pos.name,
            'login': "adt_%s" % pos.location_id.code.lower(),
            'password': "adt_%s" % pos.location_id.code.lower(),
            'groups_id': [(4, adt_group.id)],
            'pos_id': pos_id
        }
        user_id = user_pool.create(cr, uid, data)
        _logger.info("ADT user created id=%s\n data: %s" % (user_id, data))
        return user_id

    def create_bed(self, parent_id):
        global cr, uid, seed, location_pool 
        fake.seed(next_seed()) 
        code = "B"+str(fake.random_int(min=100, max=999))
        data = {'name': code, 'code': code, 'type': 'poc', 'usage': 'bed', 'parent_id': parent_id}
        location_id = location_pool.create(cr, uid, data)
        _logger.info("Bed location created id=%s\n data: %s" % (location_id, data))
        return location_id
        
    def create_ward(self, parent_id):
        global cr, uid, seed, location_pool 
        fake.seed(next_seed()) 
        code = "W"+str(fake.random_int(min=100, max=999))
        data = {'name': code, 'code': code, 'type': 'poc', 'usage': 'ward', 'parent_id': parent_id}
        location_id = location_pool.create(cr, uid, data)
        _logger.info("Ward location created id=%s\n data: %s" % (location_id, data))
        return location_id        
    
    def create_pos(self):
        global cr, uid, seed, location_pool, pos_pool
        global location_pool, pos_pool
        fake.seed(next_seed())
        # POS location 
        code = "POS"+str(fake.random_int(min=1, max=9))
        data = {'name': "POS Location (%s)" % code, 'code': code, 'type': 'pos', 'usage': 'hospital'}
        pos_location_id = location_pool.create(cr, uid, data)
        _logger.info("POS location created id=%s\n data: %s" % (pos_location_id, data))
        # Admission location
        data = {'name': "Admission Location (%s)" % code, 
                'code': "ADML-%s" % code, 
                'type': 'pos', 'usage': 'hospital', 'parent_id': pos_location_id}
        lot_admission_id = location_pool.create(cr, uid, data)
        _logger.info("Admission location created id=%s\n data: %s" % (lot_admission_id, data))
        # Discharge Location
        data = {'name': "Discharge Location (%s)" % code, 
                'code': "DISL-%s" % code, 
                'type': 'pos', 'usage': 'hospital', 'parent_id': pos_location_id}
        lot_discharge_id = location_pool.create(cr, uid, data)   
        _logger.info("Discharge location created id=%s\n data: %s" % (lot_discharge_id, data))             
        # POS        
        data = {'name': "HOSPITAL"+str(fake.random_int(min=1, max=9)),
                'location_id': pos_location_id,
                'lot_admission_id': lot_admission_id,
                'lot_discharge_id': lot_discharge_id}
        pos_id = pos_pool.create(cr, uid, data)
        _logger.info("POS created id=%s\n data: %s" % (pos_id, data))
        return pos_id