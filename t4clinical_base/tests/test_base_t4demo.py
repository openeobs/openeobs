from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv

import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)


class test_base_t4demo(SingleTransactionCase):
    @classmethod
    def tearDownClass(cls):
        if config['test_commit']:
            cls.cr.commit()
            print "COMMIT"
        else:
            cls.cr.rollback()
            print "ROLLBACK"
        cls.cr.close()
        #import pdb; pdb.set_trace()

    def setUp(self):
        global cr, uid, seed
        global patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
    
        cr, uid = self.cr, self.uid
              
        patient_pool = self.registry('t4.clinical.patient')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        activity_pool = self.registry('t4.activity')
        user_pool = self.registry('res.users')
        imd_pool = self.registry('ir.model.data')
        device_type_pool = self.registry('t4.clinical.device.type')
        device_pool = self.registry('t4.clinical.device')
        super(test_base_t4demo, self).setUp()
        
    def test_user(self):
        global cr, uid, seed
        global patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
        print "TEST res.users"
        user_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_hca'})
        user_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_nurse'})
        user_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_ward_manager'})
        user_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_doctor'})
        user_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_adt'})
        
    def test_location(self):
        global cr, uid, seed
        global patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
        print "TEST t4.clinical.location"
        pos_location_id = location_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_pos'})
        location_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_discharge'})
        location_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_admission'})
        ward_location_id = location_pool.create(cr, uid, {'parent_id': pos_location_id}, {'demo': True, 'demo_method': 'demo_values_ward'})
        location_pool.create(cr, uid, {'parent_id': ward_location_id}, {'demo': True, 'demo_method': 'demo_values_bed'})
        
    def test_patient(self):
        global cr, uid, seed
        global patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
        print "TEST t4.clinical.patient"
        patient_pool.create(cr, uid, {}, {'demo': True})        
        
    def test_pos(self):
        global cr, uid, seed
        global patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
        print "TEST t4.clinical.pos"
        pos_location_id = location_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_pos'})
        pos_pool.create(cr, uid, {'location_id': pos_location_id}, {'demo': True})  

    def test_device(self):
        global cr, uid, seed
        global patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
        print "TEST t4.clinical.device and type"
        device_type_id = device_type_pool.create(cr, uid, {}, {'demo': True})
        device_pool.create(cr, uid, {'type_id': device_type_id}, {'demo': True})  



        