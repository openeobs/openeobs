# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetDefaultParams(TransactionCase):
    """
    Tests the `get_default_params` method of the `nh.clinical.frequencies.ews`.
    """
    def setUp(self):
        super(TestGetDefaultParams, self).setUp()
        self.settings_model = self.env['nh.clinical.frequencies.ews_settings']
        self.config_parameters_model = self.env['ir.config_parameter']

        self.happy_path_values = {
            'no_risk_minimum': 10,
            'low_risk_minimum': 10,
            'medium_risk_minimum': 10,
            'high_risk_minimum': 10,
            'no_risk_maximum': 10,
            'low_risk_maximum': 10,
            'medium_risk_maximum': 10,
            'high_risk_maximum': 10,
            'no_risk': 10,
            'low_risk': 10,
            'medium_risk': 10,
            'high_risk': 10,
            'placement': 10,
            'obs_restart': 10
        }

    def call_test(self, values):
        settings = self.settings_model.create(values)
        settings.set_params()
        return settings

    def test_retrieves_set_values(self):
        """
        The method returns the values that have previously been set by
        calling `set_param`.
        """
        settings = self.call_test(values=self.happy_path_values)
        field_names = self.happy_path_values.iterkeys()
        params = settings.get_default_params(field_names)
        params_equal_to_10 = [param == '10' for param in params.itervalues()]
        self.assertTrue(all(params_equal_to_10))
