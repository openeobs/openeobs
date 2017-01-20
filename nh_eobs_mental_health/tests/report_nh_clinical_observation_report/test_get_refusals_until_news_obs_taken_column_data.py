# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase

from . import patient_refusal_event_fixtures


class TestGetRefusalsUntilNewsObsTakenColumnData(TransactionCase):

    def setUp(self):
        super(TestGetRefusalsUntilNewsObsTakenColumnData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']

    def call_test(self, arg=False):
        if arg is False:
            arg = patient_refusal_event_fixtures.refusal_episode_first
        self.refusals_until_news_obs_taken_column_data = \
            self.report_model.get_refusals_until_news_obs_taken_column_data(
                arg)

    def test_returns_int(self):
        self.call_test()
        self.assertTrue(
            isinstance(self.refusals_until_news_obs_taken_column_data, int)
        )
