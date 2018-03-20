# -*- coding: utf-8 -*-
from faker import Faker
from openerp.osv.orm import except_orm
from openerp.tests import common


fake = Faker()


class TestAuditing(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAuditing, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.activity_pool = cls.registry('nh.activity')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.allocation_pool = cls.registry(
            'nh.clinical.user.responsibility.allocation')

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]

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
