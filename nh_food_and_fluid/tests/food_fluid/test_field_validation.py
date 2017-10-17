# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp.tests.common import SingleTransactionCase


class TestFieldValidation(SingleTransactionCase):
    """
    Test that invalid food and fluid observations cannot be created.

    Not testing enforcement of 'mandatory' fields as that is taken care of
    by Odoo when fields have the 'required' attribute. Just test that required
    attribute is present.
    """
    @classmethod
    def setUpClass(cls):
        super(TestFieldValidation, cls).setUpClass()
        cls.test_utils = cls.env['nh.clinical.test_utils']
        cls.test_utils.create_patient_and_spell()
        cls.test_utils.copy_instance_variables(cls)
        cls.food_and_fluid_model = \
            cls.env['nh.clinical.patient.observation.food_fluid']

        cls.no = cls.food_and_fluid_model._bowels_open_options[0][0]
        cls.yes_measured = cls.food_and_fluid_model._passed_urine_options[0][0]
        cls.yes_not_measured = \
            cls.food_and_fluid_model._passed_urine_options[1][0]

    def test_passed_urine_has_required_attribute(self):
        passed_urine_field = self.food_and_fluid_model._fields['passed_urine']
        self.assertTrue(passed_urine_field.required)

    def test_bowels_open_has_required_attribute(self):
        bowels_open = self.food_and_fluid_model._fields['bowels_open']
        self.assertTrue(bowels_open.required)

    def test_validation_error_when_fluid_output_less_than_min(self):
        with self.assertRaises(ValidationError):
            self.food_and_fluid_model.create({
                'patient_id': self.patient.id,
                'bowels_open': self.no,
                'passed_urine': self.yes_measured,
                'fluid_output': 0
            })

    def test_validation_error_when_fluid_output_negative(self):
        with self.assertRaises(ValidationError):
            self.food_and_fluid_model.create({
                'patient_id': self.patient.id,
                'bowels_open': self.no,
                'passed_urine': self.yes_measured,
                'fluid_output': -1
            })

    def test_validation_error_when_fluid_output_greater_than_max(self):
        with self.assertRaises(ValidationError):
            self.food_and_fluid_model.create({
                'patient_id': self.patient.id,
                'bowels_open': self.no,
                'passed_urine': self.yes_measured,
                'fluid_output': 1000
            })

    def test_no_validation_error_when_fluid_output_is_1(self):
        self.food_and_fluid_model.create({
            'patient_id': self.patient.id,
            'bowels_open': self.no,
            'passed_urine': self.yes_measured,
            'fluid_output': 1
        })

    def test_no_validation_error_when_fluid_output_is_999(self):
        self.food_and_fluid_model.create({
            'patient_id': self.patient.id,
            'bowels_open': self.no,
            'passed_urine': self.yes_measured,
            'fluid_output': 999
        })
