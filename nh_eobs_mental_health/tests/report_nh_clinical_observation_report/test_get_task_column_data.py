# -*- coding: utf-8 -*-
from copy import deepcopy

from openerp.tests.common import TransactionCase

from . import patient_refusal_event_fixtures


reformat_server_datetime_called = False
context_with_timezone_kwarg = False


class TestGetTaskColumnData(TransactionCase):

    def setUp(self):
        super(TestGetTaskColumnData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.refusal_episode_fixture = deepcopy(
            patient_refusal_event_fixtures.refusal_episode_review_completed)

    def call_test(self, arg=False):
        if arg is False:
            arg = self.refusal_episode_fixture
        self.first_refusal_column_data = \
            self.report_model.get_task_column_data(arg)

    def test_calls_reformat_server_datetime_for_frontend(self):
        def mock_reformat_server_datetime_for_frontend(*args, **kwargs):
            global reformat_server_datetime_called
            global context_with_timezone_kwarg
            reformat_server_datetime_called = True
            context_with_timezone_kwarg = 'context_with_timezone' in kwargs
            return mock_reformat_server_datetime_for_frontend.origin(
                args[1], **kwargs)

        datetime_utils = self.env['datetime_utils']
        datetime_utils._patch_method(
            'reformat_server_datetime_for_frontend',
            mock_reformat_server_datetime_for_frontend)
        try:
            self.call_test()
        finally:
            datetime_utils._revert_method(
                'reformat_server_datetime_for_frontend')

        self.assertTrue(reformat_server_datetime_called)
        self.assertTrue(context_with_timezone_kwarg)
