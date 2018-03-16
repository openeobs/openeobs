# -*- coding: utf-8 -*-
# Part of NHClinical. See LICENSE file for full copyright and licensing details
from openerp.osv.orm import except_orm
from openerp.tests import common


class TestOperations(common.SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestOperations, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        # OPERATIONS DATA MODELS
        cls.placement_pool = cls.registry('nh.clinical.patient.placement')
        cls.move_pool = cls.registry('nh.clinical.patient.move')
        cls.swap_pool = cls.registry('nh.clinical.patient.swap_beds')
        cls.follow_pool = cls.registry('nh.clinical.patient.follow')
        cls.unfollow_pool = cls.registry('nh.clinical.patient.unfollow')
        cls.admission_pool = cls.registry('nh.clinical.patient.admission')
        cls.discharge_pool = cls.registry('nh.clinical.patient.discharge')
        cls.transfer_pool = cls.registry('nh.clinical.patient.transfer')

        cls.wm_group_id = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Shift Coordinator Group']])
        cls.nurse_group_id = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Nurse Group']])
        cls.admin_group_id = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Admin Group']])

        cls.hospital_id = cls.location_pool.create(
            cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                      'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(
            cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})

        cls.adt_uid = cls.users_pool.create(
            cr, uid, {'name': 'Admin 0', 'login': 'user_000',
                      'password': 'user_000',
                      'groups_id': [[4, cls.admin_group_id[0]]],
                      'pos_id': cls.pos_id})

        cls.locations = {}
        cls.users = {}
        for i in range(3):
            wid = cls.location_pool.create(
                cr, uid,
                {'name': 'Ward'+str(i), 'code': 'WARD'+str(i), 'usage': 'ward',
                 'parent_id': cls.hospital_id, 'type': 'poc'})
            cls.locations[wid] = [
                cls.location_pool.create(
                    cr, uid, {'name': 'Bed'+str(i)+str(j),
                              'code': 'BED'+str(i)+str(j),
                              'usage': 'bed', 'parent_id': wid,
                              'type': 'poc'}) for j in range(3)
            ]
            cls.users[wid] = {
                'wm': cls.users_pool.create(
                    cr, uid, {'name': 'WM'+str(i), 'login': 'wm'+str(i),
                              'password': 'wm'+str(i),
                              'groups_id': [[4, cls.wm_group_id[0]]],
                              'pos_id': cls.pos_id,
                              'location_ids': [[6, 0, [wid]]]}),
                'n': cls.users_pool.create(
                    cr, uid, {'name': 'N'+str(i), 'login': 'n'+str(i),
                              'password': 'n'+str(i),
                              'groups_id': [[4, cls.nurse_group_id[0]]],
                              'pos_id': cls.pos_id,
                              'location_ids': [[6, 0, cls.locations[wid]]]})
            }

        cls.patients = [
            cls.patient_pool.create(
                cr, uid,
                {'other_identifier': 'TESTP000'+str(i),
                 'given_name': 'John',
                 'family_name': 'Smith',
                 'middle_names': 'Clarke '+str(i),
                 'patient_identifier': 'TESTNHS0'+str(i)}) for i in range(7)
        ]

    def test_14_patient_following(self):
        cr, uid = self.cr, self.uid

        ward_id = self.locations.keys()[0]
        wm_id = self.users[ward_id]['wm']
        nurse_id = self.users[ward_id]['n']

        # Creating 4 Patient Follow Activities:
        # 1) test Patient Follow.
        # 2) test open follow activities are cancelled
        # when 'unfollowing' a patient.
        # 3) test 2nd case only happens if you created those follow activities.
        follow_id = self.follow_pool.create_activity(
            cr, uid, {'user_id': nurse_id},
            {'patient_ids': [[4, self.patients[3]]]}
        )
        follow_id2 = self.follow_pool.create_activity(
            cr, uid, {'user_id': nurse_id},
            {'patient_ids': [[6, False, [self.patients[3], self.patients[4]]]]}
        )
        follow_id3 = self.follow_pool.create_activity(
            cr, wm_id, {'user_id': nurse_id},
            {'patient_ids': [[6, False, [self.patients[3], self.patients[4]]]]}
        )
        self.assertTrue(follow_id,
                        msg="Patient Follow: Create activity failed")
        self.assertTrue(follow_id2,
                        msg="Patient Follow: Create activity failed")
        self.assertTrue(follow_id3,
                        msg="Patient Follow: Create activity failed")

        # Complete Follow Activity and check System state POST-COMPLETE
        self.activity_pool.complete(cr, uid, follow_id)
        user = self.users_pool.browse(cr, uid, nurse_id)
        self.assertTrue(
            self.patients[3] in [patient.id for patient in user.following_ids],
            msg="Patient Follow: The user is not following that patient")
        self.assertFalse(
            self.patients[4] in [patient.id for patient in user.following_ids],
            msg="Patient Follow: "
                "The user should not be following that patient")
        patient = self.patient_pool.browse(cr, uid, self.patients[3])
        patient2 = self.patient_pool.browse(cr, uid, self.patients[4])
        self.assertTrue(nurse_id in [u.id for u in patient.follower_ids],
                        msg="Patient Follow: "
                            "The user is not in the patient followers list")
        self.assertFalse(
            nurse_id in [u.id for u in patient2.follower_ids],
            msg="Patient Follow: "
                "The user should not be in the patient followers list")

        # Create an Unfollow Activity
        unfollow_id = self.unfollow_pool.create_activity(
            cr, uid, {}, {'patient_ids': [[4, self.patients[3]]]})
        self.assertTrue(unfollow_id,
                        msg="Patient Unfollow: Create activity failed")

        # Complete Unfollow Activity and check System state POST-COMPLETE
        self.activity_pool.complete(cr, uid, unfollow_id)
        user = self.users_pool.browse(cr, uid, nurse_id)
        self.assertTrue(
            self.patients[3] not in [pat.id for pat in user.following_ids],
            msg="Patient Unfollow: The user is still following that patient")
        patient = self.patient_pool.browse(cr, uid, self.patients[3])
        self.assertTrue(
            nurse_id not in [u.id for u in patient.follower_ids],
            msg="Patient Unfollow: "
                "The user still is in the patient followers list")

        follow = self.activity_pool.browse(cr, uid, follow_id2)
        self.assertEqual(follow.state, 'cancelled',
                         msg="Patient Unfollow: A follow activity containing "
                             "the unfollowed patient was not cancelled")
        follow = self.activity_pool.browse(cr, uid, follow_id3)
        self.assertNotEqual(follow.state, 'cancelled',
                            msg="Patient Unfollow: A follow activity created "
                                "by a different user was cancelled")

        # Try to complete follow activity without user assigned to it
        follow_id = self.follow_pool.create_activity(
            cr, uid, {}, {'patient_ids': [[4, self.patients[3]]]})
        with self.assertRaises(except_orm):
            self.activity_pool.complete(cr, uid, follow_id)
