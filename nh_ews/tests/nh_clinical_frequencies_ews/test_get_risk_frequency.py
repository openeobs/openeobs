# -*- coding: utf-8 -*-
"""
Module containing the TestGetRiskFrequency class.
"""
from openerp.tests.common import TransactionCase


class TestGetRiskFrequency(TransactionCase):
    """
    Tests the `get_risk_frequency` method of the `nh.clinical.frequencies.ews`
    model that is used to get retrieve the frequency for a new EWS based on
    the clinical risk indicated by the previous one.
    """
    convert_case_to_risk_called = False
    get_param_called = True

    def setUp(self):
        """
        Setup the test environment.
        """
        super(TestGetRiskFrequency, self).setUp()
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.config_model = self.env['ir.config_parameter']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        global convert_case_to_risk_called
        global get_param_called
        convert_case_to_risk_called = False
        get_param_called = False

    def call_test(self, risk=1):
        """
        Call the method under test.
        :param risk:
        """
        self.frequency = self.frequencies_model.get_risk_frequency(risk)

    def test_retrieves_set_values(self):
        expected_frequency = int(self.config_model.get_param('low_risk'))
        self.call_test(risk='low')
        self.assertEqual(expected_frequency, self.frequency)

    def test_uses_return_of_convert_case_to_risk_if_int_passed(self):
        def mock_convert_case_to_risk(self, case):
            global convert_case_to_risk_called
            convert_case_to_risk_called = True
            return 'Low'
        self.ews_model._patch_method('convert_case_to_risk',
                                     mock_convert_case_to_risk)

        def mock_get_param(self, string, *args):
            global get_param_called
            get_param_called = True
            return 'Low'
        self.frequencies_model._patch_method('_get_param', mock_get_param)

        try:
            self.call_test()

            self.assertTrue(convert_case_to_risk_called)
            self.assertTrue(get_param_called)
        finally:
            self.ews_model._revert_method('convert_case_to_risk')
            self.frequencies_model._revert_method('_get_param')

    def test_does_not_call_get_case_if_non_int_passed(self):
        def mock_convert_case_to_risk(self, case):
            global convert_case_to_risk_called
            convert_case_to_risk_called = True
            return 'Low'

        self.ews_model._patch_method('convert_case_to_risk',
                                     mock_convert_case_to_risk)

        def mock_get_param(self, string, *args):
            global get_param_called
            get_param_called = True
            return 'Low'

        self.frequencies_model._patch_method('_get_param', mock_get_param)

        try:
            self.call_test(risk='low')
            global convert_case_to_risk_called
            self.assertFalse(convert_case_to_risk_called)
        finally:
            self.ews_model._revert_method('convert_case_to_risk')
            self.frequencies_model._revert_method('_get_param')

    def test_returns_int(self):
        self.call_test()
        self.assertTrue(type(self.frequency) is int)
