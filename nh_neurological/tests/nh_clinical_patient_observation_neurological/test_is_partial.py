# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestIsPartial(TransactionCase):
    """
    Test logic for deciding whether a Neurological observation is partial
    or full.
    """
    def setUp(self):
        super(TestIsPartial, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
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

        self.neuro_obs = self.neuro_model.create({
            'patient_id': self.test_utils.patient.id,
            'eyes': eyes_valid_value,
            'verbal': verbal_valid_value,
            'motor': motor_valid_value
        })

    def test_partial_with_only_mandatory_fields_populated(self):
        """
        Observation is considered partial when only the mandatory fields are
        filled in (because there are other necessary fields).
        """
        self.assertTrue(self.neuro_obs.is_partial)

    def test_partial_with_mandatory_and_some_necessary_fields_populated(self):
        """
        Observation is considered partial even when some necessary fields
        have been populated in addition to the mandatory ones.
        """
        self.neuro_obs.pupil_right_size = '1'
        self.neuro_obs.pupil_left_size = '1'
        self.assertTrue(self.neuro_obs.is_partial)

    def test_full_with_all_necessary_fields_populated(self):
        """
        Observation is considered full when all the fields have been populated
        (because there are no optional fields for this observation).
        """
        self.neuro_obs.pupil_right_size = '1'
        self.neuro_obs.pupil_left_size = '1'
        self.neuro_obs.pupil_left_reaction = '+'
        self.neuro_obs.pupil_right_reaction = '+'
        self.neuro_obs.limb_movement_left_arm = 'NP'
        self.neuro_obs.limb_movement_right_arm = 'NP'
        self.neuro_obs.limb_movement_left_leg = 'NP'
        self.neuro_obs.limb_movement_right_leg = 'NP'
        self.assertFalse(self.neuro_obs.is_partial)
