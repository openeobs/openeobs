# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase


class TestIsPartial(SingleTransactionCase):

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

    def test_partial_with_only_mandatory_fields_populated(self):
        self.assertFalse(self.neuro_obs.is_partial)

    def test_partial_with_mandatory_and_some_necessary_fields_populated(self):
        self.neuro_obs.pupil_right_size = '1'
        self.neuro_obs.pupil_left_size = '1'
        self.assertFalse(self.neuro_obs.is_partial)

    def test_full_with_all_necessary_fields_populated(self):
        self.neuro_obs.pupil_right_size = '1'
        self.neuro_obs.pupil_left_size = '1'
        self.neuro_obs.pupil_left_reaction = 'sluggish'
        self.neuro_obs.pupil_right_reaction = 'sluggish'
        self.neuro_obs.limb_movement_left_arm = 'normal power'
        self.neuro_obs.limb_movement_right_arm = 'normal power'
        self.neuro_obs.limb_movement_left_leg = 'normal power'
        self.neuro_obs.limb_movement_right_leg = 'normal power'
        self.assertTrue(self.neuro_obs.is_partial)
