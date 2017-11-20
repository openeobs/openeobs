# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestExecute(TransactionCase):
    def setUp(self):
        super(TestExecute, self).setUp()
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.settings_model = self.env['nh.clinical.frequencies.ews_settings']

    def calls_set_params(self):
        pass
