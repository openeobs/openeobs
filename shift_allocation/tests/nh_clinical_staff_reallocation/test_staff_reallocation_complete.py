# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestStaffReallocationComplete(SingleTransactionCase):

    EXPECTED_WARDS = [128, 256, 512, 1024]
    resp_calls = []

    @classmethod
    def setUpClass(cls):
        super(TestStaffReallocationComplete, cls).setUpClass()
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
        cr, uid = self.cr, self.uid
        super(TestStaffReallocationComplete, self).setUp()

        def mock_allocation_wizard_browse(*args, **kwargs):
            context = kwargs.get('context')
            if context and 'complete_test' in context:
                if context == 'complete_test_dual_role':
                    return self.allocation_pool.new(cr, uid, {
                        'allocating_ids': self.allocating_pool.new(cr, uid,
                                                                   {}),
                        'user_ids': [uid, self.hca],
                        'ward_id': self.ward_location
                    })
                return self.allocation_pool.new(cr, uid, {
                    'allocating_ids': self.allocating_pool.new(cr, uid, {}),
                    'user_ids': [self.nurse, self.hca],
                    'ward_id': self.ward_location
                })
            else:
                return mock_allocation_wizard_browse.origin(*args, **kwargs)

        def mock_allocating_browse(*args, **kwargs):
            context = kwargs.get('context')
            if context and 'complete_test' in context:
                if context == 'complete_test_dual_role':
                    return self.allocating_pool.new(cr, uid, {
                        'nurse_id': uid,
                        'hca_ids': [self.hca],
                        'location_id': self.location
                    })
                return self.allocating_pool.new(cr, uid, {
                    'nurse_id': self.nurse,
                    'hca_ids': [self.hca],
                    'location_id': self.location
                })
            else:
                return mock_allocating_browse.origin(*args, **kwargs)

        def mock_responsibility_allocation(*args, **kwargs):
            context = kwargs.get('context')
            if context and context in ['complete_test_resp',
                                       'complete_test_dual_role']:
                self.resp_calls.append((args[3], args[4]))
            return True

        self.allocation_pool._patch_method('browse',
                                           mock_allocation_wizard_browse)
        self.allocating_pool._patch_method('browse', mock_allocating_browse)
        self.allocation_pool._patch_method(
            'responsibility_allocation_activity',
            mock_responsibility_allocation)

    def tearDown(self):
        super(TestStaffReallocationComplete, self).tearDown()
        self.allocation_pool._revert_method('browse')
        self.allocating_pool._revert_method('browse')
        self.allocation_pool._revert_method(
            'responsibility_allocation_activity')

    def test_calls_reallocation(self):
        """
        Test that the calls the responsibility allocation method with the user
        ID and location IDS
        """
        self.resp_calls = []
        self.allocation_pool.complete(self.cr, self.uid, [64],
                                      context='complete_test_resp')
        self.assertEqual(len(self.resp_calls), 3)
        self.assertIn((self.nurse, [self.location]), self.resp_calls)
        self.assertIn((self.hca, [self.location]), self.resp_calls)

    def test_calls_reallocation_dual_role(self):
        """
        Test that the calls the responsibility allocation method with the user
        ID and location IDS but when user is both ward manager and nurse make
        sure it keeps them on the ward and the bed
        """
        self.resp_calls = []
        self.allocation_pool.complete(self.cr, self.uid, [64],
                                      context='complete_test_dual_role')
        self.assertEqual(len(self.resp_calls), 2)
        self.assertIn((self.uid, [self.location, self.ward_location]),
                      self.resp_calls)
        self.assertIn((self.hca, [self.location]), self.resp_calls)

    def test_returns_wizard_id(self):
        """
        Test that the submit_wards method returns the wizard ID to the frontend
        so it can be passed to the next part of the wizard
        """
        wizard_test = self.allocation_pool.complete(
            self.cr, self.uid, [64], context='complete_test')
        self.assertEqual(wizard_test, {'type': 'ir.actions.act_window_close'})

    def test_errors_on_bad_id(self):
        """
        Method should error when passed an ID that isn't an int
        """
        with self.assertRaises(ValueError) as id_error:
            self.allocation_pool.complete(
                self.cr, self.uid, 'this is a test',
                context='complete_test')
        self.assertEqual(id_error.exception.message,
                         'Invalid ID passed to complete')
