# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestFieldValidation(TransactionCase):

    def setUp(self):
        super(TestFieldValidation, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.blood_glucose_model = \
            self.env['nh.clinical.patient.observation.blood_glucose']

        self.blood_glucose_min = 0.0
        self.blood_glucose_max = 200.0

    def test_no_values_does_not_raise_exception(self):
        self.blood_glucose_model.create({
            'patient_id': self.patient.id
        })

    def test_blood_glucose_below_min_raises_exception(self):
        with self.assertRaises(ValidationError):
            self.blood_glucose_model.create({
                'patient_id': self.patient.id,
                'blood_glucose': self.blood_glucose_min - 0.1
            })

    def test_blood_glucose_above_max_raises_exception(self):
        with self.assertRaises(ValidationError):
            self.blood_glucose_model.create({
                'patient_id': self.patient.id,
                'blood_glucose': self.blood_glucose_max + 0.1
            })

    def test_blood_glucose_on_min_does_not_raise_exception(self):
        self.blood_glucose_model.create({
            'patient_id': self.patient.id,
            'blood_glucose': self.blood_glucose_min
        })

    def test_blood_glucose_on_max_does_not_raise_exception(self):
        self.blood_glucose_model.create({
            'patient_id': self.patient.id,
            'blood_glucose': self.blood_glucose_max
        })

    def test_blood_glucose_with_more_than_one_decimal_place_is_rounded(self):
        obs = self.blood_glucose_model.create({
            'patient_id': self.patient.id,
            'blood_glucose': 35.999
        })
        self.assertEqual(36.0, obs.blood_glucose)
