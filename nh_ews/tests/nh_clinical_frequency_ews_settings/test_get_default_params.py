# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetDefaultParams(TransactionCase):
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
        self.happy_path_values_2 = {
            'no_risk_minimum': 20,
            'low_risk_minimum': 20,
            'medium_risk_minimum': 20,
            'high_risk_minimum': 20,
            'no_risk_maximum': 20,
            'low_risk_maximum': 20,
            'medium_risk_maximum': 20,
            'high_risk_maximum': 20,
            'no_risk': 20,
            'low_risk': 20,
            'medium_risk': 20,
            'high_risk': 20,
            'placement': 20,
            'obs_restart': 20
        }

    def call_test(self, values=None):
        if not values:
            values = self.happy_path_values
        settings = self.settings_model.create(values)
        settings.set_params()
        return settings

    def test_retrieves_set_values(self):
        settings = self.call_test()
        field_names = self.happy_path_values.iterkeys()
        params = settings.get_default_params(field_names)
        params_equal_to_10 = [param == '10' for param in params.itervalues()]
        self.assertTrue(all(params_equal_to_10))
