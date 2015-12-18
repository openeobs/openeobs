# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.tests import common

import logging
from mock import MagicMock

_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class TestEWS(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestEWS, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')

        cls.placement_pool = cls.registry('nh.clinical.patient.placement')
        cls.placement_pool._POLICY = {
            'activities': [
                {'model': 'nh.clinical.patient.observation.ews',
                 'type': 'recurring'}]}
        cls.ews_pool = cls.registry('nh.clinical.patient.observation.ews')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.apidemo.build_unit_test_env(
            cr, uid, bed_count=4, patient_placement_count=2)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(
            cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(
            cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(
            cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']),
                      ('pos_id', '=', cls.pos_id)])[0]

    def test_ews_observations_policy_static(self):
        cr, uid = self.cr, self.uid
        ews_test_data = {
            'SCORE': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                      17, 3, 4, 20],
            'CASE': [0, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2,
                     2, 3],
            'RR': [18, 11, 11, 11, 11, 11, 24, 24, 24, 24, 25, 25, 25, 25, 25,
                   25, 24, 25, 18, 11, 25],
            'O2': [99, 97, 95, 95, 95, 95, 95, 93, 93, 93, 93, 91, 91, 91, 91,
                   91, 91, 91, 99, 99, 91],
            'O2_flag': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1,
                        0, 0, 1],
            'BT': [37.5, 36.5, 36.5, 36.0, 36.0, 36.0, 38.5, 38.5, 38.5, 38.5,
                   38.5, 35.5, 39.5, 35.0, 35.0, 35.0, 35.0, 35.0, 37.5, 37.5,
                   35.0],
            'BPS': [120, 115, 115, 115, 110, 110, 110, 110, 100, 100, 100, 100,
                    100, 100,  90, 220, 220, 220, 120, 120, 220],
            'BPD': [80, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70, 70,
                    70, 70, 70, 80, 80, 70],
            'PR': [65, 55, 55, 55, 55, 50, 110, 50, 50, 130, 130, 130, 130,
                   130, 130, 135, 135, 135, 65, 65, 135],
            'AVPU': ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A',
                     'A', 'A', 'A', 'A', 'A', 'A', 'A', 'V', 'P', 'U']
        }
        ews_policy = {
            'frequencies': [720, 240, 60, 30],
            'risk': ['None', 'Low', 'Medium', 'High'],
            'notifications': [
                {'medical_team': [], 'assessment': False, 'frequency': False},
                {'medical_team': [], 'assessment': True, 'frequency': False},
                {'medical_team': ['Urgently inform medical team'],
                 'assessment': False, 'frequency': False},
                {'medical_team': ['Immediately inform medical team'],
                 'assessment': False, 'frequency': False}
            ]
        }

        patient_ids = self.patient_pool.search(
            cr, uid,
            [['current_location_id.usage', '=', 'bed'],
             ['current_location_id.parent_id', 'in', [self.wu_id, self.wt_id]]
             ])
        self.assertTrue(
            patient_ids, msg="Test set up Failed. No placed patients found")
        patient_id = fake.random_element(patient_ids)
        spell_ids = self.activity_pool.search(
            cr, uid,
            [['data_model', '=', 'nh.clinical.spell'],
             ['patient_id', '=', patient_id]])
        self.assertTrue(
            spell_ids,
            msg="Test set up Failed. No spell found for the patient")
        spell_activity = self.activity_pool.browse(cr, uid, spell_ids[0])
        user_id = False
        if self.nu_id in [user.id for user in spell_activity.user_ids]:
            user_id = self.nu_id
        else:
            user_id = self.nt_id

        ews_activity_id = self.ews_pool.create_activity(
            cr, uid,
            {'parent_id': spell_activity.id},
            {'patient_id': spell_activity.patient_id.id})

        for i in range(21):

            data = {
                'respiration_rate': ews_test_data['RR'][i],
                'indirect_oxymetry_spo2': ews_test_data['O2'][i],
                'oxygen_administration_flag': ews_test_data['O2_flag'][i],
                'body_temperature': ews_test_data['BT'][i],
                'blood_pressure_systolic': ews_test_data['BPS'][i],
                'blood_pressure_diastolic': ews_test_data['BPD'][i],
                'pulse_rate': ews_test_data['PR'][i],
                'avpu_text': ews_test_data['AVPU'][i]
            }

            # completion must be made as nurse user, otherwise notifications
            # are not created
            self.activity_pool.assign(cr, uid, ews_activity_id, user_id)
            self.activity_pool.submit(cr, user_id, ews_activity_id, data)
            self.activity_pool.complete(cr, user_id, ews_activity_id)
            ews_activity = self.activity_pool.browse(cr, uid, ews_activity_id)

            self.assertEqual(self.ews_pool.get_last_case(
                cr, uid, spell_activity.patient_id.id),
                ews_test_data['CASE'][i])

            frequency = ews_policy['frequencies'][ews_test_data['CASE'][i]]
            clinical_risk = ews_policy['risk'][ews_test_data['CASE'][i]]
            nurse_notifications = ews_policy['notifications'][
                ews_test_data['CASE'][i]]['medical_team']
            assessment = ews_policy['notifications'][
                ews_test_data['CASE'][i]]['assessment']
            review_frequency = ews_policy['notifications'][
                ews_test_data['CASE'][i]]['frequency']

            # # # # # # # # # # # # # # # # # # # # # # # # #
            # Check the score, frequency and clinical risk  #
            # # # # # # # # # # # # # # # # # # # # # # # # #
            self.assertEqual(
                ews_activity.data_ref.score,
                ews_test_data['SCORE'][i], msg='Score not matching')
            self.assertEqual(
                ews_activity.data_ref.clinical_risk,
                clinical_risk, msg='Risk not matching')
            domain = [
                ('creator_id', '=', ews_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', self.ews_pool._name)]
            ews_activity_ids = self.activity_pool.search(cr, uid, domain)
            self.assertTrue(
                ews_activity_ids, msg='Next EWS activity was not triggered')
            next_ews_activity = self.activity_pool.browse(
                cr, uid, ews_activity_ids[0])
            self.assertEqual(
                next_ews_activity.data_ref.frequency, frequency,
                msg='Frequency not matching')

            # # # # # # # # # # # # # # # #
            # Check notification triggers #
            # # # # # # # # # # # # # # # #
            domain = [
                ('creator_id', '=', ews_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.assessment')]
            assessment_ids = self.activity_pool.search(cr, uid, domain)

            if assessment:
                self.assertTrue(
                    assessment_ids,
                    msg='Assessment notification not triggered')
                self.activity_pool.complete(cr, uid, assessment_ids[0])
                domain = [
                    ('creator_id', '=', assessment_ids[0]),
                    ('state', 'not in', ['completed', 'cancelled']),
                    ('data_model', '=', 'nh.clinical.notification.frequency')]
                frequency_ids = self.activity_pool.search(cr, uid, domain)
                self.assertTrue(
                    frequency_ids,
                    msg='Review frequency not triggered after Assessment '
                        'complete')
                self.activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(
                    assessment_ids, msg='Assessment notification triggered')

            domain = [
                ('creator_id', '=', ews_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.notification.frequency')]
            frequency_ids = self.activity_pool.search(cr, uid, domain)
            if review_frequency:
                self.assertTrue(
                    frequency_ids,
                    msg='Review frequency notification not triggered')
                self.activity_pool.cancel(cr, uid, frequency_ids[0])
            else:
                self.assertFalse(
                    frequency_ids,
                    msg='Review frequency notification triggered')

            if nurse_notifications:
                for n in nurse_notifications:
                    domain = [
                        ('creator_id', '=', ews_activity.id),
                        ('state', 'not in', ['completed', 'cancelled']),
                        ('data_model', '=',
                         'nh.clinical.notification.medical_team'),
                        ('summary', '=', n)]
                    nurse_not_ids = self.activity_pool.search(cr, uid, domain)
                    self.assertTrue(
                        nurse_not_ids,
                        msg='Nurse notification %s not triggered' % n)
                    self.activity_pool.cancel(cr, uid, nurse_not_ids[0])
            else:
                domain = [
                    ('creator_id', '=', ews_activity.id),
                    ('state', 'not in', ['completed', 'cancelled']),
                    ('data_model', '=',
                     'nh.clinical.notification.medical_team')]
                nurse_not_ids = self.activity_pool.search(cr, uid, domain)
                self.assertFalse(
                    nurse_not_ids,
                    msg='Nurse notification triggered')
            ews_activity_id = next_ews_activity.id

    def test_get_score_display_when_ews_is_partials_returns_empty_string(self):
        cr, uid = self.cr, self.uid
        ews_mock = MagicMock(spec=self.ews_pool.__class__.__name__)
        return_value = [
            ews_mock._get_child_mock(id=1, is_partial=True),
        ]
        self.ews_pool.browse = MagicMock(return_value=return_value)

        result = self.ews_pool._get_score_display(
            cr, uid, 2, None, None, context=None
        )
        self.assertEquals(result.get(1), '')
        del ews_mock, self.ews_pool.browse

    def test_get_score_display_when_ews_is_not_partial_returns_score_as_string(
            self):
        cr, uid = self.cr, self.uid
        ews_mock = MagicMock(spec=self.ews_pool.__class__.__name__)
        return_value = [
            ews_mock._get_child_mock(id=1, is_partial=False, score=2)
        ]
        self.ews_pool.browse = MagicMock(return_value=return_value)

        result = self.ews_pool._get_score_display(
            cr, uid, 2, None, None, context=None
        )
        self.assertEquals(result.get(1), '2')
        del ews_mock, self.ews_pool.browse
