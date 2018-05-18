# -*- coding: utf-8 -*-
import re

from openerp.tests.common import TransactionCase


class TestGetSubmissionMessage(TransactionCase):
    """Test `get_submission_message` method for food & fluid."""
    def setUp(self):
        super(TestGetSubmissionMessage, self).setUp()
        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.activity_model = self.env['nh.activity']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)

        self.fluid_taken = 100
        self.fluid_output = 120

    def call_test(self, fluid_output=None):
        obs_activity_id = \
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                fluid_taken=self.fluid_taken, fluid_output=self.fluid_output
            )
        self.obs_activity = self.activity_model.browse(obs_activity_id)
        self.obs = self.obs_activity.data_ref

    def test_message_contains_total_fluid_taken(self):
        """
        Message contains total fluid taken in the current period in
        millilitres.
        """
        self.call_test()

        message = self.obs.get_submission_message()
        regex = re.compile(r'(\d+)ml')
        match = regex.search(message)
        self.assertTrue(match)

        fluid_total_actual = match.group(1)
        fluid_total_expected = \
            self.food_and_fluid_model.calculate_total_fluid_intake(
                self.spell_activity.id, self.obs_activity.date_terminated
            )
        self.assertEqual(fluid_total_expected, int(fluid_total_actual))

    def test_message_contains_period_start_datetime(self):
        """
        Message contains the datetime that the current period started with
        correct formatting.
        """
        self.call_test()

        message = self.obs.get_submission_message()
        regex = re.compile(r'\d{2}:\d{2} \d{2}/\d{2}/\d{2}')
        match = regex.search(message)
        self.assertTrue(match)
        period_start_datetime_actual = match.group(0)

        period_start_datetime_expected = \
            self.food_and_fluid_model.get_period_start_datetime(
                self.obs_activity.date_terminated
            )
        period_start_datetime_expected = \
            self.env['datetime_utils'].reformat_server_datetime_for_frontend(
                period_start_datetime_expected, two_character_year=True
            )
        self.assertEqual(period_start_datetime_expected,
                         period_start_datetime_actual)

    def test_message_contains_int_fluid_balance_when_fluid_output(self):
        """Message contains the fluid balance."""
        self.call_test()

        message = self.obs.get_submission_message()
        regex = re.compile(r'Current Fluid Balance: (.+)')
        match = regex.search(message)
        self.assertTrue(match)

        actual = match.group(0)
        expected = '-20ml'
        self.assertEqual(expected, actual)

    def test_message_contains_int_fluid_balance_when_fluid_output2(self):
        # Edited due to name duplication (added number 2)
        """Message contains the fluid balance."""
        self.fluid_taken = 0
        self.fluid_output = None
        self.call_test()

        message = self.obs.get_submission_message()
        regex = re.compile(r'Current Fluid Balance: (.+)')
        match = regex.search(message)
        self.assertTrue(match)

        actual = match.group(1)
        expected = '-'
        self.assertEqual(expected, actual)

    def test_open_obs_raises_value_error(self):
        obs_activity_id = \
            self.test_utils.create_food_and_fluid_obs_activity(100)
        obs_activity = \
            self.activity_model.browse(obs_activity_id)
        obs_activity.state = 'started'

        obs = obs_activity.data_ref
        with self.assertRaises(ValueError):
            obs.get_submission_message()
