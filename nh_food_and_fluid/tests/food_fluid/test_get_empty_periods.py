# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetEmptyPeriods(TransactionCase):
    def setUp(self):
        super(TestGetEmptyPeriods, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)

        self.datetime_utils = self.env['datetime_utils']

        self.now = datetime(2017, 8, 10, 11, 30)

        def mock_get_current_time(*args, **kwargs):
            return self.now
        self.datetime_utils._patch_method('get_current_time',
                                          mock_get_current_time)

    def tearDown(self):
        self.datetime_utils._revert_method('get_current_time')
        super(TestGetEmptyPeriods, self).tearDown()

    def _create_three_food_and_fluid_obs(self):
        self.period_1_start_datetime = datetime(2017, 8, 1, 7, 0, 0)
        self.period_2_start_datetime = datetime(2017, 8, 4, 7, 0, 0)
        self.period_3_start_datetime = datetime(2017, 8, 8, 7, 0, 0)
        self.period_1_start_datetime_str = \
            self.period_1_start_datetime.strftime(DTF)
        self.period_2_start_datetime_str = \
            self.period_2_start_datetime.strftime(DTF)
        self.period_3_start_datetime_str = \
            self.period_3_start_datetime.strftime(DTF)

        self.expected_empty_periods = [
            {
                'period_start_datetime': '2017-08-02 07:00:00',
                'period_end_datetime': '2017-08-04 07:00:00'
            },
            {
                'period_start_datetime': '2017-08-05 07:00:00',
                'period_end_datetime': '2017-08-08 07:00:00'
            },
            {
                'period_start_datetime': '2017-08-09 07:00:00',
                'period_end_datetime': '2017-08-10 07:00:00'
            }
        ]

        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=self.period_1_start_datetime)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=self.period_2_start_datetime)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=self.period_3_start_datetime)

    def call_test(self, create_obs=True, period_dictionaries=None):
        if create_obs:
            self._create_three_food_and_fluid_obs()

        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        domain = [('patient_id', '=', self.patient.id)]
        food_and_fluid_obs = self.food_and_fluid_model.search(
            domain, order='date_terminated desc').read()

        if period_dictionaries is None:
            period_dictionaries = self.food_and_fluid_model \
                .get_period_dictionaries(food_and_fluid_obs)

        self.actual_empty_periods = self.food_and_fluid_model \
            .get_empty_periods(period_dictionaries)

    def test_returns_list_of_dictionaries(self):
        self.call_test()

        self.assertTrue(isinstance(self.actual_empty_periods, list))

        expected = [True] * len(self.actual_empty_periods)
        actual = map(lambda p: isinstance(p, dict), self.actual_empty_periods)
        self.assertEqual(expected, actual)

    def test_dictionaries_have_period_start_datetime_key(self):
        self.call_test()

        for empty_period in self.actual_empty_periods:
            self.assertTrue('period_start_datetime' in empty_period)

    def test_dictionaries_have_period_end_datetime_key(self):
        self.call_test()

        for empty_period in self.actual_empty_periods:
            self.assertTrue('period_start_datetime' in empty_period)

    def test_no_empty_periods_from_before_earliest_passed_period(self):
        self.call_test()

        earliest_period_start_datetime = self.period_1_start_datetime
        for empty_period in self.actual_empty_periods:
            period_start_datetime = empty_period['period_start_datetime']
            period_start_datetime = datetime.strptime(period_start_datetime,
                                                      DTF)
            self.assertGreater(period_start_datetime,
                               earliest_period_start_datetime)

    def test_correct_number_of_empty_period_entries(self):
        """
        Contiguous entry periods should collapse into one another.
        """
        self.call_test()

        self.assertEqual(3, len(self.actual_empty_periods))

    def test_currently_active_empty_period_is_not_shown(self):
        self.call_test()

        actual_period_start_datetimes = [p['period_start_datetime']
                                         for p in self.actual_empty_periods]
        for date_time in actual_period_start_datetimes:
            self.assertNotEqual('2017-05-10 07:00', date_time)

    def test_datetimes_for_consecutive_empty_periods(self):
        """
        Consecutive empty periods 'collapse' into one entry with the 'start'
        datetime of the first period and the 'end' datetime of the last period.
        """
        self.call_test()

        self.assertEqual(self.expected_empty_periods,
                         self.actual_empty_periods)

    def test_periods_are_in_chronological_order(self):
        self.call_test()

        expected_period_start_datetimes = [p['period_start_datetime'] for p
                                           in self.expected_empty_periods]
        actual_period_start_datetimes = [p['period_start_datetime'] for p
                                         in self.actual_empty_periods]
        self.assertEqual(expected_period_start_datetimes,
                         actual_period_start_datetimes)

    def test_only_one_period_with_obs(self):
        two_days_ago = self.now - timedelta(days=2)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=two_days_ago)

        self.call_test(create_obs=False)

        expected = [{
            'period_start_datetime': '2017-08-09 07:00:00',
            'period_end_datetime': '2017-08-10 07:00:00'
        }]
        actual = self.actual_empty_periods
        self.assertEqual(expected, actual)

    def test_only_one_period_with_obs_directly_before_active(self):
        one_day_ago = self.now - timedelta(days=1)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=one_day_ago)

        self.call_test(create_obs=False)

        expected = []
        actual = self.actual_empty_periods
        self.assertEqual(expected, actual)

    def test_only_active_period_has_obs(self):
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            completion_datetime=self.now)

        self.call_test(create_obs=False)

        expected = []
        actual = self.actual_empty_periods
        self.assertEqual(expected, actual)

    def test_no_food_and_fluid_obs(self):
        self.call_test(create_obs=False, period_dictionaries=[])

        expected = []
        actual = self.actual_empty_periods
        self.assertEqual(expected, actual)
