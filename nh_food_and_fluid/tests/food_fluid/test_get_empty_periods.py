# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetEmptyPeriods(TransactionCase):
    def setUp(self):
        super(TestGetEmptyPeriods, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)

        self.period_1_start_datetime = datetime(2017, 8, 1, 7, 0, 0)
        self.period_2_start_datetime = datetime(2017, 8, 4, 7, 0, 0)
        self.period_3_start_datetime = datetime(2017, 8, 8, 7, 0, 0)
        self.period_1_start_datetime_str = \
            self.period_1_start_datetime.strftime(DTF)
        self.period_2_start_datetime_str = \
            self.period_2_start_datetime.strftime(DTF)
        self.period_3_start_datetime_str = \
            self.period_3_start_datetime.strftime(DTF)

        self.empty_period_start_datetimes_chronological = [
            datetime(2017, 8, 2, 7, 0, 0).strftime(DTF),
            datetime(2017, 8, 3, 7, 0, 0).strftime(DTF),
            datetime(2017, 8, 5, 7, 0, 0).strftime(DTF),
            datetime(2017, 8, 6, 7, 0, 0).strftime(DTF),
            datetime(2017, 8, 7, 7, 0, 0).strftime(DTF)
        ]

        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=self.period_1_start_datetime)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=self.period_2_start_datetime)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=self.period_3_start_datetime)

        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        food_and_fluid_obs = self.food_and_fluid_model.search([]).read()
        period_dictionaries = self.food_and_fluid_model\
            .get_period_dictionaries(food_and_fluid_obs)

        self.empty_periods = self.food_and_fluid_model.get_empty_periods(
            period_dictionaries)

    def test_returns_list_of_dictionaries(self):
        self.assertTrue(isinstance(self.empty_periods, list))

        expected = [True] * len(self.empty_periods)
        actual = map(lambda p: isinstance(p, dict), self.empty_periods)
        self.assertEqual(expected, actual)

    def test_dictionaries_have_period_start_datetime_key(self):
        for empty_period in self.empty_periods:
            self.assertTrue('period_start_datetime' in empty_period)

    def test_dictionaries_have_period_end_datetime_key(self):
        for empty_period in self.empty_periods:
            self.assertTrue('period_start_datetime' in empty_period)

    def test_no_empty_periods_from_before_earliest_passed_period(self):
        earliest_period_start_datetime = self.period_1_start_datetime
        for empty_period in self.empty_periods:
            period_start_datetime = empty_period['period_start_datetime']
            period_start_datetime = datetime.strptime(period_start_datetime,
                                                      DTF)
            self.assertGreater(period_start_datetime,
                               earliest_period_start_datetime)

    def test_no_empty_periods_from_after_latest_passed_period(self):
        latest_period_start_datetime = self.period_3_start_datetime
        for empty_period in self.empty_periods:
            period_start_datetime = empty_period['period_start_datetime']
            period_start_datetime = datetime.strptime(period_start_datetime, DTF)
            self.assertLess(period_start_datetime, latest_period_start_datetime)

    def test_empty_periods_between_first_and_last_passed_period_included(self):
        expected_period_start_datetimes = \
            self.empty_period_start_datetimes_chronological
        actual_period_start_datetimes = [p['period_start_datetime']
                                         for p in self.empty_periods]
        self.assertItemsEqual(expected_period_start_datetimes,
                              actual_period_start_datetimes)

    def test_periods_are_in_chronological_order(self):
        expected_period_start_datetimes = \
            self.empty_period_start_datetimes_chronological
        actual_period_start_datetimes = [p['period_start_datetime']
                                         for p in self.empty_periods]
        self.assertEqual(expected_period_start_datetimes,
                         actual_period_start_datetimes)
