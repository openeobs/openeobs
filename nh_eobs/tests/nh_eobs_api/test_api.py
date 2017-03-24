# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from datetime import datetime as dt, timedelta as td

from openerp.osv.orm import except_orm
from openerp.tests.common import SingleTransactionCase


class TestAPI(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAPI, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.user_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.context_pool = cls.registry('nh.clinical.context')
        cls.api = cls.registry('nh.clinical.api')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.eobs_api = cls.registry('nh.eobs.api')
        cls.apidemo = cls.registry('nh.clinical.api.demo')
        cls.follow_pool = cls.registry('nh.clinical.patient.follow')
        cls.unfollow_pool = cls.registry('nh.clinical.patient.unfollow')
        cls.creason_pool = cls.registry('nh.cancel.reason')

        cls.eobs_context_id = cls.context_pool.search(
            cr, uid, [['name', '=', 'eobs']])[0]
        cls.admin_group_id = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Admin Group']])[0]
        cls.hca_group_id = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical HCA Group']])[0]
        cls.nurse_group_id = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Nurse Group']])[0]
        cls.wm_group_id = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Shift Coordinator Group']])[0]
        cls.dr_group_id = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Doctor Group']])[0]

        cls.hospital_id = cls.location_pool.create(
            cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                      'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(
            cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})

        cls.adt_uid = cls.user_pool.create(
            cr, uid, {'name': 'Admin 0', 'login': 'user_000',
                      'pos_id': cls.pos_id, 'password': 'user_000',
                      'groups_id': [[4, cls.admin_group_id]]})
        cls.ward_id = cls.location_pool.create(
            cr, uid, {'name': 'Ward0', 'code': 'W0', 'usage': 'ward',
                      'parent_id': cls.hospital_id, 'type': 'poc',
                      'context_ids': [[4, cls.eobs_context_id]]})
        cls.ward_id2 = cls.location_pool.create(
            cr, uid, {'name': 'Ward1', 'code': 'W1', 'usage': 'ward',
                      'parent_id': cls.hospital_id, 'type': 'poc',
                      'context_ids': [[4, cls.eobs_context_id]]})
        cls.beds = [cls.location_pool.create(
            cr, uid, {'name': 'Bed'+str(i), 'code': 'B'+str(i), 'usage': 'bed',
                      'parent_id': cls.ward_id, 'type': 'poc',
                      'context_ids': [[4, cls.eobs_context_id]]}
        ) for i in range(3)]
        cls.hca_uid = cls.user_pool.create(
            cr, uid, {'name': 'HCA0', 'login': 'hca0', 'password': 'hca0',
                      'groups_id': [[4, cls.hca_group_id]],
                      'location_ids': [[5]]})
        cls.nurse_uid = cls.user_pool.create(
            cr, uid, {'name': 'NURSE0', 'login': 'n0', 'password': 'n0',
                      'groups_id': [[4, cls.nurse_group_id]],
                      'location_ids': [[4, cls.beds[0]]]})
        cls.nurse_uid2 = cls.user_pool.create(
            cr, uid, {'name': 'NURSE1', 'login': 'n1', 'password': 'n1',
                      'groups_id': [[4, cls.nurse_group_id]],
                      'location_ids': [[4, cls.beds[0]], [4, cls.beds[1]]]})
        cls.wm_uid = cls.user_pool.create(
            cr, uid, {'name': 'WM0', 'login': 'wm0', 'password': 'wm0',
                      'groups_id': [[4, cls.wm_group_id]],
                      'location_ids': [[4, cls.ward_id]]})
        cls.dr_uid = cls.user_pool.create(
            cr, uid, {'name': 'DR0', 'login': 'dr0', 'password': 'dr0',
                      'groups_id': [[4, cls.dr_group_id]],
                      'location_ids': [[4, cls.ward_id]]})
        cls.patients = [cls.patient_pool.create(
            cr, uid, {'other_identifier': 'HN00'+str(i)}) for i in range(3)]

        cls.api.admit(cr, cls.adt_uid, 'HN000', {'location': 'W0'})
        cls.api.admit(cr, cls.adt_uid, 'HN001', {'location': 'W0'})

        placement_id = cls.activity_pool.search(
            cr, uid, [['patient_id', '=', cls.patients[0]],
                      ['data_model', '=', 'nh.clinical.patient.placement'],
                      ['state', '=', 'scheduled']])[0]
        cls.activity_pool.submit(
            cr, uid, placement_id, {'location_id': cls.beds[0]})
        cls.activity_pool.complete(cr, uid, placement_id)

    def test_01_check_activity_id(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: activity_id exists
        activity_ids = self.activity_pool.search(cr, uid, [])
        self.assertTrue(
            self.eobs_api._check_activity_id(cr, uid, activity_ids[0]))

        # Scenario 2: activity_id does not exist
        with self.assertRaises(except_orm):
            self.eobs_api._check_activity_id(cr, uid, -1)

    def test_02_check_activity_access(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: user is responsible for the activity
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'scheduled'],
            ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        self.assertTrue(self.eobs_api.check_activity_access(
            cr, self.nurse_uid, activity_ids[0]))

        # Scenario 2: user is not responsible for the activity
        self.assertFalse(self.eobs_api.check_activity_access(
            cr, self.hca_uid, activity_ids[0]))

        # Scenario 3: the activity has been assigned to a specific user
        self.activity_pool.write(
            cr, uid, activity_ids[0], {'user_id': self.hca_uid})
        self.assertFalse(self.eobs_api.check_activity_access(
            cr, self.nurse_uid, activity_ids[0]))
        self.activity_pool.write(cr, uid, activity_ids[0], {'user_id': False})

    def test_03_create_activity(self):
        cr = self.cr

        activity_id = self.eobs_api._create_activity(
            cr, self.nurse_uid, 'nh.clinical.patient.move', {}, {})
        self.assertTrue(activity_id)

    def test_04_get_activities_for_spell(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: get activities
        spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patients[0])
        activities_data = self.eobs_api.get_activities_for_spell(
            cr, self.wm_uid, spell_id, False)
        self.assertEqual(len(activities_data), 1)
        self.assertEqual(activities_data[0]['data_model'],
                         'nh.clinical.patient.observation.ews')
        self.activity_pool.submit(
            cr, self.nurse_uid, activities_data[0]['id'],
            {'respiration_rate': 35, 'indirect_oxymetry_spo2': 99,
             'body_temperature': 37.5, 'blood_pressure_systolic': 120,
             'blood_pressure_diastolic': 80, 'pulse_rate': 65,
             'avpu_text': 'A', 'oxygen_administration_flag': False})
        self.activity_pool.complete(
            cr, self.nurse_uid, activities_data[0]['id'])

        # Scenario 2: get specific observations data
        activities_data = self.eobs_api.get_activities_for_spell(
            cr, self.wm_uid, spell_id, 'ews')
        self.assertEqual(len(activities_data), 1)

        # Scenario 3: get specific observations data within a time frame
        start = dt.now() + td(hours=1)
        end = dt.now() + td(hours=2)
        activities_data = self.eobs_api.get_activities_for_spell(
            cr, self.wm_uid, spell_id, 'ews', start, end)
        self.assertEqual(len(activities_data), 0)

        # Scenario 3: get specific observations data within a time frame,
        # incorrect start date
        start = 'start'
        with self.assertRaises(except_orm):
            self.eobs_api.get_activities_for_spell(
                cr, self.wm_uid, spell_id, 'ews', start)

        # Scenario 3: get specific observations data within a time frame,
        # incorrect end date
        end = 'end'
        with self.assertRaises(except_orm):
            self.eobs_api.get_activities_for_spell(
                cr, self.wm_uid, spell_id, 'ews', None, end)

        # Scenario 3: try to get data for an spell that doesn't exist
        with self.assertRaises(except_orm):
            self.eobs_api.get_activities_for_spell(cr, self.wm_uid, -1, 'ews')

    def test_05_get_activities(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: get specific activities data
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'completed'],
            ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        data = self.eobs_api.get_activities(cr, self.nurse_uid, activity_ids)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], activity_ids[0])

        # Scenario 2: get responsibility activities
        data = self.eobs_api.get_activities(cr, self.nurse_uid, [])
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['summary'], 'Urgently inform medical team')
        self.assertEqual(data[1]['summary'], 'NEWS Observation')

        # Scenario 3: get activities returns no data
        data = self.eobs_api.get_activities(cr, self.nurse_uid, [-1])
        self.assertFalse(data)

    def test_06_submit(self):
        cr, uid = self.cr, self.uid

        data = {
            'respiration_rate': 11,
            'indirect_oxymetry_spo2': 99,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A',
            'oxygen_administration_flag': False
        }

        # Scenario 1: submit data for an activity
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'scheduled'],
            ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        self.assertTrue(self.eobs_api.submit(
            cr, self.nurse_uid, activity_ids[0], data))

        # Scenario 2: attempt submission without responsibility
        with self.assertRaises(except_orm):
            self.eobs_api.submit(cr, self.hca_uid, activity_ids[0], data)

    def test_07_assign(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: attempt to assign without responsibility
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]],
            ['state', 'not in', ['completed', 'cancelled']],
            ['data_model', '=', 'nh.clinical.notification.medical_team']])
        with self.assertRaises(except_orm):
            self.eobs_api.assign(cr, self.hca_uid, activity_ids[0], False)

        # Scenario 2: attempt to assign to a non existing user
        with self.assertRaises(except_orm):
            self.eobs_api.assign(
                cr, self.nurse_uid, activity_ids[0], {'user_id': -1})

        # Scenario 3: assign the activity
        self.eobs_api.assign(
            cr, self.nurse_uid, activity_ids[0], {'user_id': self.hca_uid})
        activity = self.activity_pool.browse(cr, uid, activity_ids[0])
        self.assertEqual(activity.user_id.id, self.hca_uid)
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]],
            ['state', 'not in', ['completed', 'cancelled']],
            ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        self.eobs_api.assign(cr, self.nurse_uid, activity_ids[0], {})

    def test_08_follow_invite(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: attempt to send an invite for a patient you are not
        # responsible for
        with self.assertRaises(except_orm):
            self.eobs_api.follow_invite(
                cr, self.nurse_uid, [self.patients[1]], self.hca_uid)

        # Scenario 2: invite another user to follow a patient
        self.assertTrue(self.eobs_api.follow_invite(
            cr, self.nurse_uid, [self.patients[0]], self.hca_uid))
        activity_ids = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.patient.follow'],
            ['user_id', '=', self.hca_uid], ['state', '=', 'new']])
        self.assertTrue(activity_ids)

    def test_09_get_invited_users(self):
        cr = self.cr

        patients = self.eobs_api.get_patients(cr, self.nurse_uid, [])
        self.assertTrue(self.eobs_api.get_invited_users(
            cr, self.nurse_uid, patients))
        self.assertEqual(len(patients[0]['invited_users']), 1)
        self.assertEqual(patients[0]['invited_users'][0]['id'], self.hca_uid)
        self.assertEqual(patients[0]['invited_users'][0]['name'], 'HCA0')

    def test_10_get_assigned_activities(self):
        cr = self.cr

        # Scenario 1: get specific type activities
        res = self.eobs_api.get_assigned_activities(
            cr, self.hca_uid, 'nh.clinical.notification.medical_team')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['message'], 'You have a notification')

        # Scenario 2: get all assigned activities
        res = self.eobs_api.get_assigned_activities(cr, self.hca_uid)
        self.assertEqual(len(res), 2)

    def test_11_get_patient_followers(self):
        cr, uid = self.cr, self.uid

        activity_ids = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.patient.follow'],
            ['user_id', '=', self.hca_uid], ['state', '=', 'new']])
        self.activity_pool.complete(cr, self.hca_uid, activity_ids[0])
        patients = self.eobs_api.get_patients(cr, self.nurse_uid, [])
        self.assertTrue(self.eobs_api.get_patient_followers(
            cr, self.nurse_uid, patients))
        self.assertEqual(len(patients[0]['followers']), 1)
        self.assertEqual(patients[0]['followers'][0]['id'], self.hca_uid)
        self.assertEqual(patients[0]['followers'][0]['name'], 'HCA0')

    def test_12_get_followed_patients(self):
        cr = self.cr

        # Scenario 1: followed patients returns data
        res = self.eobs_api.get_followed_patients(cr, self.hca_uid)
        self.assertEqual(len(res), 1)

        # Scenario 2: no followed patients
        res = self.eobs_api.get_followed_patients(cr, self.nurse_uid)
        self.assertEqual(len(res), 0)

    def test_13_remove_followers(self):
        cr = self.cr

        # Scenario 1: attempt to remove followers for a patient you are not
        # responsible for
        with self.assertRaises(except_orm):
            self.eobs_api.remove_followers(
                cr, self.nurse_uid, [self.patients[1]])

        # Scenario 2: remove patient followers
        self.assertTrue(self.eobs_api.remove_followers(
            cr, self.nurse_uid, [self.patients[0]]))

    def test_14_unassign(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: attempt to unassign without being assigned to the
        # activity
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]],
            ['state', 'not in', ['completed', 'cancelled']],
            ['data_model', '=', 'nh.clinical.notification.medical_team']])
        with self.assertRaises(except_orm):
            self.eobs_api.unassign(cr, self.nurse_uid, activity_ids[0])

        # Scenario 2: unassign hca activities
        self.assertTrue(self.eobs_api.unassign_my_activities(cr, self.hca_uid))
        activity = self.activity_pool.browse(cr, uid, activity_ids[0])
        self.assertFalse(activity.user_id)

    def test_15_complete(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: attempt to complete without responsibility
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]],
            ['state', 'not in', ['completed', 'cancelled']],
            ['data_model', '=', 'nh.clinical.notification.medical_team']])
        with self.assertRaises(except_orm):
            self.eobs_api.complete(cr, self.hca_uid, activity_ids[0], {})

        # Scenario 2: complete an activity
        self.assertTrue(self.eobs_api.complete(
            cr, self.nurse_uid, activity_ids[0], {}))

    def test_16_get_cancel_reasons(self):
        cr, uid = self.cr, self.uid

        reason_ids = list()
        reason_ids.append(self.creason_pool.create(
            cr, uid, {'name': 'test_reason_01', 'system': False}))
        reason_ids.append(self.creason_pool.create(
            cr, uid, {'name': 'test_reason_02', 'system': True}))

        reasons = self.eobs_api.get_cancel_reasons(cr, uid)
        self.assertTrue(reasons)
        reason_returned = False
        for r in reasons:
            if r['id'] in reason_ids:
                self.assertEqual(r['name'], 'test_reason_01')
                reason_returned = True
        self.assertTrue(reason_returned)

    def test_17_get_form_description(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.get_form_description(
            cr, self.nurse_uid, self.patients[0],
            'nh.clinical.patient.observation.ews'))

    def test_18_is_cancellable(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.is_cancellable(
            cr, self.nurse_uid, 'nh.clinical.notification.medical_team'))
        self.assertFalse(self.eobs_api.is_cancellable(
            cr, self.nurse_uid, 'nh.clinical.patient.observation.ews'))

    def test_19_get_activity_score(self):
        cr = self.cr

        data = {
            'respiration_rate': 35,
            'indirect_oxymetry_spo2': 99,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A',
            'oxygen_administration_flag': False
        }

        self.assertFalse(self.eobs_api.get_activity_score(
            cr, self.nurse_uid, 'nh.clinical.notification.medical_team', {}))
        self.assertDictEqual(self.eobs_api.get_activity_score(
            cr, self.nurse_uid, 'nh.clinical.patient.observation.ews', data), {
                'score': 3, 'clinical_risk': 'Medium', 'three_in_one': True})

    def test_20_get_active_observations(self):
        cr = self.cr

        active_observations = [
            {
                'type': 'ews',
                'name': 'NEWS'
            },
            {
                'type': 'height',
                'name': 'Height'
            },
            {
                'type': 'weight',
                'name': 'Weight'
            },
            {
                'type': 'blood_product',
                'name': 'Blood Product'
            },
            {
                'type': 'blood_sugar',
                'name': 'Blood Sugar'
            },
            {
                'type': 'stools',
                'name': 'Bristol Stool Scale'
            },
            {
                'type': 'gcs',
                'name': 'Glasgow Coma Scale (GCS)'
            },
            {
                'type': 'pbp',
                'name': 'Postural Blood Pressure'
            }
        ]

        self.assertListEqual(self.eobs_api.get_active_observations(
            cr, self.nurse_uid, self.patients[0]), active_observations)
        self.assertFalse(self.eobs_api.get_active_observations(
            cr, self.nurse_uid, self.patients[2]))

    def test_21_get_patient_info(self):
        cr = self.cr

        res = self.eobs_api.get_patient_info(cr, self.nurse_uid, 'HN000')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['other_identifier'], 'HN000')
        self.assertEqual(len(res[0]['activities']), 2)

    def test_22_get_patients(self):
        cr = self.cr

        # Scenario 1: get specific patient data
        res = self.eobs_api.get_patients(
            cr, self.nurse_uid, [self.patients[1]])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['other_identifier'], 'HN001')

        # Scenario 2: get responsibility patients
        res = self.eobs_api.get_patients(cr, self.nurse_uid, [])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['other_identifier'], 'HN000')

        # Scenario 3: get patients without having responsibility
        res = self.eobs_api.get_patients(cr, self.hca_uid, [])
        self.assertFalse(res)

    def test_23_check_patient_responsibility(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.check_patient_responsibility(
            cr, self.nurse_uid, self.patients[0]))
        self.assertFalse(self.eobs_api.check_patient_responsibility(
            cr, self.nurse_uid, self.patients[1]))

    def test_24_get_activities_for_patient(self):
        cr = self.cr

        # Scenario 1: get activities
        res = self.eobs_api.get_activities_for_patient(
            cr, self.wm_uid, self.patients[0], False)
        self.assertEqual(len(res), 2)

        # Scenario 2: get specific observations data
        res = self.eobs_api.get_activities_for_patient(
            cr, self.wm_uid, self.patients[0], 'ews')
        self.assertEqual(len(res), 1)

    def test_25_get_activity_type(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: get activity type
        self.assertEqual(self.eobs_api._get_activity_type(
            cr, uid, 'ews'), 'nh.clinical.patient.observation.ews')

        # Scenario 2: get ambiguous activity type
        # Gone. Weight moved into its own module, nh_weight.

        # Scenario 3: get observation activity type

        # Scenario 4: attempt to get activity type that does not exist
        with self.assertRaises(except_orm):
            self.eobs_api._get_activity_type(cr, uid, 'test.non.existant.type')

    def test_26_create_activity_for_patient(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: attempt to create an activity with an invalid type
        with self.assertRaises(except_orm):
            self.eobs_api.create_activity_for_patient(
                cr, self.nurse_uid, self.patients[0], '')

        # Scenario 2: attempt to create an activity without proper access
        # rights
        group_id = self.groups_pool.create(cr, uid, {'name': 'Test Group'})
        user_id = self.user_pool.create(
            cr, uid, {'name': 'TU01', 'login': 'tu01', 'password': 'tu01',
                      'groups_id': [[6, 0, [group_id]]]})
        with self.assertRaises(except_orm):
            self.eobs_api.create_activity_for_patient(
                cr, user_id, self.patients[0], 'ews')

        # Scenario 3: attempt to create an activity that already exists
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]],
            ['state', 'not in', ['completed', 'cancelled']],
            ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        ews_id = self.eobs_api.create_activity_for_patient(
            cr, self.nurse_uid, self.patients[0], 'ews')
        self.assertEqual(activity_ids[0], ews_id)

        # Scenario 4: attempt to create a new activity for a not admitted
        # patient
        # Gone. Weight moved into its own module, nh_weight.

        # Scenario 5: create a new activity
        # Gone. Weight moved into its own module, nh_weight.

    def test_27_register(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.register(
            cr, self.adt_uid, 'HN009', {'family_name': 'test26',
                                        'given_name': '26test'}))

    def test_28_update(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.update(
            cr, self.adt_uid, 'HN009',
            {'family_name': 'test26', 'given_name': '26test',
             'patient_identifier': 'NHS009'}))

    def test_29_admit(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.admit(
            cr, self.adt_uid, 'HN009', {'location': 'W0'}))

    def test_30_admit_update(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.admit_update(
            cr, self.adt_uid, 'HN009', {'location': 'W1'}))

    def test_31_cancel_admit(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.cancel_admit(cr, self.adt_uid, 'HN009'))

    def test_32_transfer(self):
        cr = self.cr

        self.eobs_api.admit(cr, self.adt_uid, 'HN009', {'location': 'W0'})
        self.assertTrue(self.eobs_api.transfer(
            cr, self.adt_uid, 'HN009', {'location': 'W1'}))

    def test_33_cancel_transfer(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.cancel_transfer(
            cr, self.adt_uid, 'HN009'))

    def test_34_discharge(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.discharge(cr, self.adt_uid, 'HN009', {}))

    def test_35_cancel_discharge(self):
        cr = self.cr

        self.assertTrue(self.eobs_api.cancel_discharge(
            cr, self.adt_uid, 'HN009'))

    def test_36_merge(self):
        cr = self.cr
        self.eobs_api.register(
            cr, self.adt_uid, 'HN010', {'family_name': 'test35'})
        self.assertTrue(self.eobs_api.merge(
            cr, self.adt_uid, 'HN010', {'from_identifier': 'HN009'}))

    def test_37_get_share_users(self):
        cr = self.cr

        res = self.eobs_api.get_share_users(cr, self.nurse_uid)
        self.assertEqual(len(res), 1)

    def test_38_cancel(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Cancel without data
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'scheduled'],
            ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        self.activity_pool.submit(cr, self.nurse_uid, activity_ids[0], {
            'respiration_rate': 35,
            'indirect_oxymetry_spo2': 99,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A',
            'oxygen_administration_flag': False
        })
        self.activity_pool.complete(cr, self.nurse_uid, activity_ids[0])
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'new'],
            ['data_model', '=', 'nh.clinical.notification.medical_team']])
        self.assertTrue(self.eobs_api.cancel(
            cr, self.nurse_uid, activity_ids[0], None))

        # Scenario 2: Cancel with data
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'scheduled'],
            ['data_model', '=', 'nh.clinical.patient.observation.ews']])
        self.activity_pool.submit(cr, self.nurse_uid, activity_ids[0], {
            'respiration_rate': 35,
            'indirect_oxymetry_spo2': 99,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A',
            'oxygen_administration_flag': False
        })
        self.activity_pool.complete(cr, self.nurse_uid, activity_ids[0])
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'new'],
            ['data_model', '=', 'nh.clinical.notification.medical_team']])
        self.assertTrue(self.eobs_api.cancel(
            cr, self.nurse_uid, activity_ids[0],
            {'date_terminated': '2015-7-10 00:00:00'}))
