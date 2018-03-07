# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestStaffAllocationSubmitWard(SingleTransactionCase):

    EXPECTED_WARDS = [128, 256, 512, 1024]

    @classmethod
    def setUpClass(cls):
        super(TestStaffAllocationSubmitWard, cls).setUpClass()
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.allocation_pool = cls.registry('nh.clinical.staff.allocation')

    def setUp(self):
        cr, uid = self.cr, self.uid
        super(TestStaffAllocationSubmitWard, self).setUp()

        def mock_allocation_wizard_browse(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'submit_ward_test':
                ward = self.location_pool.new(cr, uid, {'id': 'test_location'})
                return self.allocation_pool.new(cr, uid, {'ward_id': ward})
            else:
                return mock_allocation_wizard_browse.origin(*args, **kwargs)
        self.allocation_pool._patch_method('browse',
                                           mock_allocation_wizard_browse)

        def mock_location_search(*args, **kwargs):
            return self.EXPECTED_WARDS
        self.location_pool._patch_method('search', mock_location_search)

    def tearDown(self):
        super(TestStaffAllocationSubmitWard, self).tearDown()
        self.allocation_pool._revert_method('browse')
        self.location_pool._revert_method('search')

    def test_writes_bed_locations(self):
        """
        Test that the submit_wards method finds a set of beds and writes them
        to the wizard model
        """
        def mock_allocation_write(*args, **kwargs):
            global allocation_write_vals
            allocation_write_vals = args[4]['location_ids'][0][2]
            return True

        self.allocation_pool._patch_method('write', mock_allocation_write)
        self.allocation_pool.submit_ward(self.cr, self.uid, [64],
                                         context='submit_ward_test')
        self.allocation_pool._revert_method('write')
        self.assertEqual(allocation_write_vals, self.EXPECTED_WARDS)

    def test_returns_wizard_id(self):
        """
        Test that the submit_wards method returns the wizard ID to the frontend
        so it can be passed to the next part of the wizard
        """
        def mock_allocation_write(*args, **kwargs):
            return True

        self.allocation_pool._patch_method('write', mock_allocation_write)
        wizard_test = self.allocation_pool.submit_ward(
            self.cr, self.uid, [64], context='submit_ward_test')
        self.allocation_pool._revert_method('write')
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
            self.allocation_pool.submit_ward(
                self.cr, self.uid, 'this is a test',
                context='submit_ward_test')
        self.assertEqual(id_error.exception.message,
                         'Invalid ID passed to submit_wards')
