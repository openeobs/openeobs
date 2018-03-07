# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestStaffAllocationResponsibilityAllocation(SingleTransactionCase):

    EXPECTED_LOCATIONS = [128, 256, 512, 1024]

    @classmethod
    def setUpClass(cls):
        super(TestStaffAllocationResponsibilityAllocation, cls).setUpClass()
        cls.allocation_pool = cls.registry('nh.clinical.staff.allocation')
        cls.activity_pool = cls.registry('nh.activity')
        cls.resp_allocation_pool = \
            cls.registry('nh.clinical.user.responsibility.allocation')

    def setUp(self):
        super(TestStaffAllocationResponsibilityAllocation, self).setUp()

        def mock_resp_allo_create(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'resp_allo_test_create':
                global activity_data
                activity_data = args[4]
            return 1

        def mock_activity_complete(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'resp_allo_test_complete':
                global completed_activities
                completed_activities = args[3]
            return True

        self.resp_allocation_pool._patch_method('create_activity',
                                                mock_resp_allo_create)
        self.activity_pool._patch_method('complete', mock_activity_complete)

    def tearDown(self):
        super(TestStaffAllocationResponsibilityAllocation, self).tearDown()
        self.resp_allocation_pool._revert_method('create_activity')
        self.activity_pool._revert_method('complete')

    def test_creates_activity_with_data(self):
        """
        Test that the calls the responsibility allocation method with the user
        ID and location IDS
        """
        self.resp_calls = []
        self.allocation_pool.responsibility_allocation_activity(
            self.cr, self.uid, 64, self.EXPECTED_LOCATIONS,
            context='resp_allo_test_create')
        self.assertEqual(activity_data, {
            'responsible_user_id': 64,
            'location_ids': [[6, 0, self.EXPECTED_LOCATIONS]]
        })

    def test_completes_activity(self):
        """
        Test that the calls the responsibility allocation method with the user
        ID and location IDS
        """
        self.resp_calls = []
        self.allocation_pool.responsibility_allocation_activity(
            self.cr, self.uid, 64, self.EXPECTED_LOCATIONS,
            context='resp_allo_test_complete')
        self.assertEqual(completed_activities, 1)
