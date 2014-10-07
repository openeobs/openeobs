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
        super(test_observations, self).setUp()

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
        gcs_pool = self.registry('nh.clinical.patient.observation.gcs')
        env_pool = self.registry('nh.clinical.demo.env')
        api = self.registry('nh.clinical.api')
        activity_pool = self.registry('nh.activity')
        env_id = env_pool.create(cr, uid)
        env = env_pool.browse(cr, uid, env_id)

        # gcs
        gcs_activity = env_pool.create_complete(cr, uid, env_id,'nh.clinical.patient.observation.gcs')
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
        