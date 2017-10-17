# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestCalculateBmi(TransactionCase):

    def setUp(self):
        super(TestCalculateBmi, self).setUp()
        self.weight_model = self.env['nh.clinical.patient.observation.weight']

    def test_bmi_rounded_to_1_decimal_place(self):
        actual = round(self.weight_model.calculate_bmi(74.6, 1.75), 1)
        expected = 24.4
        self.assertEqual(expected, actual)

        actual = round(self.weight_model.calculate_bmi(25.1, 10000.6), 1)
        expected = 0.0
        self.assertEqual(expected, actual)

    def test_many_decimal_places(self):
        actual = round(
            self.weight_model.calculate_bmi(74.6666666666, 1.5555555555), 1
        )
        expected = 30.9
        self.assertEqual(expected, actual)

    def test_integer_values(self):
        actual = round(self.weight_model.calculate_bmi(83, 2), 1)
        expected = 20.8
        self.assertEqual(expected, actual)

    def test_0_height_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.weight_model.calculate_bmi(75.5, 0.0)

    def test_one_int_one_float(self):
        actual = round(self.weight_model.calculate_bmi(67, 1.28), 1)
        expected = 40.9
        self.assertEqual(expected, actual)
