# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class Field(object):
    selection = [
        ('V2', 'V2'),
        ('V1', 'V1'),
        ('V0', 'V0')
    ]


class Model(object):
    _fields = {
        'field1': Field(),
        'field2': Field(),
        'field3': Field()
    }


class TestGetScoreForValue(TransactionCase):

    def setUp(self):
        super(TestGetScoreForValue, self).setUp()
        self.obs_scored_model = \
            self.env['nh.clinical.patient.observation_scored']

    def call_test(self, field_name, field_value, expected_score):
        actual_score = self.obs_scored_model.get_score_for_value(
            Model(), field_name, field_value
        )
        self.assertEqual(expected_score, actual_score)

    def test_score_is_index_of_reversed_selection_list(self):
        self.call_test('field1', 'V0', 0)
        self.call_test('field1', 'V1', 1)
        self.call_test('field1', 'V2', 2)
