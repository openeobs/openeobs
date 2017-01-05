# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.tests.common import TransactionCase


class TestGetFirstRefusalColumnData(TransactionCase):

    datetime_format = '%d/%m/%Y %H:%M'

    def setUp(self):
        super(TestGetFirstRefusalColumnData, self).setUp()
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
        # mock_refusal_episode_second = {
        #     'count': 1,
        #     'first_refusal_date_terminated': '2017-01-03 17:49:1#3.36621',
        #     'freq_date_terminated': None,
        #     'freq_state': None,
        #     'freq_terminate_uid': None,
        #     'review_date_termninated': None,
        #     'review_state': None,
        #     'review_terminate_uid': None,
        #     'spell_activity_id': 10
        # }
        # mock_refusal_episode_third = {
        #     'count': 1,
        #     'first_refusal_date_terminated': '2017-01-03 17:49:14.36621',
        #     'freq_date_terminated': None,
        #     'freq_state': None,
        #     'freq_terminate_uid': None,
        #     'review_date_termninated': None,
        #     'review_state': None,
        #     'review_terminate_uid': None,
        #     'spell_activity_id': 10
        # }
        # self.mock_refusal_episodes = [
        #     mock_refusal_episode_third,
        #     mock_refusal_episode_first,
        #     mock_refusal_episode_second
        # ]

    def call_test(self, arg=False):
        if arg is False:
            arg = self.mock_refusal_episode
        self.first_refusal_column_data = \
            self.report_model.get_first_refusal_column_data(arg)

    def test_returns_str(self):
        self.call_test()
        self.assertTrue(isinstance(self.first_refusal_column_data, str))

    # def test_number_of_report_entries(self):
    #     self.call_test()
    #     self.assertEqual(len(self.mock_refusal_episodes),
    #                      len(self.first_refusal_column_data))

    def test_date_format(self):
        self.call_test()
        datetime.strptime(self.first_refusal_column_data, self.datetime_format)
        # If no exception is raised from parsing, then the format is correct.

    # def test_date(self):
    #     self.call_test()
    #     expected = datetime.strptime(self.mock_refusal_episodes.keys()[0],
    #                                  self.datetime_format)
    #     actual = datetime.strptime(self.first_refusal_column_data[0],
    #                                self.datetime_format)
    #     self.assertEqual(expected, actual)

    # def test_ordered_chronologically_ascending(self):
    #     self.call_test()
    #     datetime_objects = [datetime.strptime(episode, self.datetime_format)
    #                         for episode in self.first_refusal_column_data]
    #     datetime_objects_sorted = deepcopy(datetime_objects)
    #     sorted(datetime_objects_sorted)
    #
    #     self.assertEqual(datetime_objects,
    #                      datetime_objects_sorted)
    #
    # def test_empty_list_arg_raises_value_error(self):
    #     with self.assertRaises(ValueError):
    #         self.call_test(arg=[])
    #
    # def test_invalid_arg_type_raises_type_error(self):
    #     with self.assertRaises(TypeError):
    #         self.call_test(arg='')
