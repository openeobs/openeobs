# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase


class TestCalculateTotalFluidIntake(TransactionCase):
    """
    Test `nh.clinical.patient.observation.food_fluid` model's
    `calculate_total_fluid_intake()` method.
    """
    def setUp(self):
        super(TestCalculateTotalFluidIntake, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']

    def call_test(self, date_time, expected, spell_activity_id=None):
        if not spell_activity_id:
            spell_activity_id = self.spell_activity.id
        actual = self.food_and_fluid_model.calculate_total_fluid_intake(
            spell_activity_id, date_time
        )
        self.assertEqual(expected, actual)

    def test_no_obs_inside_current_period(self):
        """
        0 returned when there are no observations inside the current period.
        """
        this_period = datetime.now()
        last_period = datetime.now() - timedelta(days=1)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, last_period
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, last_period
        )

        self.call_test(this_period, 0)

    def test_only_obs_inside_current_period(self):
        """
        Correct total returned when there are some observations inside the
        current period.
        """
        now = datetime.now()
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, now
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, now
        )

        self.call_test(now, 200)

    def test_obs_inside_and_outside_current_period(self):
        """
        Correct total returned when there are observation both inside and
        outside the current period.
        """
        now = datetime.now()
        last_period = datetime.now() - timedelta(days=1)
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, now
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, now
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, last_period
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, last_period
        )

        self.call_test(now, 200)

    def test_obs_taken_1_microsecond_before_next_period_is_included(self):
        """
        An observation completed one microsecond before the next period begins
        is still included in the current period and contributes towards the
        total fluid intake.
        """
        twelve_hours_before_next_period = datetime(
            year=2017, month=01, day=30, hour=18, second=59, microsecond=999999
        )
        one_microsecond_before_next_period = datetime(
            year=2017, month=01, day=31, hour=6, second=59, microsecond=999999
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, twelve_hours_before_next_period
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, one_microsecond_before_next_period
        )

        self.call_test(twelve_hours_before_next_period, 200)

    def test_obs_taken_at_0700_is_not_included_in_current_period(self):
        """
        Confirm that an observation taken at exactly 7am is considered part of
        the next period and is therefore does not contribute to the current
        period's total fluid intake.
        """
        twelve_hours_before_next_period = datetime(
            year=2017, month=01, day=30, hour=18, second=59, microsecond=999999
        )
        exactly_seven_am = datetime(
            year=2017, month=01, day=31, hour=7, second=0, microsecond=0
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, twelve_hours_before_next_period
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, exactly_seven_am
        )

        self.call_test(twelve_hours_before_next_period, 100)

    def test_period_crossing_month_boundary(self):
        """
        Total fluid taken correctly handles crossing of month boundaries.
        Before the day was simply being incremented by 1 to get the end of the
        period when was in the next day. This led to a blow up because the day
        was out of range, i.e. 32nd of January is not a real date.
        """
        twelve_hours_before_next_period = datetime(
            year=2017, month=01, day=31, hour=18, second=59, microsecond=999999
        )
        # Calculating total fluid taken for the below observation will involve
        # the period 'overflowing' into the next month.
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, twelve_hours_before_next_period
        )

        self.call_test(twelve_hours_before_next_period, 100)

    def test_open_obs_are_not_included(self):
        """
        Uncompleted observations are never included in the calculation.
        """
        now = datetime.now()
        self.test_utils.create_food_and_fluid_obs_activity(100)

        self.call_test(now, 0)

    def test_null_fluid_taken_values(self):
        """
        Method correctly handles observations that did not have a value
        submitted for the `fluid_taken` field, treating them as `0`.
        """
        now = datetime.now()
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            fluid_taken=None, completion_datetime=now
        )

        self.call_test(now, 0)

    def test_only_obs_on_correct_patient_are_calculated(self):
        """
        Only observations for the passed `patient_id` are used to calculate
        the total.
        """
        now = datetime.now()
        patient_one_id = self.patient.id
        patient_one_spell_activity_id = self.spell_activity.id
        self.test_utils.create_patient_and_spell()
        patient_two_id = self.test_utils.patient.id

        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, now, patient_id=patient_one_id
        )
        self.test_utils.create_and_complete_food_and_fluid_obs_activity(
            100, now, patient_id=patient_two_id
        )

        self.call_test(now, 100,
                       spell_activity_id=patient_one_spell_activity_id)
