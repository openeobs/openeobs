# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetPeriodDictionaries(TransactionCase):
    """
    Test `get_food_and_fluid_report_data` method in override of
    `report.nh.clinical.observation.report`.
    """
    def setUp(self):
        super(TestGetPeriodDictionaries, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.datetime_utils = self.env['datetime_utils']

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
                fluid_taken=100, fluid_output=100,
                completion_datetime=completion_datetime
            )
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                fluid_taken=100, fluid_output=100,
                completion_datetime=completion_datetime
            )

        obs = self.food_and_fluid_model.read_obs_for_patient(self.patient.id)
        self.period_dictionaries = \
            self.food_and_fluid_model.get_period_dictionaries(obs)

    @staticmethod
    def parse_datetime_string_list(datetime_string_list):
        datetime_format = DTF
        datetimes = [datetime.strptime(date_time, datetime_format)
                     for date_time in datetime_string_list]
        return datetimes

    def test_returns_list_of_dictionaries(self):
        """Returns a list of dictionaries"""
        self.call_test()
        self.assertTrue(isinstance(self.period_dictionaries, list))
        for period in self.period_dictionaries:
            self.assertTrue(isinstance(period, dict))

    def test_number_of_periods(self):
        """Correct number of periods."""
        self.call_test()

        self.assertEqual(3, len(self.period_dictionaries))

    def test_number_of_obs_in_period(self):
        """Correct number of observations in each period."""
        self.call_test()

        for period in self.period_dictionaries:
            observations = period['observations']
            self.assertEqual(2, len(observations))

    def test_empty_period_is_left_out(self):
        """
        Periods in which no observations were performed do not appear in
        the returned dictionary at all.
        """
        self.call_test(skip_iteration=1)

        self.assertEqual(2, len(self.period_dictionaries))

    def test_period_datetimes_are_both_seven_am(self):
        """
        Both start and end datetimes of the period are at 7:00AM on their
        respective days.
        """
        self.call_test()

        period_start_datetimes = [period['period_start_datetime'] for period in
                                  self.period_dictionaries]
        self.parse_datetime_string_list(period_start_datetimes)

    def test_no_duplicate_periods(self):
        """No period is repeated more than once."""
        self.call_test()

        period_start_datetimes = [period['period_start_datetime'] for period in
                                  self.period_dictionaries]
        period_start_datetimes_set = set(period_start_datetimes)

        self.assertEqual(len(period_start_datetimes_set),
                         len(period_start_datetimes))

    def test_fluid_balance_key_exists(self):
        self.call_test()
        for period_dictionary in self.period_dictionaries:
            self.assertTrue('fluid_balance' in period_dictionary)
