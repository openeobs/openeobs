# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestCalculateScore(TransactionCase):

    def setUp(self):
        super(TestCalculateScore, self).setUp()
        self.obs_scored_model = \
            self.env['nh.clinical.patient.observation_scored']

        def mock_get_score_for_value(*args, **kwargs):
            field_value = args[2]
            return field_value[1]  # Number after the 'V'

        self.obs_scored_model._patch_method('get_score_for_value',
                                            mock_get_score_for_value)

    def tearDown(self):
        self.obs_scored_model._revert_method('get_score_for_value')
        super(TestCalculateScore, self).tearDown()

    def call_test(self, data, expected_score):
        actual_score = self.obs_scored_model.calculate_score(
            data, return_dictionary=False
        )
        self.assertEqual(expected_score, actual_score)

    def test_score_is_sum_of_field_values(self):
        obs_data_dict = {
            'field1': 'V0',
            'field2': 'V2',
            'field3': 'V1',
        }
        self.call_test(obs_data_dict, 3)
