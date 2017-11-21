# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestSetRiskFrequencies(TransactionCase):

    def setUp(self):
        super(TestSetRiskFrequencies, self).setUp()
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

    def test_policy_frequencies_set_from_config(self):
        config_model = self.env['ir.config_parameter']

        expected_no_risk_frequency = config_model.get_param('no_risk')
        expected_low_risk_frequency = config_model.get_param('low_risk')
        expected_medium_risk_frequency = config_model.get_param('medium_risk')
        expected_high_risk_frequency = config_model.get_param('high_risk')
        expected_risk_frequencies = [
            expected_no_risk_frequency,
            expected_low_risk_frequency,
            expected_medium_risk_frequency,
            expected_high_risk_frequency
        ]

        actual_risk_frequencies = self.ews_model._POLICY['frequencies']
        self.assertEqual(expected_risk_frequencies, actual_risk_frequencies)

    def raises_if_parameter_does_not_exist(self):
        pass
