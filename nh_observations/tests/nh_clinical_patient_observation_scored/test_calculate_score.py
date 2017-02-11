# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestCalculateScore(TransactionCase):

    def setUp(self):
        super(TestCalculateScore, self).setUp()
        self.obs_scored_model = \
            self.env['nh.clinical.patient.observation_scored']

    def call_test(self, record, expected_score):
        actual_score = self.obs_scored_model.calculate_score(
            record, return_dictionary=False
        )
        self.assertEqual(expected_score, actual_score)

    def test_score_is_sum_of_ints_in_dict(self):
        obs_data_dict = {
            'field1': 2,
            'field2': 5,
            'field3': 2,
        }
        self.call_test(obs_data_dict, 9)

    def test_score_is_sum_of_strings_in_dict(self):
        obs_data_dict = {
            'field1': '2',
            'field2': '5',
            'field3': '2',
        }
        self.call_test(obs_data_dict, 9)

    def test_uncastable_types_disregarded_from_score(self):
        obs_data_dict = {
            'field1': '2',
            'field2': "Hello.",
            'field3': '5',
            'field4': [],
            'field5': '4'
        }
        self.call_test(obs_data_dict, 11)
