# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestIsPartial(SingleTransactionCase):
    """
    Testing
    """
    def setUp(self):
        self.neuro_model = \
            self.env['nh.clinical.patient.observation.neurological']
        self.neuro_test_model = \
            self.env['nh.clinical.test.neurological.common']

        eyes_valid_value = \
            self.neuro_test_model.get_valid_value_for_field('eyes')
        verbal_valid_value = \
            self.neuro_test_model.get_valid_value_for_field('verbal')
        motor_valid_value = \
            self.neuro_test_model.get_valid_value_for_field('motor')

        self.neuro_obs = self.neuro_model.new({
            'eyes': eyes_valid_value,
            'verbal': verbal_valid_value,
            'motor': motor_valid_value
        })

    def test_full_with_mandatory_fields_populated(self):
        eyes_valid_value = \
            self.neuro_test_model.get_valid_value_for_field('eyes')
        verbal_valid_value = \
            self.neuro_test_model.get_valid_value_for_field('verbal')
        motor_valid_value = \
            self.neuro_test_model.get_valid_value_for_field('motor')

        self.neuro_obs.eyes = eyes_valid_value
        self.neuro_obs.verbal = verbal_valid_value
        self.neuro_obs.motor = motor_valid_value

        self.assertTrue(self.neuro_obs.is_partial)

    def test_partial_with_no_mandatory_fields_populated(self):
        pass

    def test_partial_with_one_mandatory_field_populated(self):
        pass

    def test_partial_with_all_optional_fields_populated(self):
        pass

    def test_partial_with_no_fields_populated(self):
        pass
