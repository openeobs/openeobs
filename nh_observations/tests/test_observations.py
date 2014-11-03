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


class test_observations(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(test_observations, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.api_pool = cls.registry('nh.clinical.api')
        
        # OBSERVATIONS DATA MODELS
        cls.height_pool = cls.registry('nh.clinical.patient.observation.height')
        cls.weight_pool = cls.registry('nh.clinical.patient.observation.weight')
        cls.blood_sugar_pool = cls.registry('nh.clinical.patient.observation.blood_sugar')
        cls.blood_product_pool = cls.registry('nh.clinical.patient.observation.blood_product')
        # PARAMETERS DATA MODELS
        cls.mrsa_pool = cls.registry('nh.clinical.patient.mrsa')
        cls.diabetes_pool = cls.registry('nh.clinical.patient.diabetes')
        cls.weight_monitoring_pool = cls.registry('nh.clinical.patient.weight_monitoring')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.apidemo.build_unit_test_env(cr, uid, bed_count=4, patient_placement_count=2)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]

    def test_basic_observations(self):
        cr, uid = self.cr, self.uid
        
        patient_ids = self.patient_pool.search(cr, uid, [['current_location_id.usage', '=', 'bed'], ['current_location_id.parent_id', 'in', [self.wu_id, self.wt_id]]])
        self.assertTrue(patient_ids, msg="Test set up Failed. No placed patients found")
        patient_id = fake.random_element(patient_ids)
        spell_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.spell'], ['patient_id', '=', patient_id]])
        self.assertTrue(spell_ids, msg="Test set up Failed. No spell found for the patient")
        spell_activity = self.activity_pool.browse(cr, uid, spell_ids[0])
        user_id = False
        if self.nu_id in [user.id for user in spell_activity.user_ids]:
            user_id = self.nu_id
        else:
            user_id = self.nt_id
        
        # Height Observation
        height_data = {
            'height': float(fake.random_int(min=100, max=220))/100.0
        }        
        height_activity_id = self.height_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, height_activity_id, height_data)
        check_height = self.activity_pool.browse(cr, user_id, height_activity_id)
        
        self.assertTrue(check_height.summary == self.height_pool._description, msg="Height Observation: Activity summary not submitted correctly")
        self.assertTrue(check_height.data_ref.patient_id.id == patient_id, msg="Height Observation: Patient id not submitted correctly")
        height = self.height_pool.read(cr, uid, check_height.data_ref.id, ['height'])['height']
        self.assertTrue(height == height_data['height'], msg="Height Observation: Height not submitted correctly - Read comparison")
        # self.assertTrue(check_height.data_ref.height == height_data['height'], msg="Height Observation: Height not submitted correctly")
        self.activity_pool.complete(cr, user_id, height_activity_id)
        check_height = self.activity_pool.browse(cr, user_id, height_activity_id)
        self.assertTrue(check_height.state == 'completed', msg="Height Observation Completed: State not updated")
        self.assertTrue(check_height.date_terminated, msg="Height Observation Completed: Date terminated not updated")
        self.assertFalse(check_height.data_ref.is_partial, msg="Height Observation Completed: Partial status incorrect")
        
        # Weight Observation
        weight_data = {
            'weight': float(fake.random_int(min=400, max=1200))/10.0
        }        
        weight_activity_id = self.weight_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, weight_activity_id, weight_data)
        check_weight = self.activity_pool.browse(cr, user_id, weight_activity_id)
        
        self.assertTrue(check_weight.summary == self.weight_pool._description, msg="Weight Observation: Activity summary not submitted correctly")
        self.assertTrue(check_weight.data_ref.patient_id.id == patient_id, msg="Weight Observation: Patient id not submitted correctly")
        weight = self.weight_pool.read(cr, uid, check_weight.data_ref.id, ['weight'])['weight']
        self.assertTrue(weight == weight_data['weight'], msg="Weight Observation: Weight not submitted correctly - Read comparison")
        # self.assertTrue(check_weight.data_ref.weight == weight_data['weight'], msg="Weight Observation: weight not submitted correctly")
        self.activity_pool.complete(cr, user_id, weight_activity_id)
        check_weight = self.activity_pool.browse(cr, user_id, weight_activity_id)
        self.assertTrue(check_weight.state == 'completed', msg="Weight Observation Completed: State not updated")
        self.assertTrue(check_weight.date_terminated, msg="Weight Observation Completed: Date terminated not updated")
        self.assertFalse(check_weight.data_ref.is_partial, msg="Weight Observation Completed: Partial status incorrect")
        
        # Blood Sugar Observation
        blood_sugar_data = {
            'blood_sugar': float(fake.random_int(min=10, max=999))/10.0
        }        
        blood_sugar_activity_id = self.blood_sugar_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, blood_sugar_activity_id, blood_sugar_data)
        check_blood_sugar = self.activity_pool.browse(cr, user_id, blood_sugar_activity_id)

        self.assertTrue(check_blood_sugar.summary == self.blood_sugar_pool._description, msg="Blood Sugar Observation: Activity summary not submitted correctly")
        self.assertTrue(check_blood_sugar.data_ref.patient_id.id == patient_id, msg="Blood Sugar Observation: Patient id not submitted correctly")
        blood_sugar = self.blood_sugar_pool.read(cr, uid, check_blood_sugar.data_ref.id, ['blood_sugar'])['blood_sugar']
        self.assertTrue(blood_sugar == blood_sugar_data['blood_sugar'], msg="Blood Sugar Observation: Blood Sugar not submitted correctly - Read comparison")
        # self.assertTrue(check_blood_sugar.data_ref.blood_sugar == blood_sugar_data['blood_sugar'], msg="Blood Sugar Observation: Blood Sugar not submitted correctly")
        self.activity_pool.complete(cr, user_id, blood_sugar_activity_id)
        check_blood_sugar = self.activity_pool.browse(cr, user_id, blood_sugar_activity_id)
        self.assertTrue(check_blood_sugar.state == 'completed', msg="Blood Sugar Observation Completed: State not updated")
        self.assertTrue(check_blood_sugar.date_terminated, msg="Blood Sugar Observation Completed: Date terminated not updated")
        self.assertFalse(check_blood_sugar.data_ref.is_partial, msg="Blood Sugar Observation Completed: Partial status incorrect")
        
        # Blood Product Observation
        blood_product_data = {
            'vol': float(fake.random_int(min=1, max=100000))/10.0,
            'product': fake.random_element(self.blood_product_pool._blood_product_values)[0]
        }        
        blood_product_activity_id = self.blood_product_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, blood_product_activity_id, blood_product_data)
        check_blood_product = self.activity_pool.browse(cr, user_id, blood_product_activity_id)
        
        self.assertTrue(check_blood_product.summary == self.blood_product_pool._description, msg="Blood Product Observation: Activity summary not submitted correctly")
        self.assertTrue(check_blood_product.data_ref.patient_id.id == patient_id, msg="Blood Product Observation: Patient id not submitted correctly")
        self.assertTrue(check_blood_product.data_ref.product == blood_product_data['product'], msg="Blood Product Observation: Blood Product not submitted correctly")
        blood_product = self.blood_product_pool.read(cr, uid, check_blood_product.data_ref.id, ['vol'])['vol']
        self.assertTrue(blood_product == blood_product_data['vol'], msg="Blood Product Observation: volume not submitted correctly - Read comparison")
        # self.assertTrue(check_blood_product.data_ref.vol == blood_product_data['vol'], msg="Blood Product Observation: Blood Product volume not submitted correctly")
        self.activity_pool.complete(cr, user_id, blood_product_activity_id)
        check_blood_product = self.activity_pool.browse(cr, user_id, blood_product_activity_id)
        self.assertTrue(check_blood_product.state == 'completed', msg="Blood Product Observation Completed: State not updated")
        self.assertTrue(check_blood_product.date_terminated, msg="Blood Product Observation Completed: Date terminated not updated")
        self.assertFalse(check_blood_product.data_ref.is_partial, msg="Blood Product Observation Completed: Partial status incorrect")
            
    def test_parameters(self):
        cr, uid = self.cr, self.uid
        
        patient_ids = self.patient_pool.search(cr, uid, [['current_location_id.usage', '=', 'bed'], ['current_location_id.parent_id', 'in', [self.wu_id, self.wt_id]]])
        self.assertTrue(patient_ids, msg="Test set up Failed. No placed patients found")
        patient_id = fake.random_element(patient_ids)
        spell_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.spell'], ['patient_id', '=', patient_id]])
        self.assertTrue(spell_ids, msg="Test set up Failed. No spell found for the patient")
        spell_activity = self.activity_pool.browse(cr, uid, spell_ids[0])
        user_id = False
        if self.wmu_id in [user.id for user in spell_activity.user_ids]:
            user_id = self.wmu_id
        else:
            user_id = self.wmt_id
        
        # MRSA parameter
        mrsa_data = {
            'mrsa': fake.random_element([True, False])
        }        
        mrsa_activity_id = self.mrsa_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, mrsa_activity_id, mrsa_data)
        check_mrsa = self.activity_pool.browse(cr, user_id, mrsa_activity_id)

        self.assertTrue(check_mrsa.data_ref.patient_id.id == patient_id, msg="MRSA Parameter: Patient id not submitted correctly")
        self.assertTrue(check_mrsa.data_ref.mrsa == mrsa_data['mrsa'], msg="MRSA Parameter: MRSA not submitted correctly")
        self.activity_pool.complete(cr, user_id, mrsa_activity_id)
        check_mrsa = self.activity_pool.browse(cr, user_id, mrsa_activity_id)
        self.assertTrue(check_mrsa.state == 'completed', msg="MRSA Parameter Completed: State not updated")
        self.assertTrue(check_mrsa.date_terminated, msg="MRSA Parameter Completed: Date terminated not updated")
        
        # Diabetes parameter
        diabetes_data = {
            'diabetes': fake.random_element([True, False])
        }        
        diabetes_activity_id = self.diabetes_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, diabetes_activity_id, diabetes_data)
        check_diabetes = self.activity_pool.browse(cr, user_id, diabetes_activity_id)

        self.assertTrue(check_diabetes.data_ref.patient_id.id == patient_id, msg="Diabetes Parameter: Patient id not submitted correctly")
        self.assertTrue(check_diabetes.data_ref.diabetes == diabetes_data['diabetes'], msg="Diabetes Parameter: Diabetes not submitted correctly")
        self.activity_pool.complete(cr, user_id, diabetes_activity_id)
        check_diabetes = self.activity_pool.browse(cr, user_id, diabetes_activity_id)
        self.assertTrue(check_diabetes.state == 'completed', msg="Diabetes Parameter Completed: State not updated")
        self.assertTrue(check_diabetes.date_terminated, msg="Diabetes Parameter Completed: Date terminated not updated")
        
        # Weight Monitoring parameter
        weight_monitoring_data = {
            'weight_monitoring': fake.random_element([True, False])
        }        
        weight_monitoring_activity_id = self.weight_monitoring_pool.create_activity(cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, weight_monitoring_activity_id, weight_monitoring_data)
        check_weight_monitoring = self.activity_pool.browse(cr, user_id, weight_monitoring_activity_id)

        self.assertTrue(check_weight_monitoring.data_ref.patient_id.id == patient_id, msg="Weight Monitoring Parameter: Patient id not submitted correctly")
        self.assertTrue(check_weight_monitoring.data_ref.weight_monitoring == weight_monitoring_data['weight_monitoring'], msg="Weight Monitoring Parameter: Weight Monitoring not submitted correctly")
        self.activity_pool.complete(cr, user_id, weight_monitoring_activity_id)
        check_weight_monitoring = self.activity_pool.browse(cr, user_id, weight_monitoring_activity_id)
        self.assertTrue(check_weight_monitoring.state == 'completed', msg="Weight Monitoring Parameter Completed: State not updated")
        self.assertTrue(check_weight_monitoring.date_terminated, msg="Weight Monitoring Parameter Completed: Date terminated not updated")
        scheduled_weight_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.weight'], ['patient_id', '=', patient_id], ['state', '=', 'scheduled']])
        self.assertTrue(bool(scheduled_weight_ids) == weight_monitoring_data['weight_monitoring'], msg="Weight Monitoring Parameter Completed: Weight Observation trigger failure")
        
    # def test_gcs_observations_policy_static(self):
    #     cr, uid = self.cr, self.uid
    #     gcs_test_data = {
    #         'SCORE':    [   3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15],
    #         'CASE':     [   0,    0,    0,    1,    1,    1,    1,    2,    2,    2,    2,    3,    4],
    #         'EYES':     [ '1',  'C',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '4',  '4',  '4',  '4'],
    #         'VERBAL':   [ '1',  'T',  '1',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '5',  '5',  '5'],
    #         'MOTOR':    [ '1',  '2',  '2',  '2',  '2',  '2',  '3',  '3',  '3',  '4',  '4',  '5',  '6'],
    #     }
    #     
    #     gcs_policy = {
    #         'frequencies': [30, 60, 120, 240, 720],
    #         'notifications': [
    #             {'nurse': [], 'assessment': False, 'frequency': False},
    #             {'nurse': [], 'assessment': False, 'frequency': False},
    #             {'nurse': [], 'assessment': False, 'frequency': False},
    #             {'nurse': [], 'assessment': False, 'frequency': False},
    #             {'nurse': [], 'assessment': False, 'frequency': False}
    #         ]
    #     }
    #     gcs_pool = self.registry('nh.clinical.patient.observation.gcs')
    #     env_pool = self.registry('nh.clinical.demo.env')
    #     api = self.registry('nh.clinical.api')
    #     activity_pool = self.registry('nh.activity')
    #     env_id = env_pool.create(cr, uid)
    #     env_pool.build(cr, uid, env_id)
    #     env = env_pool.browse(cr, uid, env_id)
    # 
    #     # gcs
    #     gcs_activity = env_pool.create_complete(cr, uid, env_id,'nh.clinical.patient.observation.gcs')
    #     for i in range(13):
    #         data = {
    #             'eyes': gcs_test_data['EYES'][i],
    #             'verbal': gcs_test_data['VERBAL'][i],
    #             'motor': gcs_test_data['MOTOR'][i],
    #         }
    #         gcs_activity = env_pool.submit_complete(cr, uid, env_id, gcs_activity.created_ids[0].id, data)
    #         frequency = gcs_policy['frequencies'][gcs_test_data['CASE'][i]]
    #         nurse_notifications = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['nurse']
    #         assessment = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['assessment']
    #         review_frequency = gcs_policy['notifications'][gcs_test_data['CASE'][i]]['frequency']
    # 
    #         print "TEST - observation GCS: expecting score %s, frequency %s" % (gcs_test_data['SCORE'][i], frequency)
    #         
    #         # # # # # # # # # # # # # # # # #
    #         # Check the score and frequency #
    #         # # # # # # # # # # # # # # # # #
    #         self.assertEqual(gcs_activity.data_ref.score, gcs_test_data['SCORE'][i], msg='Score not matching')
    #         domain = [
    #             ('creator_id', '=', gcs_activity.id),
    #             ('state', 'not in', ['completed', 'cancelled']),
    #             ('data_model', '=', gcs_pool._name)]
    #         gcs_activity_ids = activity_pool.search(cr, uid, domain)
    #         self.assertTrue(gcs_activity_ids, msg='Next GCS activity was not triggered')
    #         next_gcs_activity = activity_pool.browse(cr, uid, gcs_activity_ids[0])
    #         self.assertEqual(next_gcs_activity.data_ref.frequency, frequency, msg='Frequency not matching')
        

