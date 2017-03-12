# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase


class TestGetFoodAndFluidObservations(TransactionCase):
    """
    Test `get_food_and_fluid_observations` method in override of
    `report.nh.clinical.observation.report`.
    """
    def setUp(self):
        super(TestGetFoodAndFluidObservations, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.report_model = self.env['report.nh.clinical.observation_report']
        self.report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']
        self.datetime_utils = self.env['datetime_utils']

        self.report_wizard = self.report_wizard_model.create({})
        self.report_wizard.spell_id = self.spell.id
        self.report_model.spell_activity_id = self.spell_activity.id

    def call_test(self, period_first_datetime=None, skip_iteration=None):
        """
        Create observations in different periods. By default the first period
        will be yesterday's (so it is not the active period which is in effect
        today) and subsequent periods will be one day earlier than the last.

        :param period_first_datetime:
        :param skip_iteration:
        :return:
        """
        self.period_first_datetime = \
            period_first_datetime if period_first_datetime \
            else datetime.now() - timedelta(days=1)

        for i in range(3):
            if i is skip_iteration:
                continue
            completion_datetime = self.period_first_datetime \
                - timedelta(days=i)
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                100, completion_datetime
            )
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                100, completion_datetime
            )

        self.food_and_fluid_report_data = \
            self.report_model.get_food_and_fluid_observations(
                self.report_wizard
            )

    def parse_datetime_string_list(self, datetime_string_list):
        datetime_format = \
            self.datetime_utils.datetime_format_front_end_two_character_year
        datetimes = [datetime.strptime(date_time, datetime_format)
                     for date_time in datetime_string_list]
        return datetimes

    def test_returns_list_of_dictionaries(self):
        """Returns a list of dictionaries."""
        self.call_test()
        self.assertTrue(isinstance(self.food_and_fluid_report_data, list))
        for period in self.food_and_fluid_report_data:
            self.assertTrue(isinstance(period, dict))

    def test_periods_are_in_chronological_order(self):
        self.call_test()

        period_start_datetimes = \
            [period['period_start_datetime'] for period
             in self.food_and_fluid_report_data]
        actual = self.parse_datetime_string_list(period_start_datetimes)
        expected = sorted(actual)

        self.assertEqual(expected, actual)

    def test_period_datetimes_format(self):
        """Datetimes are in the correct format for display on the reports."""
        self.call_test()

        period_start_datetimes = [period['period_start_datetime'] for period in
                                  self.food_and_fluid_report_data]
        self.parse_datetime_string_list(period_start_datetimes)

    def test_active_period_has_no_total_fluid_intake_value(self):
        """
        If the current period appears on the reports, it has no value for the
        total fluid intake.
        """
        self.call_test(period_first_datetime=datetime.now())

        period_start_datetime = \
            self.food_and_fluid_model.get_period_start_datetime(
                self.period_first_datetime
            )
        period_start_datetime = \
            self.datetime_utils.convert_datetime_str_to_known_format(
                period_start_datetime, self.report_model.pretty_date_format
            )
        active_period = \
            [period for period in self.food_and_fluid_report_data
             if period['period_start_datetime'] == period_start_datetime][0]

        self.assertIsNone(active_period['total_fluid_intake'])

    def test_non_active_periods_have_total_fluid_intake_value(self):
        """
        Periods which are not the currently active one all have an integer
        for their total fluid intake value.
        """
        self.call_test()

        period_start_datetime = \
            self.food_and_fluid_model.get_period_start_datetime(datetime.now())
        period_start_datetime = \
            self.datetime_utils.convert_datetime_str_to_known_format(
                period_start_datetime, self.report_model.pretty_date_format
            )
        non_active_periods = \
            [period for period in self.food_and_fluid_report_data
             if period['period_start_datetime'] != period_start_datetime]

        regex = re.compile(r'\d+ml')
        for period in non_active_periods:
            total_fluid_intake = period['total_fluid_intake']
            match = regex.match(total_fluid_intake)
            self.assertTrue(match)
