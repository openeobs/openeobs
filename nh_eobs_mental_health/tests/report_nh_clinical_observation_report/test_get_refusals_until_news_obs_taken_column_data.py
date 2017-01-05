# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetRefusalsUntilNewsObsTakenColumnData(TransactionCase):

    def setUp(self):
        super(TestGetRefusalsUntilNewsObsTakenColumnData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.mock_refusal_episode = {
            'count': 1,
            'first_refusal_date_terminated': '2017-01-03 17:49:11.36621',
            'freq_date_terminated': None,
            'freq_state': None,
            'freq_terminate_uid': None,
            'review_date_terminated': None,
            'review_state': None,
            'review_terminate_uid': None,
            'spell_activity_id': 10
        }

    def call_test(self, arg=False):
        if arg is False:
            arg = self.mock_refusal_episode
        self.refusals_until_news_obs_taken_column_data = \
            self.report_model.get_refusals_until_news_obs_taken_column_data(
                arg)

    def test_returns_int(self):
        self.call_test()
        self.assertTrue(
            isinstance(self.refusals_until_news_obs_taken_column_data, int)
        )
