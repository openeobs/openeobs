# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetParam(TransactionCase):
    def setUp(self):
        super(TestGetParam, self).setUp()
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.config_model = self.env['ir.config_parameter']

    def call_test(self):
        return self.frequencies_model._get_param('not_an_actual_param')

    def test_raises_if_param_does_not_exist(self):
        with self.assertRaises(ValueError):
            self.call_test()
