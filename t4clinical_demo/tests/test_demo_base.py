from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv
import openerp
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

class aaa(openerp.addons.t4clinical_demo.api_demo.t4_clinical_demo):
    # configuration
    pass

class test_test_base(common.SingleTransactionCase):
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
        global pos_id, ward_location_ids, bed_location_ids, adt_user_id, nurse_user_ids, demo_pool
    
        cr, uid = self.cr, self.uid
              
        patient_pool = self.registry('t4.clinical.patient')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        activity_pool = self.registry('t4.activity')
        user_pool = self.registry('res.users')
        imd_pool = self.registry('ir.model.data')
        device_type_pool = self.registry('t4.clinical.device.type')
        device_pool = self.registry('t4.clinical.device')
        
        demo_pool = self.registry('t4.clinical.demo')
        
        super(test_test_base, self).setUp()
        
    def test_demo(self):

#         pos_location_id = demo_pool.create_pos_location(cr, uid)
#         bed_location_id = demo_pool.create_bed_location(cr, uid)
#         ward_location_id = demo_pool.create_ward_location(cr, uid)
#         admission_location_id = demo_pool.create_admission_location(cr, uid)
#         discharge_location_id = demo_pool.create_discharge_location(cr, uid)
#         pos_id = demo_pool.create_pos(cr, uid)
#         adt_user_id = demo_pool.create_adt_user(cr, uid)
#         nurse_user_id = demo_pool.create_nurse_user(cr, uid)
#         device_type_id = demo_pool.create_device_type(cr, uid)
#         device_id = demo_pool.create_device(cr, uid)
         
        pos_env = demo_pool.create_pos_env(cr, uid)
        adt_user_id = pos_env['adt_users'][0]['id']
        # Register
        register_activity_id = demo_pool.create_activity_adt_register(cr, adt_user_id)
        activity_pool.complete(cr, uid, register_activity_id)
        
        # Admit
        admit_activity_id = demo_pool.create_activity_adt_admit(cr, adt_user_id)
        activity_pool.complete(cr, uid, admit_activity_id)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        