# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestStaffAllocationUnfollow(SingleTransactionCase):

    EXPECTED_PATIENTS = [128, 256, 512, 1024]

    @classmethod
    def setUpClass(cls):
        super(TestStaffAllocationUnfollow, cls).setUpClass()
        cls.allocation_pool = cls.registry('nh.clinical.staff.allocation')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.unfollow_pool = cls.registry('nh.clinical.patient.unfollow')

    def setUp(self):
        super(TestStaffAllocationUnfollow, self).setUp()

        def mock_patient_search(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'unfollow_test_search':
                global search_location_ids
                search_location_ids = args[3]
            return self.EXPECTED_PATIENTS

        def mock_unfollow_create(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'unfollow_test_create':
                global unfollow_patients
                unfollow_patients = args[4]
            return 1

        def mock_activity_complete(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'unfollow_test_complete':
                global completed_activities
                completed_activities = args[3]
            return True

        self.patient_pool._patch_method('search', mock_patient_search)
        self.unfollow_pool._patch_method('create_activity',
                                         mock_unfollow_create)
        self.activity_pool._patch_method('complete', mock_activity_complete)

    def tearDown(self):
        super(TestStaffAllocationUnfollow, self).tearDown()
        self.patient_pool._revert_method('search')
        self.unfollow_pool._revert_method('create_activity')
        self.activity_pool._revert_method('complete')

    def test_passes_location_ids(self):
        """
        Test that the calls the responsibility allocation method with the user
        ID and location IDS
        """
        self.resp_calls = []
        self.allocation_pool.unfollow_patients_in_locations(
            self.cr, self.uid, [64], context='unfollow_test_search')
        self.assertEqual(search_location_ids, [
            ['current_location_id', 'in', [64]]])

    def test_passes_patient_ids(self):
        """
        Test that the calls the responsibility allocation method with the user
        ID and location IDS
        """
        self.resp_calls = []
        self.allocation_pool.unfollow_patients_in_locations(
            self.cr, self.uid, [64], context='unfollow_test_create')
        self.assertEqual(unfollow_patients, {
            'patient_ids': [[6, 0, self.EXPECTED_PATIENTS]]
        })

    def test_completes_activity(self):
        """
        Test that the calls the responsibility allocation method with the user
        ID and location IDS
        """
        self.resp_calls = []
        self.allocation_pool.unfollow_patients_in_locations(
            self.cr, self.uid, [64], context='unfollow_test_complete')
        self.assertEqual(completed_activities, 1)
