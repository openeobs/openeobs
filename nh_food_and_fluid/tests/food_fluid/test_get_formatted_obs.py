# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.tests.common import TransactionCase


class TestGetFormattedObs(TransactionCase):
    """
    Test `get_food_and_fluid_observations` method in override of
    `report.nh.clinical.observation.report`.
    """
    def setUp(self):
        super(TestGetFormattedObs, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.datetime_utils = self.env['datetime_utils']
        self.activity_model = self.env['nh.activity']

        obs_activity_id = \
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                100, datetime.now()
            )
        obs_activity = self.activity_model.browse(obs_activity_id)
        obs = obs_activity.data_ref
        self.formatted_obs = obs.get_formatted_obs()

    def parse_datetime_string_list(self, datetime_string_list):
        datetime_format = \
            self.datetime_utils.datetime_format_front_end_two_character_year
        datetimes = [datetime.strptime(date_time, datetime_format)
                     for date_time in datetime_string_list]
        return datetimes

    def test_returned_in_reverse_chronological_order(self):
        period_start_datetimes = \
            [period['period_start_datetime'] for period
             in self.formatted_obs]
        actual = self.parse_datetime_string_list(period_start_datetimes)
        expected = sorted(actual, reverse=True)

        self.assertEqual(expected, actual)

    def test_datetimes_format(self):
        """Datetimes are in the correct format for display on the UI."""
        period_start_datetimes = [period['period_start_datetime'] for period in
                                  self.formatted_obs]
        self.parse_datetime_string_list(period_start_datetimes)
