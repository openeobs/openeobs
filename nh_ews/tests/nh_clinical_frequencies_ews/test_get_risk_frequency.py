# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetRiskFrequency(TransactionCase):
    def setUp(self):
        super(TestGetRiskFrequency, self).setUp()
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.config_model = self.env['ir.config_parameter']

    def call_test(self):
        return self.frequencies_model.get_risk_frequency('low')

    def test_retrieves_set_values(self):
        expected_frequency = int(self.config_model.get_param('low_risk'))
        actual_frequency = self.call_test()
        self.assertEqual(expected_frequency, actual_frequency)
