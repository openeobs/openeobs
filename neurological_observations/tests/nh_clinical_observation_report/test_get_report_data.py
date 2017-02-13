# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_eobs.report.helpers import DataObj
from openerp.tests.common import TransactionCase


class TestGetReportData(TransactionCase):

    def setUp(self):
        super(TestGetReportData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.datetime_start = datetime.now() + timedelta(days=1)
        self.datetime_end = datetime.now() + timedelta(days=2)
        self.data = DataObj(self.spell_activity.id,
                            self.datetime_start, self.datetime_end)

    def test_returns_dict_with_neurological_key_with_list_value(self):
        report_data = self.report_model.get_report_data()
        self.assertTrue('neurological' in report_data)
        self.assertTrue(type(report_data['neurological']) is list)
