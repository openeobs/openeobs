# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.tests import common
from faker import Faker
import logging
_logger = logging.getLogger(__name__)

fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class TestGCS(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestGCS, cls).setUpClass()
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
        cls.gcs_pool = cls.registry('nh.clinical.patient.observation.gcs')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.apidemo.build_unit_test_env(cr, uid, bed_count=4,
                                        patient_placement_count=2)

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

    def test_gcs_observations_policy_static(self):
        cr, uid = self.cr, self.uid

        gcs_test_data = {
            'SCORE':    [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            'CASE':     [0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 4],
            'EYES':     ['1', 'C', '2', '2', '3', '3', '3', '4', '4', '4', '4',
                         '4', '4'],
            'VERBAL':   ['1', 'T', '1', '2', '2', '3', '3', '3', '4', '4', '5',
                         '5', '5'],
            'MOTOR':    ['1', '2', '2', '2', '2', '2', '3', '3', '3', '4', '4',
                         '5', '6'],
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

        gcs_activity_id = self.gcs_pool.create_activity(
            cr, uid,
            {'parent_id': spell_activity.id},
            {'patient_id': spell_activity.patient_id.id})

        for i in range(13):
            data = {
                'eyes': gcs_test_data['EYES'][i],
                'verbal': gcs_test_data['VERBAL'][i],
                'motor': gcs_test_data['MOTOR'][i],
            }
            self.activity_pool.assign(cr, uid, gcs_activity_id, user_id)
            self.activity_pool.submit(cr, user_id, gcs_activity_id, data)
            self.activity_pool.complete(cr, user_id, gcs_activity_id)
            gcs_activity = self.activity_pool.browse(cr, uid, gcs_activity_id)

            frequency = gcs_policy['frequencies'][
                gcs_test_data['CASE'][i]]
            nurse_notifications = gcs_policy['notifications'][
                gcs_test_data['CASE'][i]]['nurse']
            assessment = gcs_policy['notifications'][
                gcs_test_data['CASE'][i]]['assessment']
            review_frequency = gcs_policy['notifications'][
                gcs_test_data['CASE'][i]]['frequency']

            _logger.info("TEST - observation GCS: expecting score %s, "
                         "frequency %s"
                         % (gcs_test_data['SCORE'][i], frequency))

            # # # # # # # # # # # # # # # # #
            # Check the score and frequency #
            # # # # # # # # # # # # # # # # #
            self.assertEqual(
                gcs_activity.data_ref.score,
                gcs_test_data['SCORE'][i], msg='Score not matching')
            domain = [
                ('creator_id', '=', gcs_activity.id),
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', self.gcs_pool._name)]
            gcs_activity_ids = self.activity_pool.search(cr, uid, domain)
            self.assertTrue(
                gcs_activity_ids, msg='Next GCS activity was not triggered')
            next_gcs_activity = self.activity_pool.browse(
                cr, uid, gcs_activity_ids[0])
            self.assertEqual(
                next_gcs_activity.data_ref.frequency,
                frequency, msg='Frequency not matching')

            # # # # # # # # # # # # # # # #
            # Check notification triggers #
            # # # # # # # # # # # # # # # #
            domain = [
                ('creator_id', '=', gcs_activity.id),
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
                ('creator_id', '=', gcs_activity.id),
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
                        ('creator_id', '=', gcs_activity.id),
                        ('state', 'not in', ['completed', 'cancelled']),
                        ('data_model', '=', 'nh.clinical.notification.nurse'),
                        ('summary', '=', n)]
                    nurse_not_ids = self.activity_pool.search(cr, uid, domain)
                    self.assertTrue(
                        nurse_not_ids,
                        msg='Nurse notification %s not triggered' % n)
                    self.activity_pool.cancel(cr, uid, nurse_not_ids[0])
            else:
                domain = [
                    ('creator_id', '=', gcs_activity.id),
                    ('state', 'not in', ['completed', 'cancelled']),
                    ('data_model', '=', 'nh.clinical.notification.nurse')]
                nurse_not_ids = self.activity_pool.search(cr, uid, domain)
                self.assertFalse(
                    nurse_not_ids, msg='Nurse notification triggered')
            gcs_activity_id = next_gcs_activity.id
