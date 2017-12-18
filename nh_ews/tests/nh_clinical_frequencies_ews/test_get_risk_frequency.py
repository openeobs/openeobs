# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetRiskFrequency(TransactionCase):
    """
    Tests the `get_risk_frequency` method of the `nh.clinical.frequencies.ews`
    model that is used to get retrieve the frequency for a new EWS based on
    the clinical risk indicated by the previous one.
    """
    def setUp(self):
        super(TestGetRiskFrequency, self).setUp()
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.config_model = self.env['ir.config_parameter']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.convert_case_to_risk_called = False
        self.convert_case_to_risk_case_arg = False
        self.get_param_called = False
        self.get_param_string_arg = None

        def mock_convert_case_to_risk(ews_model, case):
            self.convert_case_to_risk_called = True
            self.convert_case_to_risk_case_arg = case
            return 'Low'
        self.ews_model._patch_method('convert_case_to_risk',
                                     mock_convert_case_to_risk)

        self.expected_frequency = 20

        def mock_get_param(frequencies_model, string, *args):
            self.get_param_called = True
            self.get_param_string_arg = args[0]
            return 20
        self.frequencies_model._patch_method('_get_param', mock_get_param)

    def call_test(self, risk):
        """
        Call the method under test.
        :param risk:
        """
        self.actual_frequency = self.frequencies_model.get_risk_frequency(risk)

    def test_returns_set_values(self):
        """
        The value returned by the method is the same as the one currently in
        the config parameter database table under the 'low_risk' key name.
        """
        self.call_test(risk='low')
        self.assertEqual(self.expected_frequency, self.actual_frequency)

    def test_uses_return_of_convert_case_to_risk_if_int_passed(self):
        """
        If an int is passed as the risk argument then the method passes it to
        the `convert_case_to_risk` method and uses the return of that method
        in the final call to `get_param`.
        """
        expected_case_arg = 1
        expected_get_param_arg = 'low'
        self.call_test(risk=expected_case_arg)
        self.assertTrue(self.convert_case_to_risk_called)
        self.assertTrue(self.get_param_called)
        self.assertEqual(self.convert_case_to_risk_case_arg, expected_case_arg)
        self.assertEqual(self.get_param_string_arg, expected_get_param_arg)

    def test_does_not_call_convert_case_to_risk_if_non_int_passed(self):
        """
        If a non-integer type is passed as the risk argument then the
        `convert_case_to_risk` method is not called as it is not needed. The
        argument can be passed straight to `get_param`.
        """
        self.call_test(risk='low')
        self.assertFalse(self.convert_case_to_risk_called)

    def test_returns_int(self):
        self.call_test(risk=1)
        self.assertTrue(isinstance(self.actual_frequency, int))

    def tearDown(self):
        self.ews_model._revert_method('convert_case_to_risk')
        self.frequencies_model._revert_method('_get_param')
        super(TestGetRiskFrequency, self).tearDown()
