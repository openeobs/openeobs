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
        global cr, uid, seed, demo_pool, activity_pool
    
        cr, uid = self.cr, self.uid
        
        demo_pool = self.registry('t4.clinical.demo')
        activity_pool = self.registry('t4.activity')
        
        super(test_test_base, self).setUp()
        
    def test_demo(self):
        # create env 
        pos_env = demo_pool.create_pos_env(cr, uid)
        adt_user_id = pos_env['adt_users'][0]['id']
         
        # Register
        register_activity_id = demo_pool.create_activity(cr, adt_user_id, 't4.clinical.adt.patient.register')
        demo_pool.complete_activity(cr, uid, register_activity_id)
         
        # Admit
        admit_activity_id = demo_pool.create_activity(cr, adt_user_id, 't4.clinical.adt.patient.admit')
        demo_pool.complete_activity(cr, uid, admit_activity_id)
         
        # ward managers complete their activities 
        for ward_manager in demo_pool._pos['ward_manager_users']:
            activity_ids = demo_pool.get_user_activity_ids(cr, ward_manager['id'])
            for activity in activity_pool.browse(cr, uid, activity_ids):
                data = demo_pool.data_activity(cr, uid, activity.data_model)
                activity_pool.submit(cr, ward_manager['id'], activity.id, data)
                activity_pool.complete(cr, ward_manager['id'], activity.id)
 
        # activity for specific patient
        for patient_id in demo_pool.get_current_patient_ids(cr, uid):
            demo_pool.create_activity(cr, uid, 't4.clinical.patient.observation.gcs', {}, {'patient_id': patient_id})
             
        # activity for random patient
        #demo_pool.create_activity(cr, uid, 't4.clinical.patient.observation.gcs')
         
        # nurses complete their activities 
        for nurse in demo_pool._pos['nurse_users']:
            activity_ids = demo_pool.get_user_activity_ids(cr, nurse['id'])
            for activity in activity_pool.browse(cr, uid, activity_ids):
                #data = demo_pool.data_activity(cr, uid, activity.data_model)
                demo_pool.submit_activity(cr, nurse['id'], activity.id, data)
                demo_pool.complete_activity(cr, nurse['id'], activity.id)

        
        pp(demo_pool._pos)        
        
        
        
        
        
        
        
        
        