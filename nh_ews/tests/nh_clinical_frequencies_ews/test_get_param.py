# -*- coding: utf-8 -*-
"""
Module containing the TestGetParam class.
"""
from openerp.tests.common import TransactionCase


class TestGetParam(TransactionCase):
    """
    Tests for the `test_get_param` method of the `nh.clinical.frequencies.ews`
    model.
    """
    def setUp(self):
        """
        Set up the test environment.
        """
        super(TestGetParam, self).setUp()
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.config_model = self.env['ir.config_parameter']

    def call_test(self):
        """
        Call the method under test.
        """
        return self.frequencies_model._get_param('not_an_actual_param')

    def test_raises_if_param_does_not_exist(self):
        """
        Raises an exception if the config parameter specified by the past name
        does not exist.
        """
        with self.assertRaises(ValueError):
            self.call_test()
