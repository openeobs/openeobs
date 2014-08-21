from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv

import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)


class test_activity_types_t4demo(SingleTransactionCase):
    @classmethod
    def tearDownClass(cls):
        if config['test_commit']:
            cls.cr.commit()
            print "COMMIT"
        else:
            cls.cr.rollback()
            print "ROLLBACK"
        cls.cr.close()
        import pdb; pdb.set_trace()

    def setUp(self):
        global cr, uid, seed, api
        global register_pool, admit_pool, patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
    
        cr, uid = self.cr, self.uid
        api = self.registry('t4.clinical.api')
              
        patient_pool = self.registry('t4.clinical.patient')
        location_pool = self.registry('t4.clinical.location')
        pos_pool = self.registry('t4.clinical.pos')
        activity_pool = self.registry('t4.activity')
        user_pool = self.registry('res.users')
        imd_pool = self.registry('ir.model.data')
        device_type_pool = self.registry('t4.clinical.device.type')
        device_pool = self.registry('t4.clinical.device')
        
        register_pool = self.registry('t4.clinical.adt.patient.register')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        
        super(test_activity_types_t4demo, self).setUp()
        
    def test_adt(self):
        global cr, uid, seed
        global register_pool, admit_pool, patient_pool, location_pool, pos_pool, user_pool, imd_pool, activity_pool, device_type_pool, device_pool
        print "TEST t4.clinical.adt.patient.register"
        pos_location_id = location_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_pos'})
        pos_id = pos_pool.create(cr, uid, {'location_id': pos_location_id}, {'demo': True})
        adt_uid = user_pool.create(cr, uid, {'pos_id': pos_id}, {'demo': True, 'demo_method': 'demo_values_adt'})
        reg_activity_id = register_pool.create_activity(cr, adt_uid, {}, {}, {'demo': True})
        ward_location_id = location_pool.create(cr, uid, {'parent_id': pos_location_id}, {'demo': True, 'demo_method': 'demo_values_ward'})
        assert reg_activity_id, "reg_activity_id: %s" % reg_activity_id
        print "TEST t4.clinical.adt.patient.admit"
        ward = api.location_map(cr, uid, location_ids=[ward_location_id])[ward_location_id]
        reg_data = api.get_activity_data(cr, uid, reg_activity_id)
        adm_activity_id = admit_pool.create_activity(cr, adt_uid, {}, {'location': ward['code'], 'other_identifier': reg_data['other_identifier']}, {'demo': True})
        assert adm_activity_id, "adm_activity_id: %s" % adm_activity_id
        
        
        #print "positive. reg_activity_id: %s" % reg_activity_id