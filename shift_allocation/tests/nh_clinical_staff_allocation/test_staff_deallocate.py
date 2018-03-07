# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestStaffAllocationDeallocate(SingleTransactionCase):

    EXPECTED_WARDS = [128, 256, 512, 1024]

    @classmethod
    def setUpClass(cls):
        super(TestStaffAllocationDeallocate, cls).setUpClass()
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.allocation_pool = cls.registry('nh.clinical.staff.allocation')
        cls.user_pool = cls.registry('res.users')
        cls.allocating_pool = cls.registry('nh.clinical.allocating')

    def setUp(self):
        cr, uid = self.cr, self.uid
        super(TestStaffAllocationDeallocate, self).setUp()

        def mock_allocation_wizard_browse(*args, **kwargs):
            context = kwargs.get('context')
            if context and 'deallocate_test' in context:
                loc_1 = self.location_pool.create(
                    cr, uid, {'usage': 'bed', 'name': 'Loc1',
                              'type': 'poc', 'parent_id': 1})
                loc_2 = self.location_pool.create(
                    cr, uid, {'usage': 'bed', 'name': 'Loc2',
                              'type': 'poc', 'parent_id': 1})
                loc_3 = self.location_pool.create(
                    cr, uid, {'usage': 'ward', 'name': 'Loc3',
                              'type': 'poc', 'parent_id': 1})
                if context == 'deallocate_test_resp_allocation':
                    global ward_id
                    ward_id = loc_3
                if context in ['deallocate_test_unfollow',
                               'deallocate_test_user_write']:
                    global location_ids
                    location_ids = [loc_1, loc_2]
                return self.allocation_pool.new(cr, uid, {'location_ids': [
                    loc_1, loc_2], 'ward_id': loc_3})
            else:
                return mock_allocation_wizard_browse.origin(*args, **kwargs)

        def mock_user_write(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'deallocate_test_user_write':
                global user_locations
                user_locations = args[4]['location_ids'][0]
            return True

        def mock_resp_allocation(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'deallocate_test_resp_allocation':
                global resp_allocation
                resp_allocation = args[4]
            return True

        def mock_unfollow(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'deallocate_test_unfollow':
                global unfollow
                unfollow = args[3]
            return True

        def mock_allocating_create(*args, **kwargs):
            return 1

        def mock_allocation_write(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'deallocate_test_allocation_write':
                global allocating_ids
                allocating_ids = args[4]
            return True

        def mock_user_for_location_search(*args, **kwargs):
            return [1, 2, 4, 8, 16, 32, 64]

        self.allocation_pool._patch_method('browse',
                                           mock_allocation_wizard_browse)
        self.allocation_pool._patch_method(
            'responsibility_allocation_activity', mock_resp_allocation)
        self.allocation_pool._patch_method(
            'unfollow_patients_in_locations', mock_unfollow)
        self.user_pool._patch_method('search', mock_user_for_location_search)
        self.user_pool._patch_method('write', mock_user_write)
        self.allocating_pool._patch_method('create', mock_allocating_create)
        self.allocation_pool._patch_method('write', mock_allocation_write)

    def tearDown(self):
        super(TestStaffAllocationDeallocate, self).tearDown()
        self.allocation_pool._revert_method('browse')
        self.allocation_pool._revert_method(
            'responsibility_allocation_activity')
        self.allocation_pool._revert_method('unfollow_patients_in_locations')
        self.user_pool._revert_method('search')
        self.user_pool._revert_method('write')
        self.allocating_pool._revert_method('create')
        self.allocation_pool._revert_method('write')

    def test_deallocates_users_from_locations(self):
        """
        Test that deallocate is deallocating the users from the correct
        locations
        """
        self.allocation_pool.deallocate(self.cr, self.uid, [64],
                                        context='deallocate_test_user_write')
        self.assertEqual(user_locations[0], 3)
        self.assertEqual(user_locations[1], location_ids[1])

    def test_adds_allocating_ids(self):
        """
        Make sure that deallocate is writing the correct
        allocation ids to the model and changing the stage to users
        """
        self.allocation_pool.deallocate(
            self.cr, self.uid, [64],
            context='deallocate_test_allocation_write')
        self.assertEqual(allocating_ids['allocating_ids'],
                         [[6, 0, [1, 1]]])
        self.assertEqual(allocating_ids['stage'], 'users')

    def test_create_responsibility_allocation_activities(self):
        """
        Make sure that deallocate is creating and completing responsibility
        allocation activities for the allocation
        """
        self.allocation_pool.deallocate(
            self.cr, self.uid, [64],
            context='deallocate_test_resp_allocation')
        self.assertEqual(resp_allocation, [ward_id])

    def test_unfollow_patients_in_locations(self):
        """
        Make sure that deallocate is unfollowing all patients in the location
        so there's no followed patients persisting after a reallocation
        """
        self.allocation_pool.deallocate(
            self.cr, self.uid, [64],
            context='deallocate_test_unfollow')
        self.assertEqual(unfollow, location_ids)

    def test_returns_wizard_id(self):
        """
        Test that the submit_wards method returns the wizard ID to the frontend
        so it can be passed to the next part of the wizard
        """
        wizard_test = self.allocation_pool.deallocate(
            self.cr, self.uid, [64], context='deallocate_test')
        self.assertEqual(wizard_test,
                         {
                             'type': 'ir.actions.act_window',
                             'name': 'Nursing Shift Change',
                             'res_model': 'nh.clinical.staff.allocation',
                             'res_id': 64,
                             'view_mode': 'form',
                             'target': 'new',
                         })

    def test_errors_on_bad_id(self):
        """
        Method should error when passed an ID that isn't an int
        """
        with self.assertRaises(ValueError) as id_error:
            self.allocation_pool.deallocate(
                self.cr, self.uid, 'this is a test',
                context='deallocate_test')
        self.assertEqual(id_error.exception.message,
                         'Invalid ID passed to deallocate')
