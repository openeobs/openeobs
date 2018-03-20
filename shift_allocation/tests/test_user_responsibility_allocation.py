# -*- coding: utf-8 -*-
from faker import Faker
from openerp.osv.orm import except_orm
from openerp.tests import common


fake = Faker()


# TODO fix this test and remove unnecessary setup.
# This test was created when the shift_allocation module was extracted from the
# nh_clinical module. The test method in here was part of
# `nh_clinical.tests.test_auditing` which was a disabled test.
#
# To ensure that the test would have everything it needed to run it was moved
# into here with the setup duplicated from test_auditing. If this test is ever
# reinstated then there is probably some of the setup that can be removed as it
# is only relevant to the other test that still remains in
# `nh_clinical.tests.test_auditing`.
class TestAuditing(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAuditing, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.activate_pool = cls.registry('nh.clinical.location.activate')
        cls.deactivate_pool = cls.registry('nh.clinical.location.deactivate')
        cls.allocation_pool = cls.registry(
            'nh.clinical.user.responsibility.allocation')
        cls.move_pool = cls.registry('nh.clinical.patient.move')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.patient_ids = cls.apidemo.build_unit_test_env1(cr, uid,
                                                           bed_count=4,
                                                           patient_count=4)

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

    def test_user_responsibility_allocation(self):
        """
        Tests User Responsibility Allocation Activity
        """
        cr, uid = self.cr, self.uid

        # Scenario 1: Removing responsibility from a user
        user = self.users_pool.browse(cr, uid, self.nu_id)
        self.assertTrue(user.location_ids,
                        msg="Scenario 1 Pre-state: "
                            "User is not responsible for any locations")
        activity_id = self.allocation_pool.create_activity(cr, uid, {}, {
            'responsible_user_id': self.nu_id,
            'location_ids': [[6, False, []]]})
        self.assertTrue(activity_id,
                        msg="User Responsibility Allocation Activity creation "
                            "failed")
        activity = self.activity_pool.browse(cr, uid, activity_id)
        self.assertEqual(activity.data_ref.responsible_user_id.id, self.nu_id,
                         msg="User Responsibility Allocation Activity: "
                             "wrong user recorded")
        self.assertFalse(activity.data_ref.location_ids,
                         msg="User Responsibility Allocation Activity: "
                             "wrong locations recorded")
        self.activity_pool.complete(cr, uid, activity_id)
        user = self.users_pool.browse(cr, uid, self.nu_id)
        self.assertFalse(user.location_ids,
                         msg="Scenario 1 Failed: "
                             "User is still responsible for some locations")

        # Scenario 2: Assigning a bed to a nurse
        bed_ids = self.location_pool.search(
            cr, uid, [['usage', '=', 'bed'], ['id', 'child_of', self.wu_id]])
        activity_id = self.allocation_pool.create_activity(cr, uid, {}, {
            'responsible_user_id': self.nu_id,
            'location_ids': [[6, False, [bed_ids[0]]]]})
        self.activity_pool.complete(cr, uid, activity_id)
        user = self.users_pool.browse(cr, uid, self.nu_id)
        self.assertEqual(bed_ids[0], user.location_ids.id,
                         msg="Scenario 2 Failed: User locations don't match")

        # Scenario 3: Assigning a ward to a nurse
        location_ids = self.location_pool.search(
            cr, uid, [['id', 'child_of', self.wu_id]])
        activity_id = self.allocation_pool.create_activity(cr, uid, {}, {
            'responsible_user_id': self.nu_id,
            'location_ids': [[6, False, [self.wu_id]]]})
        self.activity_pool.complete(cr, uid, activity_id)
        user = self.users_pool.browse(cr, uid, self.nu_id)
        self.assertEqual(location_ids, [loc.id for loc in user.location_ids],
                         msg="Scenario 3 Failed: User locations don't match")

        # Scenario 4: Assigning a ward to a ward manager
        activity_id = self.allocation_pool.create_activity(cr, uid, {}, {
            'responsible_user_id': self.wmu_id,
            'location_ids': [[6, False, [self.wu_id]]]})
        self.activity_pool.complete(cr, uid, activity_id)
        user = self.users_pool.browse(cr, uid, self.wmu_id)
        self.assertEqual(self.wu_id, user.location_ids.id,
                         msg="Scenario 4 Failed: User locations don't match")

        # Scenario 5: Assign a bed to a ward manager
        activity_id = self.allocation_pool.create_activity(cr, uid, {}, {
            'responsible_user_id': self.wmu_id,
            'location_ids': [[6, False, [bed_ids[0]]]]})
        self.activity_pool.complete(cr, uid, activity_id)
        user = self.users_pool.browse(cr, uid, self.wmu_id)
        self.assertEqual(bed_ids[0], user.location_ids.id,
                         msg="Scenario 5 Failed: User locations don't match")

        # Scenario 6: Complete the activity without data
        activity_id = self.allocation_pool.create_activity(cr, uid, {}, {})
        with self.assertRaises(except_orm):
            self.activity_pool.complete(cr, uid, activity_id)

        # Scenario 7: Complete the activity without user
        activity_id = self.allocation_pool.create_activity(cr, uid, {}, {
            'location_ids': [[6, False, [bed_ids[0]]]]})
        with self.assertRaises(except_orm):
            self.activity_pool.complete(cr, uid, activity_id)
