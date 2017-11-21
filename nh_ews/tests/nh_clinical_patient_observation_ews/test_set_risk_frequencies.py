# -*- coding: utf-8 -*-
"""
Module containing the TestSetRiskFrequencies class.
"""
from openerp.tests.common import TransactionCase


class TestSetRiskFrequencies(TransactionCase):
    """
    Tests for the `set_risk_frequencies` method of the
    `nh.clinical.patient.observation.ews` model. Used to retrieve values from
    the configuration and set them on the model for use by various methods.
    """
    def setUp(self):
        """
        Setup the test environment.
        """
        super(TestSetRiskFrequencies, self).setUp()
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

    def test_policy_frequencies_set_from_config(self):
        """
        The frequencies set in the `_POLICY['frequencies']` should be
        identical to what is set in the configuration at the time.
        """
        config_model = self.env['ir.config_parameter']

        expected_no_risk_frequency = config_model.get_param('no_risk')
        expected_low_risk_frequency = config_model.get_param('low_risk')
        expected_medium_risk_frequency = config_model.get_param('medium_risk')
        expected_high_risk_frequency = config_model.get_param('high_risk')
        expected_risk_frequencies = [
            int(expected_no_risk_frequency),
            int(expected_low_risk_frequency),
            int(expected_medium_risk_frequency),
            int(expected_high_risk_frequency)
        ]

        actual_risk_frequencies = self.ews_model._POLICY['frequencies']
        self.assertEqual(expected_risk_frequencies, actual_risk_frequencies)

    def raises_if_parameter_does_not_exist(self):
        pass
