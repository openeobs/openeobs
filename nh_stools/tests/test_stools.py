from openerp.tests import common

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


# class ActivityTypesTest(BaseTest):    
#     def setUp(self):
#         global cr, uid, \
#                register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool, \
#                activity_id, api, location_pool, pos_pool, user_pool, imd_pool, discharge_pool, \
#                device_connect_pool, device_disconnect_pool, partner_pool, height_pool, blood_sugar_pool, \
#                blood_product_pool, weight_pool, stools_pool, gcs_pool, vips_pool, o2target_pool, o2target_activity_pool
#          
#         cr, uid = self.cr, self.uid
#  
#         register_pool = self.registry('nh.clinical.adt.patient.register')
#         patient_pool = self.registry('nh.clinical.patient')
#         admit_pool = self.registry('nh.clinical.adt.patient.admit')
#         discharge_pool = self.registry('nh.clinical.patient.discharge')
#         activity_pool = self.registry('nh.activity')
#         transfer_pool = self.registry('nh.clinical.adt.patient.transfer')
#         ews_pool = self.registry('nh.clinical.patient.observation.ews')
#         height_pool = self.registry('nh.clinical.patient.observation.height')
#         weight_pool = self.registry('nh.clinical.patient.observation.weight')
#         blood_sugar_pool = self.registry('nh.clinical.patient.observation.blood_sugar')
#         blood_product_pool = self.registry('nh.clinical.patient.observation.blood_product')
#         stools_pool = self.registry('nh.clinical.patient.observation.stools')
#         gcs_pool = self.registry('nh.clinical.patient.observation.gcs')
#         vips_pool = self.registry('nh.clinical.patient.observation.vips')
#         api = self.registry('nh.clinical.api')
#         location_pool = self.registry('nh.clinical.location')
#         pos_pool = self.registry('nh.clinical.pos')
#         user_pool = self.registry('res.users')
#         partner_pool = self.registry('res.partner')
#         imd_pool = self.registry('ir.model.data')
#         device_connect_pool = self.registry('nh.clinical.device.connect')
#         device_disconnect_pool = self.registry('nh.clinical.device.disconnect')
#         o2target_pool = self.registry('nh.clinical.o2level')
#         o2target_activity_pool = self.registry('nh.clinical.patient.o2target')
#  
#         super(ActivityTypesTest, self).setUp()         
# 
#  
#     def device_connect(self, activity_vals={}, data_vals={}, env={}):
#         data = {}
#         device_id = data_vals.get('device_id') \
#                      or env['device_ids'][fake.random_int(min=0, max=len(env['device_ids'])-1)]
#         patient_id = data_vals.get('patient_id') \
#                      or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)] 
#         spell_activity_id = api.get_patient_spell_activity_id(cr, uid, patient_id)
#         # Create
#         connect_activity_id = device_connect_pool.create_activity(cr, uid, {'parent_id': spell_activity_id},
#                                                                   {
#                                                                    'patient_id': patient_id,
#                                                                    'device_id': device_id
#                                                                    })
#         # Complete
#         activity_pool.complete(cr, uid, connect_activity_id)   
#  
#         connect_activity = activity_pool.browse(cr, uid, connect_activity_id)
#         self.assertTrue(connect_activity.state == 'completed',
#                        "connect_activity.state != 'completed' after completion!")
#         session_activity_id = activity_pool.search(cr, uid, [('creator_id','=',connect_activity.id),
#                                                              ('data_model','=','nh.clinical.device.session')])
#         session_activity_id = session_activity_id and session_activity_id[0]
#         self.assertTrue(session_activity_id,
#                        "session activity not found after device.connect completion!")        
#         session_activity = activity_pool.browse(cr, uid, session_activity_id)
#         self.assertTrue(session_activity.patient_id.id == session_activity.patient_id.id,
#                        "session.patient_id != connect.patient_id!")         
#         self.assertTrue(session_activity.device_id.id == session_activity.device_id.id,
#                        "session.device_id != connect.device_id!")  
#  
#         return connect_activity_id          
#                 
#     def device_disconnect(self, activity_vals={}, data_vals={}, env={}):
#         data = {}
#         device_id = data_vals.get('device_id') \
#                      or env['device_ids'][fake.random_int(min=0, max=len(env['device_ids'])-1)]
#         patient_id = data_vals.get('patient_id') \
#                      or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)] 
#         spell_activity_id = api.get_patient_spell_activity_id(cr, uid, patient_id)
#         # Create
#         disconnect_activity_id = device_disconnect_pool.create_activity(cr, uid, {'parent_id': spell_activity_id},
#                                                                   {
#                                                                    'patient_id': patient_id,
#                                                                    'device_id': device_id
#                                                                    })
#         # Complete
#         session_activity_id = api.get_device_session_activity_id(cr, uid, device_id)
#         activity_pool.complete(cr, uid, disconnect_activity_id)   
#         session_activity = activity_pool.browse(cr, uid, session_activity_id)
#         self.assertTrue(session_activity.state == 'completed',
#                        "session_activity.state != 'completed' after device.disconnect completion!")  
#         return disconnect_activity_id
#      
# 
#  
#     def o2target(self, activity_vals={}, data_vals={}, env={}):
#         patient_id = data_vals.get('patient_id') \
#                      or env['patient_ids'][fake.random_int(min=0, max=len(env['patient_ids'])-1)]
#         o2target_ids = o2target_pool.search(cr, uid, [])
#         o2level_id = data_vals.get('level_id') or fake.random_element(o2target_ids) if o2target_ids else False
#         if not o2level_id:
#             return False
#         spell_activity_id = api.get_patient_spell_activity_id(cr, uid, patient_id)
#         o2target_activity_id = o2target_activity_pool.create_activity(cr, uid, {'parent_id': spell_activity_id}, {'level_id': o2level_id, 'patient_id': patient_id})
#         activity_pool.complete(cr, uid, o2target_activity_id)
#         return o2target_activity_id

class test_observations(common.SingleTransactionCase):

    def setUp(self):
        super(test_observations, self).setUp()

    def test_no_policy_obs_and_adt_cancel(self):
        #return
        cr, uid = self.cr, self.uid
        env_pool = self.registry('nh.clinical.demo.env')
        api = self.registry('nh.clinical.api')
        config = {
              'bed_qty': 7 
        }
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
        pos = env.pos_id
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        nurse_user_id = api.user_map(cr,uid, group_xmlids=['group_nhc_nurse']).keys()[0]
        
        # Complete observation.stools
        stools = [env_pool.create_complete(cr, uid, env_id, 'nh.clinical.patient.observation.stools') for i in range(env.patient_qty)]
        # cancel adt.cancel_admit
        cancel = [env_pool.create_complete(cr, adt_user_id, env_id, 'nh.clinical.adt.patient.cancel_admit') for i in range(1)]
        
        for a in stools:
            if a.patient_id.id == cancel[0].patient_id.id:
                assert a.state == 'cancelled'
