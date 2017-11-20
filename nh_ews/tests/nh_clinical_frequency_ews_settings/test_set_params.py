# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestSetParams(TransactionCase):
    def setUp(self):
        super(TestSetParams, self).setUp()
        self.settings_model = self.env['nh.clinical.frequencies.ews_settings']
        self.config_parameters_model = self.env['ir.config_parameter']

        self.field_names = [
            'no_risk_minimum',
            'low_risk_minimum',
            'medium_risk_minimum',
            'high_risk_minimum',
            'no_risk_maximum',
            'low_risk_maximum',
            'medium_risk_maximum',
            'high_risk_maximum',
            'no_risk',
            'low_risk',
            'medium_risk',
            'high_risk',
            'placement',
            'obs_restart'
        ]

    def call_test(self, values=8, minimum=5, maximum=10):
        self.fields_dict = {
            field_name: values for field_name in self.field_names
        }
        for field_name in self.fields_dict:
            if 'minimum' in field_name:
                self.fields_dict[field_name] = minimum
            elif 'maximum' in field_name:
                self.fields_dict[field_name] = maximum

        settings = self.settings_model.create(self.fields_dict)
        settings.set_params()
        return settings

    def test_execute_creates_parameters_for_each_field(self):
        number_of_parameters = self.config_parameters_model.search_count([])
        number_of_fields = 14

        self.call_test()

        expected = number_of_parameters + number_of_fields
        actual = self.config_parameters_model.search_count([])
        self.assertEqual(expected, actual)

    def test_execute_updates_existing_parameters(self):
        settings = self.call_test(values=8)
        expected_param_values = [str(field_value) for field_value
                                 in self.fields_dict.itervalues()]
        actual_param_values = \
            settings.get_default_params(self.field_names).values()
        self.assertEqual(expected_param_values, actual_param_values)

        self.call_test(values=9)
        expected_param_values = [str(field_value) for field_value
                                 in self.fields_dict.itervalues()]
        actual_param_values = \
            settings.get_default_params(self.field_names).values()
        self.assertEqual(expected_param_values, actual_param_values)

    def test_raises_validation_error_if_a_field_is_below_minimum(self):
        with self.assertRaises(ValidationError):
            self.call_test(values=4)

    def test_raises_validation_error_if_a_field_is_above_maximum(self):
        with self.assertRaises(ValidationError):
            self.call_test(values=11)

    def test_does_not_raise_if_field_value_is_minimum(self):
        self.call_test(values=5)

    def test_does_not_raise_if_field_value_is_maximum(self):
        self.call_test(values=10)
