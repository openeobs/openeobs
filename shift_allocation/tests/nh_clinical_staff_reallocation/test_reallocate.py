# -*- coding: utf-8 -*-
# Part of NHClinical. See LICENSE file for full copyright and licensing details
from openerp.tests.common import SingleTransactionCase


class TestStaffReallocationReallocate(SingleTransactionCase):

    EXPECTED_WARDS = [128, 256, 512, 1024]
    EXPECTED_USERS = [1, 2]

    @classmethod
    def setUpClass(cls):
        super(TestStaffReallocationReallocate, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.activity_pool = cls.registry('nh.activity')
        cls.allocation_pool = cls.registry('nh.clinical.staff.reallocation')
        cls.allocating_pool = cls.registry('nh.clinical.allocating')
        cls.users_pool = cls.registry('res.users')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.nurse = cls.users_pool.create(cr, uid, {
            'name': 'Nurse 1',
            'login': 'complete_test_nurse1'
        })
        cls.hca = cls.users_pool.create(cr, uid, {
            'name': 'HCA 1',
            'login': 'complete_test_hca1'
        })
        cls.location = cls.location_pool.create(cr, uid, {
            'usage': 'bed', 'name': 'Loc3',
            'type': 'poc', 'parent_id': 1})
        cls.ward_location = cls.location_pool.create(cr, uid, {
            'usage': 'ward', 'name': 'Loc4',
            'type': 'poc', 'parent_id': 1})
        cls.allocation = cls.allocating_pool.create(cr, uid, {
            'nurse_id': cls.nurse,
            'hca_ids': [cls.hca],
            'location_id': cls.location
        })

    def setUp(self):
        super(TestStaffReallocationReallocate, self).setUp()

        def mock_get_default_allocatings(*args, **kwargs):
            return [666]

        def mock_get_users_for_locations(*args, **kwargs):
            context = kwargs.get('context')
            if context:
                if context.get('test') == 'get_loc_users':
                    global locations_passed
                    locations_passed = args[3]
                if context.get('test') in ['calls_methods',
                                           'writes_allocating']:
                    return [3]
            return self.EXPECTED_USERS

        def mock_reallocation_wizard_read(*args, **kwargs):
            return {
                'location_ids': self.EXPECTED_WARDS,
                'user_ids': self.EXPECTED_USERS
            }

        def mock_user_read(*args, **kwargs):
            return {
                'location_ids': [1, 2, 3, 4]
            }

        def mock_responsibility_allocation_activity(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'calls_methods':
                global resp_allo_act_called
                resp_allo_act_called = True
            if context and context.get('test') == 'not_called':
                global resp_allo_act_shouldnt_called
                resp_allo_act_shouldnt_called = True
            return True

        def mock_user_patient_unfollow(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'calls_methods':
                global unfollow_called
                unfollow_called = True
            if context and context.get('test') == 'not_called':
                global unfollow_shouldnt_called
                unfollow_shouldnt_called = True
            return True

        def mock_reallocation_write(*args, **kwargs):
            context = kwargs.get('context')
            if context:
                if context.get('test') == 'stage_write':
                    global stagewrite
                    stagewrite = args[4]
                if context.get('test') == 'writes_allocating':
                    global allocatingwrite
                    allocatingwrite = args[4]
            return True

        # TODO EOBS-2534 Refactor test_reallocate module in shift allocation
        def mock_update_shift(*args, **kwargs):
            pass

        self.allocation_pool._patch_method('_get_default_allocatings',
                                           mock_get_default_allocatings)
        self.allocation_pool._patch_method('read',
                                           mock_reallocation_wizard_read)
        self.allocation_pool._patch_method('get_users_for_locations',
                                           mock_get_users_for_locations)
        self.users_pool._patch_method('read', mock_user_read)
        self.allocation_pool._patch_method(
            'responsibility_allocation_activity',
            mock_responsibility_allocation_activity)
        self.allocation_pool._patch_method('unfollow_patients_in_locations',
                                           mock_user_patient_unfollow)
        self.allocation_pool._patch_method('write', mock_reallocation_write)
        self.allocation_pool._patch_method('_update_shift', mock_update_shift)

    def tearDown(self):
        super(TestStaffReallocationReallocate, self).tearDown()
        self.allocation_pool._revert_method('read')
        self.allocation_pool._revert_method('_get_default_allocatings')
        self.users_pool._revert_method('read')
        self.allocation_pool._revert_method(
            'responsibility_allocation_activity')
        self.allocation_pool._revert_method('unfollow_patients_in_locations')
        self.allocation_pool._revert_method('write')
        self.allocation_pool._revert_method('get_users_for_locations')
        self.allocation_pool._revert_method('_update_shift')

    def test_calls_resp_unfollow_on_user_deallocated(self):
        """
        Test that the calls the responsibility allocation method and unfollow
        when the user supplied in locations is not in the user list submitted
        """
        self.allocation_pool.reallocate(self.cr, self.uid, [64],
                                        context={'test': 'calls_methods'})
        self.assertTrue(resp_allo_act_called)
        self.assertTrue(unfollow_called)

    def test_raises_on_invalid_id(self):
        """
        TEst that it raises an exception if passed a non-integer / list ID
        """
        with self.assertRaises(ValueError) as err:
            self.allocation_pool.reallocate(self.cr, self.uid, 'baaaaddd')
        self.assertEqual(err.exception.message, 'reallocate expected integer')

    def test_passes_locations_to_get_users(self):
        """
        Test that it passes the locations from teh Wizard into the method
        to get users based on location
        """
        self.allocation_pool.reallocate(
            self.cr, self.uid, [64], context={'test': 'get_loc_users'})
        self.assertEqual(locations_passed, self.EXPECTED_WARDS)

    def test_doesnt_call_methods_on_no_users_deallocated(self):
        """
        Test that when all users in the locations are submitted it doesn't call
        the resp act and unfollow methods
        """
        self.allocation_pool.reallocate(self.cr, self.uid, [64],
                                        context={'test': 'not_called'})
        self.assertFalse('resp_allo_act_shouldnt_called' in globals())
        self.assertFalse('unfollow_shouldnt_called' in globals())

    def test_writes_stage_to_be_allocating(self):
        """
        Test that it writes the stage 'allocating' to the wizard
        """
        self.allocation_pool.reallocate(self.cr, self.uid, [64],
                                        context={'test': 'stage_write'})
        self.assertEqual(stagewrite, {'stage': 'allocation'})

    def test_recompute_gets_allocatings(self):
        """
        TEst that on the users in the locations not being in the submitted user
        list that it gets the allocations based on the locations and writes
        these to the wizard object
        """
        self.allocation_pool.reallocate(self.cr, self.uid, [64],
                                        context={'test': 'writes_allocating'})
        self.assertEqual(allocatingwrite, {'allocating_ids': [[6, 0, [666]]]})

    def test_returns_wizard_id_to_gui(self):
        """
        Test that the wizard ID is in the returned dictionary
        """
        reallocation = self.allocation_pool.reallocate(self.cr, self.uid, [64])
        self.assertEqual(reallocation, {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Re-Allocation',
            'res_model': 'nh.clinical.staff.reallocation',
            'res_id': 64,
            'view_mode': 'form',
            'target': 'new',
        })
