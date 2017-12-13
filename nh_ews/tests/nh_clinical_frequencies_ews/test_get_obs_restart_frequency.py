# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetObsRestartFrequency(TransactionCase):
    def setUp(self):
        super(TestGetObsRestartFrequency, self).setUp()
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.config_model = self.env['ir.config_parameter']

        self.expected_frequency = 54
        self.config_model.set_param(
            'obs_restart_frequency', self.expected_frequency)
        self.actual_frequency = self.frequencies_model.get_obs_restart_frequency()

    def test_returns_value_set_in_config(self):
        self.assertEqual(self.expected_frequency, self.actual_frequency)