#     def test_ews_observations_policy_static(self):
#         cr, uid = self.cr, self.uid
#         ews_test_data = {
#             'SCORE':    [   0,    1,    2,    3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15,   16,   17,    3,    4,   20],
#             'CASE':     [   0,    1,    1,    1,    1,    2,    2,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    3,    2,    2,    3],
#             'RR':       [  18,   11,   11,   11,   11,   11,   24,   24,   24,   24,   25,   25,   25,   25,   25,   25,   24,   25,   18,   11,   25],
#             'O2':       [  99,   97,   95,   95,   95,   95,   95,   93,   93,   93,   93,   91,   91,   91,   91,   91,   91,   91,   99,   99,   91],
#             'O2_flag':  [   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    1,    0,    0,    1],
#             'BT':       [37.5, 36.5, 36.5, 36.0, 36.0, 36.0, 38.5, 38.5, 38.5, 38.5, 38.5, 35.5, 39.5, 35.0, 35.0, 35.0, 35.0, 35.0, 37.5, 37.5, 35.0],
#             'BPS':      [ 120,  115,  115,  115,  110,  110,  110,  110,  100,  100,  100,  100,  100,  100,   90,  220,  220,  220,  120,  120,  220],
#             'BPD':      [  80,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   70,   80,   80,   70],
#             'PR':       [  65,   55,   55,   55,   55,   50,  110,   50,   50,  130,  130,  130,  130,  130,  130,  135,  135,  135,   65,   65,  135],
#             'AVPU':     [ 'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'A',  'V',  'P',  'U']
#         }
#         ews_policy = {
#             'frequencies': [720, 240, 60, 30],
#             'risk': ['None', 'Low', 'Medium', 'High'],
#             'notifications': [
#                 {'nurse': [], 'assessment': False, 'frequency': False},
#                 {'nurse': [], 'assessment': True, 'frequency': False},
#                 {'nurse': ['Urgently inform medical team'], 'assessment': False, 'frequency': False},
#                 {'nurse': ['Immediately inform medical team'], 'assessment': False, 'frequency': False}
#             ]
#         }
# 
#         env_pool = self.registry('nh.clinical.demo.env')
#         api = self.registry('nh.clinical.api')
#         activity_pool = self.registry('nh.activity')
#         ews_pool = self.registry('nh.clinical.patient.observation.ews')
#         env_id = env_pool.create(cr, uid)
#         env_pool.build(cr, uid, env_id)
#         env = env_pool.browse(cr, uid, env_id)
#         # ews
#         ews_activity = api.get_activities(cr, uid, 
#                                                pos_ids=[env.pos_id.id], 
#                                                data_models=['nh.clinical.patient.observation.ews'],
#                                                states=['new','scheduled','started'])[0]
#         for i in range(21):
#             
#             data={
#                 'respiration_rate': ews_test_data['RR'][i],
#                 'indirect_oxymetry_spo2': ews_test_data['O2'][i],
#                 'oxygen_administration_flag': ews_test_data['O2_flag'][i],
#                 'body_temperature': ews_test_data['BT'][i],
#                 'blood_pressure_systolic': ews_test_data['BPS'][i],
#                 'blood_pressure_diastolic': ews_test_data['BPD'][i],
#                 'pulse_rate': ews_test_data['PR'][i],
#                 'avpu_text': ews_test_data['AVPU'][i]
#             }
#             nurse_user_id = api.user_map(cr,uid, group_xmlids=['group_nhc_nurse']).keys()[0]
# 
#             # completion must be made as nurse user, otherwise notifications are not created
#             api.assign(cr, uid, ews_activity.id, nurse_user_id)
#             ews_activity = api.submit_complete(cr, nurse_user_id, ews_activity.id, data)
#             
#             frequency = ews_policy['frequencies'][ews_test_data['CASE'][i]]
#             clinical_risk = ews_policy['risk'][ews_test_data['CASE'][i]]
#             nurse_notifications = ews_policy['notifications'][ews_test_data['CASE'][i]]['nurse']
#             assessment = ews_policy['notifications'][ews_test_data['CASE'][i]]['assessment']
#             review_frequency = ews_policy['notifications'][ews_test_data['CASE'][i]]['frequency']
# 
#             print "TEST - observation EWS: expecting score %s, frequency %s, risk %s" % (ews_test_data['SCORE'][i], frequency, clinical_risk)
# 
# 
#             # # # # # # # # # # # # # # # # # # # # # # # # #
#             # Check the score, frequency and clinical risk  #
#             # # # # # # # # # # # # # # # # # # # # # # # # #
#             #import pdb; pdb.set_trace()
#             self.assertEqual(ews_activity.data_ref.score, ews_test_data['SCORE'][i], msg='Score not matching')
#             self.assertEqual(ews_activity.data_ref.clinical_risk, clinical_risk, msg='Risk not matching')
#             domain = [
#                 ('creator_id', '=', ews_activity.id),
#                 ('state', 'not in', ['completed', 'cancelled']),
#                 ('data_model', '=', ews_pool._name)]
#             ews_activity_ids = activity_pool.search(cr, uid, domain)
#             self.assertTrue(ews_activity_ids, msg='Next EWS activity was not triggered')
#             next_ews_activity = activity_pool.browse(cr, uid, ews_activity_ids[0])
#             self.assertEqual(next_ews_activity.data_ref.frequency, frequency, msg='Frequency not matching')
# 
#             # # # # # # # # # # # # # # # #
#             # Check notification triggers #
#             # # # # # # # # # # # # # # # #
#             domain = [
#                 ('creator_id', '=', ews_activity.id),
#                 ('state', 'not in', ['completed', 'cancelled']),
#                 ('data_model', '=', 'nh.clinical.notification.assessment')]
#             assessment_ids = activity_pool.search(cr, uid, domain)
#             
#             if assessment:
#                 self.assertTrue(assessment_ids, msg='Assessment notification not triggered')
#                 activity_pool.complete(cr, uid, assessment_ids[0])
#                 domain = [
#                     ('creator_id', '=', assessment_ids[0]),
#                     ('state', 'not in', ['completed', 'cancelled']),
#                     ('data_model', '=', 'nh.clinical.notification.frequency')]
#                 frequency_ids = activity_pool.search(cr, uid, domain)
#                 self.assertTrue(frequency_ids, msg='Review frequency not triggered after Assessment complete')
#                 activity_pool.cancel(cr, uid, frequency_ids[0])
#             else:
#                 self.assertFalse(assessment_ids, msg='Assessment notification triggered')
# 
#             domain = [
#                 ('creator_id', '=', ews_activity.id),
#                 ('state', 'not in', ['completed', 'cancelled']),
#                 ('data_model', '=', 'nh.clinical.notification.frequency')]
#             frequency_ids = activity_pool.search(cr, uid, domain)
#             if review_frequency:
#                 self.assertTrue(frequency_ids, msg='Review frequency notification not triggered')
#                 activity_pool.cancel(cr, uid, frequency_ids[0])
#             else:
#                 self.assertFalse(frequency_ids, msg='Review frequency notification triggered')
# 
#             ews_activity = api.get_activities(cr, uid, pos_ids=[env.pos_id.id], 
#                                                    data_models=['nh.clinical.patient.observation.ews'],
#                                                    states=['new','scheduled','started'])[0]