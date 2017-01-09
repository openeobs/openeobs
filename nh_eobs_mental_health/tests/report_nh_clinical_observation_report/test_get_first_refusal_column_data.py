# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime

from openerp.tests.common import TransactionCase

from . import patient_refusal_event_fixtures


class TestGetFirstRefusalColumnData(TransactionCase):

    datetime_format = '%d/%m/%Y %H:%M'

    def setUp(self):
        super(TestGetFirstRefusalColumnData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.refusal_episode_fixture = \
            deepcopy(patient_refusal_event_fixtures.refusal_episode_first)

    def call_test(self, arg=False):
        if arg is False:
            arg = self.refusal_episode_fixture
        self.first_refusal_column_data = \
            self.report_model.get_first_refusal_column_data(arg)

    def test_returns_str(self):
        self.call_test()
        self.assertTrue(isinstance(self.first_refusal_column_data, str))

    def test_date_format(self):
        self.call_test()
        datetime.strptime(self.first_refusal_column_data, self.datetime_format)
        # If no exception is raised from parsing, then the format is correct.
