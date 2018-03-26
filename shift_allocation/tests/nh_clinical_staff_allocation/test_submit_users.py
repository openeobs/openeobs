# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestStaffAllocationSubmitUsers(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestStaffAllocationSubmitUsers, cls).setUpClass()
        cls.allocation_pool = cls.registry('nh.clinical.staff.allocation')

    def setUp(self):
        super(TestStaffAllocationSubmitUsers, self).setUp()

        def mock_allocation_write(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'submit_users_test_write':
                global allocating_ids
                allocating_ids = args[4]
            return True

        self.allocation_pool._patch_method('write', mock_allocation_write)

    def tearDown(self):
        super(TestStaffAllocationSubmitUsers, self).tearDown()
        self.allocation_pool._revert_method('write')

    def test_writes_stage(self):
        """
        Make sure that the stage is being changed
        """
        self.allocation_pool.submit_users(self.cr, self.uid, [64],
                                          context='submit_users_test_write')
        self.assertEqual(allocating_ids['stage'], 'allocation')

    def test_returns_wizard_id(self):
        """
        Test that the submit_wards method returns the wizard ID to the frontend
        so it can be passed to the next part of the wizard
        """
        wizard_test = self.allocation_pool.submit_users(
            self.cr, self.uid, [64], context='submit_users_test')
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': 64,
            'view_mode': 'form',
            'target': 'new',
        }
        self.assertEqual(wizard_test, action)

    def test_errors_on_bad_id(self):
        """
        Method should error when passed an ID that isn't an int
        """
        with self.assertRaises(ValueError) as id_error:
            self.allocation_pool.submit_users(
                self.cr, self.uid, 'this is a test',
                context='submit_users_test')
        self.assertEqual(id_error.exception.message,
                         'Invalid ID passed to submit_users')
