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

    def setUp(self):
        placement_model = self.registry('nh.clinical.patient.placement')
        placement_model._POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews', 'type': 'recurring'}]}
        super(test_observations, self).setUp()

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

        env_pool = self.registry('nh.clinical.demo.env')
        api = self.registry('nh.clinical.api')
        activity_pool = self.registry('nh.activity')
        ews_pool = self.registry('nh.clinical.patient.observation.ews')
        env_id = env_pool.create(cr, uid)
        env_pool.build(cr, uid, env_id)
        env = env_pool.browse(cr, uid, env_id)
        # ews
        ews_activity = api.get_activities(cr, uid,
                                               pos_ids=[env.pos_id.id],
                                               data_models=['nh.clinical.patient.observation.ews'],
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
            nurse_user_id = api.user_map(cr,uid, group_xmlids=['group_nhc_nurse']).keys()[0]

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
                ('data_model', '=', 'nh.clinical.notification.assessment')]
            assessment_ids = activity_pool.search(cr, uid, domain)

            if assessment:
                self.assertTrue(assessment_ids, msg='Assessment notification not triggered')
                activity_pool.complete(cr, uid, assessment_ids[0])
                domain = [
                    ('creator_id', '=', assessment_ids[0]),
                    ('state', 'not in', ['completed', 'cancelled']),
                    ('data_model', '=', 'nh.clinical.notification.frequency')]
                frequency_ids = activity_pool.search(cr, uid, domain)
                self.assertTrue(frequency_ids, msg='Review frequency not triggered after Assessment complete')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(assessment_ids, msg='Assessment notification triggered')

            domain = [
                ('creator_id', '=', ews_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.frequency')]
            frequency_ids = activity_pool.search(cr, uid, domain)
            if review_frequency:
                self.assertTrue(frequency_ids, msg='Review frequency notification not triggered')
                activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(frequency_ids, msg='Review frequency notification triggered')

            ews_activity = api.get_activities(cr, uid, pos_ids=[env.pos_id.id],
                                                   data_models=['nh.clinical.patient.observation.ews'],
                                                   states=['new','scheduled','started'])[0]