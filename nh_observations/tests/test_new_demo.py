from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv

import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)


class test_activity_types_nhdemo(SingleTransactionCase):
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
        global cr, uid
        cr, uid = self.cr, self.uid
        
        super(test_activity_types_nhdemo, self).setUp()
        
#     def test_adt(self):
#         global cr, uid, seed
#         api = self.registry('nh.clinical.api')
#         api_demo = self.registry('nh.clinical.api.demo')
#         
#         api_demo.build_uat_pos(cr, uid)
        
        
#         pos_id = api_demo.create(cr, uid, 'nh.clinical.pos')  
#         adt_uid = api_demo.create(cr, uid, 'res.users', 'user_adt', {'pos_id': pos_id})
#         register_activity_id = api_demo.create_activity(cr, adt_uid, 'nh.clinical.adt.patient.register')
#         register_data = api.get_activity_data(cr, uid, register_activity_id)
#         
#         ward_location_id = api_demo.create(cr, uid, 'nh.clinical.location', 'location_ward', {'pos_id': pos_id})
#         ward_location = api.location_map(cr, uid, location_ids=[ward_location_id])[ward_location_id]
#         
#         admit_activity_id = api_demo.create_activity(cr, adt_uid, 'nh.clinical.adt.patient.admit')
#         
#         api.complete(cr, adt_uid, admit_activity_id)
# 
#         admit_data = api.get_activity_data(cr, uid, admit_activity_id)
#         patient_id = admit_data['patient_id']
#         placement_activity_id = api.activity_map(cr, uid, 
#                                                  data_models=['nh.clinical.patient.placement'], 
#                                                  patient_ids=[patient_id], pos_ids=[pos_id],
#                                                  states=['new', 'scheduled']).keys()[0]
#         
#         bed_location_id = api_demo.create(cr, uid, 'nh.clinical.location', 'location_bed', {'patent_id': ward_location_id})
#         api.submit_complete(cr, uid, placement_activity_id, {'location_id': bed_location_id})
        
                                                 
    def test_observations(self):
        global cr, uid, seed 
    
