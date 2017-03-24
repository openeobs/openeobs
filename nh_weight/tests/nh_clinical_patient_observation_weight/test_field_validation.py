# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestFieldValidation(TransactionCase):

    def setUp(self):
        super(TestFieldValidation, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.weight_model = self.env['nh.clinical.patient.observation.weight']

        self.weight_min = 0.0
        self.weight_max = 500.0

        self.waist_min = 30.0
        self.waist_max = 500.0

    def test_no_values_does_not_raise_exception(self):
        self.weight_model.create({
            'patient_id': self.patient.id
        })

    def test_just_weight_does_not_raise_exception(self):
        self.weight_model.create({
            'patient_id': self.patient.id,
            'weight': self.weight_min + 0.1
        })

    def test_just_waist_does_not_raise_exception(self):
        self.weight_model.create({
            'patient_id': self.patient.id,
            'waist_measurement': self.waist_min + 0.1
        })

    def test_weight_below_min_raises_exception(self):
        with self.assertRaises(ValidationError):
            self.weight_model.create({
                'patient_id': self.patient.id,
                'weight': self.weight_min - 0.1
            })

    def test_weight_above_max_raises_exception(self):
        with self.assertRaises(ValidationError):
            self.weight_model.create({
                'patient_id': self.patient.id,
                'weight': self.weight_max + 0.1
            })

    def test_weight_on_min_does_not_raise_exception(self):
        self.weight_model.create({
            'patient_id': self.patient.id,
            'weight': self.weight_min
        })

    def test_weight_on_max_does_not_raise_exception(self):
        self.weight_model.create({
            'patient_id': self.patient.id,
            'weight': self.weight_max
        })

    def test_waist_below_min_raises_exception(self):
        with self.assertRaises(ValidationError):
            self.weight_model.create({
                'patient_id': self.patient.id,
                'waist_measurement': self.waist_min - 0.1
            })

    def test_waist_above_max_raises_exception(self):
        with self.assertRaises(ValidationError):
            self.weight_model.create({
                'patient_id': self.patient.id,
                'waist_measurement': self.waist_max + 0.1
            })

    def test_waist_on_min_does_not_raise_exception(self):
        self.weight_model.create({
            'patient_id': self.patient.id,
            'waist_measurement': self.weight_min
        })

    def test_waist_on_max_does_not_raise_exception(self):
        self.weight_model.create({
            'patient_id': self.patient.id,
            'waist_measurement': self.waist_max
        })

    def test_weight_with_more_than_one_decimal_place_is_rounded(self):
        obs = self.weight_model.create({
            'patient_id': self.patient.id,
            'weight': 35.999
        })
        self.assertEqual(36.0, obs.weight)
