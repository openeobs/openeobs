# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.tests.common import TransactionCase


class TestCalculateFluidBalance(TransactionCase):

    def setUp(self):
        super(TestCalculateFluidBalance, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.datetime_utils = self.env['datetime_utils']

    def call_test(self):
        self.obs = self.food_and_fluid_model.read_obs_for_patient(
            self.patient.id)
        self.now = datetime.now()
        self.fluid_balance = self.food_and_fluid_model.calculate_fluid_balance(
            self.spell_activity.id, self.now)

    def test_hyphen_when_no_fluid_intake_or_output_recorded(self):
        self.call_test()
        self.assertIsNone(self.fluid_balance)

    def test_zero_or_greater_when_only_intake_recorded(self):
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=28)
        self.call_test()
        self.assertGreaterEqual(self.fluid_balance, 0)

    def test_negative_integer_when_only_output_recorded(self):
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_output=49)
        self.call_test()
        self.assertLess(self.fluid_balance, 0)

    def test_balance_is_equal_to_intake_when_only_intake_recorded(self):
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=28)
        self.call_test()
        self.assertEqual(self.fluid_balance, 28)

    def test_balance_is_equal_to_negative_output_when_only_output_recorded(
            self):
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_output=49)
        self.call_test()
        self.assertEqual(self.fluid_balance, -49)

    def test_balance_is_sum_of_intake_and_negative_output(self):
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=100, fluid_output=49)
        self.call_test()
        self.assertEqual(self.fluid_balance, 51)

    def test_balance_is_zero_when_intake_and_output_are_equal(self):
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=49, fluid_output=49)
        self.call_test()
        self.assertEqual(0, self.fluid_balance)

    def test_some_obs_with_output_and_some_without(self):
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=50)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=50)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=50, fluid_output=50)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=50, fluid_output=50)
        self.call_test()
        self.assertEqual(100, self.fluid_balance)
