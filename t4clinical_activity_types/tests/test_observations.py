from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from pprint import pprint as pp

from openerp import tools
from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.tests.test_base import BaseTest

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
#         register_pool = self.registry('t4.clinical.adt.patient.register')
#         patient_pool = self.registry('t4.clinical.patient')
#         admit_pool = self.registry('t4.clinical.adt.patient.admit')
#         discharge_pool = self.registry('t4.clinical.patient.discharge')
#         activity_pool = self.registry('t4.activity')
#         transfer_pool = self.registry('t4.clinical.adt.patient.transfer')
#         ews_pool = self.registry('t4.clinical.patient.observation.ews')
#         height_pool = self.registry('t4.clinical.patient.observation.height')
#         weight_pool = self.registry('t4.clinical.patient.observation.weight')
#         blood_sugar_pool = self.registry('t4.clinical.patient.observation.blood_sugar')
#         blood_product_pool = self.registry('t4.clinical.patient.observation.blood_product')
#         stools_pool = self.registry('t4.clinical.patient.observation.stools')
#         gcs_pool = self.registry('t4.clinical.patient.observation.gcs')
#         vips_pool = self.registry('t4.clinical.patient.observation.vips')
#         api = self.registry('t4.clinical.api')
#         location_pool = self.registry('t4.clinical.location')
#         pos_pool = self.registry('t4.clinical.pos')
#         user_pool = self.registry('res.users')
#         partner_pool = self.registry('res.partner')
#         imd_pool = self.registry('ir.model.data')
#         device_connect_pool = self.registry('t4.clinical.device.connect')
#         device_disconnect_pool = self.registry('t4.clinical.device.disconnect')
#         o2target_pool = self.registry('t4.clinical.o2level')
#         o2target_activity_pool = self.registry('t4.clinical.patient.o2target')
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
#                                                              ('data_model','=','t4.clinical.device.session')])
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
        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        config = {
              'bed_qty': 7 
        }
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.browse(cr, uid, env_id)
        pos = env.pos_id
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        nurse_user_id = api.user_map(cr,uid, group_xmlids=['group_t4clinical_nurse']).keys()[0]
        
        #Complete observation.ews
        ews_activities = api.get_activities(cr, uid, pos_ids=[pos.id], data_models=['t4.clinical.patient.observation.ews'])
        assert len(ews_activities) == env.patient_qty, "len(ews_activities) = %s, env.patient_qty = %s, pos.id = %s" % (len(ews_activities), env.patient_qty, pos.id)
        for activity in ews_activities:
            api.assign(cr, uid, activity.id, nurse_user_id)
            env_pool.submit_complete(cr, nurse_user_id, env_id, activity.id)
                
        # Complete observation.gcs  
        gcs = [env_pool.create_activity(cr, uid, env_id, 't4.clinical.patient.observation.gcs') for i in range(env.patient_qty)]
        for gcs_activity in gcs: 
            api.assign(cr, uid, gcs_activity.id, nurse_user_id)
            env_pool.submit_complete(cr, nurse_user_id, env_id, gcs_activity.id)
        # Complete observation.height
        height = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.height') for i in range(env.patient_qty)]
        # Complete observation.weight
        weight = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.weight') for i in range(env.patient_qty)]
        # Complete observation.blood_sugar
        blood_sugar = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.blood_sugar') for i in range(env.patient_qty)]
        # Complete observation.blood_product
        blood_product = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.blood_product') for i in range(env.patient_qty)]
        # Complete observation.stools
        stools = [env_pool.create_complete(cr, uid, env_id, 't4.clinical.patient.observation.stools') for i in range(env.patient_qty)]
        # cancel adt.cancel_admit
        cancel = [env_pool.create_complete(cr, adt_user_id, env_id, 't4.clinical.adt.patient.cancel_admit') for i in range(1)]
        
        for a in gcs + height + weight + blood_sugar + blood_product + stools:
            if a.patient_id.id == cancel[0].patient_id.id:
                assert a.state == 'cancelled'

    def test_gcs_observations_policy_static(self):
        #return
        cr, uid = self.cr, self.uid
        gcs_test_data = {
            'SCORE':    [   3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15],
            'CASE':     [   0,    0,    0,    1,    1,    1,    1,    2,    2,    2,    2,    3,    4],
            'EYES':     [ '1',  'C',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '4',  '4',  '4',  '4'],
            'VERBAL':   [ '1',  'T',  '1',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '5',  '5',  '5'],
            'MOTOR':    [ '1',  '2',  '2',  '2',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '5',  '6'],
        }
        
        gcs_policy = {
            'frequencies': [30, 60, 120, 240, 720],
            'notifications': [
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': False, 'frequency': False}
            ]
        }
        gcs_pool = self.registry('t4.clinical.patient.observation.gcs')
        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        activity_pool = self.registry('t4.activity')
        env_id = env_pool.create(cr, uid)
        env = env_pool.browse(cr, uid, env_id)

        # gcs
        gcs_activity = env_pool.create_complete(cr, uid, env_id,'t4.clinical.patient.observation.gcs')
        for i in range(13):
            data = {
                'eyes': gcs_test_data['EYES'][i],
                'verbal': gcs_test_data['VERBAL'][i],
                'motor': gcs_test_data['MOTOR'][i],
            }
            gcs_activity = env_pool.submit_complete(cr, uid, env_id, gcs_activity.created_ids[0].id, data)
            frequency = gcs_policy['frequencies'][gcs_test_data['CASE'][i]]
            nurse_notifications = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['nurse']
            assessment = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['assessment']
            review_frequency = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['frequency']

            print "TEST - observation GCS: expecting score %s, frequency %s" % (gcs_test_data['SCORE'][i], frequency)
            
            # # # # # # # # # # # # # # # # #
            # Check the score and frequency #
            # # # # # # # # # # # # # # # # #
            self.assertEqual(gcs_activity.data_ref.score, gcs_test_data['SCORE'][i], msg='Score not matching')
            domain = [
                ('creator_id', '=', gcs_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', gcs_pool._name)]
            gcs_activity_ids = activity_pool.search(cr, uid, domain)
            self.assertTrue(gcs_activity_ids, msg='Next GCS activity was not triggered')
            next_gcs_activity = activity_pool.browse(cr, uid, gcs_activity_ids[0])
            self.assertEqual(next_gcs_activity.data_ref.frequency, frequency, msg='Frequency not matching')
        

    def test_ews_observations_policy_static(self):
        #return
        cr, uid = self.cr, self.uid
        ews_test_data = {
            'SCORE':    [   0,    1,    2,    3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15,   16,   17,    3,    4,   20],
            'CASE':     [   0,    1,    1,    1,    1,    2,    2,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    2,    2,    3],
            'RR':       [  18,   11,   11,   11,   11,   11,   24,   24,   24,   24,   25,   25,   25,   25,   25,   25,   24,   25,   18,   11,   25],
            'O2':       [  99,   97,   95,   95,   95,   95,   95,   93,   93,   93,   93,   91,   91,   91,   91,   91,   91,   91,   99,   99,   91],
            'O2_flag':  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    1,    0,    0,    1],
            'BT':       [37.5, 36.5, 36.5, 36.0, 36.0, 36.0, 38.5, 38.5, 38.5, 38.5, 38.5, 35.5, 39.5, 35.0, 35.0, 35.0, 35.0, 35.0, 37.5, 37.5, 35.0],
            'BPS':      [ 120,  115,  115,  115,  110,  110,  110,  110,  100,  100,  100,  100,  100,  100,   90,  220,  220,  220,  120,  120,  220],
            'BPD':      [  80,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   80,   80,   70],
            'PR':       [  65,   55,   55,   55,   55,   50,  110,   50,   50,  130,  130,  130,  130,  130,  130,  135,  135,  135,   65,   65,  135],
            'AVPU':     [ 'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'V',  'P',  'U']
        }
        ews_policy = {
            'frequencies': [720, 240, 60, 30],
            'risk': ['None', 'Low', 'Medium', 'High'],
            'notifications': [
                {'nurse': [], 'assessment': False, 'frequency': False},
                {'nurse': [], 'assessment': True, 'frequency': False},
                {'nurse': ['Urgently inform medical team'], 'assessment': False, 'frequency': False},
                {'nurse': ['Immediately inform medical team'], 'assessment': False, 'frequency': False}
            ]
        }

        env_pool = self.registry('t4.clinical.demo.env')
        api = self.registry('t4.clinical.api')
        activity_pool = self.registry('t4.activity')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        env_id = env_pool.create(cr, uid)
        env = env_pool.browse(cr, uid, env_id)
        # ews
        ews_activity = api.get_activities(cr, uid, 
                                               pos_ids=[env.pos_id.id], 
                                               data_models=['t4.clinical.patient.observation.ews'],
                                               states=['new','scheduled','started'])[0]
        for i in range(21):
            
            data={
                'respiration_rate': ews_test_data['RR'][i],
                'indirect_oxymetry_spo2': ews_test_data['O2'][i],
                'oxygen_administration_flag': ews_test_data['O2_flag'][i],
                'body_temperature': ews_test_data['BT'][i],
                'blood_pressure_systolic': ews_test_data['BPS'][i],
                'blood_pressure_diastolic': ews_test_data['BPD'][i],
                'pulse_rate': ews_test_data['PR'][i],
                'avpu_text': ews_test_data['AVPU'][i]
            }
            nurse_user_id = api.user_map(cr,uid, group_xmlids=['group_t4clinical_nurse']).keys()[0]

            # completion must be made as nurse user, otherwise notifications are not created
            api.assign(cr, uid, ews_activity.id, nurse_user_id)
            ews_activity = api.submit_complete(cr, nurse_user_id, ews_activity.id, data)
            
            frequency = ews_policy['frequencies'][ews_test_data['CASE'][i]]
            clinical_risk = ews_policy['risk'][ews_test_data['CASE'][i]]
            nurse_notifications = ews_policy['notifications'][ews_test_data['CASE'][i]]['nurse']
            assessment = ews_policy['notifications'][ews_test_data['CASE'][i]]['assessment']
            review_frequency = ews_policy['notifications'][ews_test_data['CASE'][i]]['frequency']

            print "TEST - observation EWS: expecting score %s, frequency %s, risk %s" % (ews_test_data['SCORE'][i], frequency, clinical_risk)


            # # # # # # # # # # # # # # # # # # # # # # # # #
            # Check the score, frequency and clinical risk  #
            # # # # # # # # # # # # # # # # # # # # # # # # #
            #import pdb; pdb.set_trace()
            self.assertEqual(ews_activity.data_ref.score, ews_test_data['SCORE'][i], msg='Score not matching')
            self.assertEqual(ews_activity.data_ref.clinical_risk, clinical_risk, msg='Risk not matching')
            domain = [
                ('creator_id', '=', ews_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', ews_pool._name)]
            ews_activity_ids = activity_pool.search(cr, uid, domain)
            self.assertTrue(ews_activity_ids, msg='Next EWS activity was not triggered')
            next_ews_activity = activity_pool.browse(cr, uid, ews_activity_ids[0])
            self.assertEqual(next_ews_activity.data_ref.frequency, frequency, msg='Frequency not matching')

            # # # # # # # # # # # # # # # #
            # Check notification triggers #
            # # # # # # # # # # # # # # # #
            domain = [
                ('creator_id', '=', ews_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 't4.clinical.notification.assessment')]
            assessment_ids = activity_pool.search(cr, uid, domain)
            
            if assessment:
                self.assertTrue(assessment_ids, msg='Assessment notification not triggered')
                activity_pool.complete(cr, uid, assessment_ids[0])
                domain = [
                    ('creator_id', '=', assessment_ids[0]),
                    ('state', 'not in', ['completed', 'cancelled']),
                    ('data_model', '=', 't4.clinical.notification.frequency')]
                frequency_ids = activity_pool.search(cr, uid, domain)
                self.assertTrue(frequency_ids, msg='Review frequency not triggered after Assessment complete')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(assessment_ids, msg='Assessment notification triggered')

            domain = [
                ('creator_id', '=', ews_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 't4.clinical.notification.frequency')]
            frequency_ids = activity_pool.search(cr, uid, domain)
            if review_frequency:
                self.assertTrue(frequency_ids, msg='Review frequency notification not triggered')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(frequency_ids, msg='Review frequency notification triggered')

            ews_activity = api.get_activities(cr, uid, pos_ids=[env.pos_id.id], 
                                                   data_models=['t4.clinical.patient.observation.ews'],
                                                   states=['new','scheduled','started'])[0]