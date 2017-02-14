# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetReportData(TransactionCase):

    def setUp(self):
        super(TestGetReportData, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.datetime_start = datetime.now() - timedelta(days=2)
        self.datetime_end = datetime.now() - timedelta(days=1)

        self.report_wizard = self.report_wizard_model.create({
            'start_time': self.datetime_start.strftime(DTF),
            'end_time': self.datetime_end.strftime(DTF)
        })
        self.report_wizard.spell_id = self.spell.id

    def test_returns_dict_with_neurological_key_with_list_value(self):
        report_data = self.report_model.get_report_data(self.report_wizard)
        self.assertTrue('neurological' in report_data)
        self.assertTrue(type(report_data['neurological']) is list)
