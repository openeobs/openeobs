from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp.addons.nh_ews.tests.common.clinical_risk_sample_data import \
    NO_RISK_DATA


class TestActiveFoodFluidPeriod(TransactionCase):
    """
    Test that the active Food & Fluid Period is calculated
    """

    def setUp(self):
        super(TestActiveFoodFluidPeriod, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.dateutils_model = self.env['datetime_utils']
        self.food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        def patch_get_current_time(*args, **kwargs):
            return datetime(1988, 1, 12, 12, 0, 0)

        self.dateutils_model._patch_method(
            'get_current_time', patch_get_current_time)

    def tearDown(self):
        self.datetutils_model._revert_method('get_current_time')
        super(TestActiveFoodFluidPeriod, self).tearDown()

    def test_second_before_period(self):
        """
        Test that period is not active if last obs was at 06:59:59 that morning
        """
        self.test_utils_model.create_and_complete_food_and_fluid_obs_activity(
            100, 100,
            '1988-01-12 06:59:59', self.patient.id
        )
        self.assertFalse(
            self.food_fluid_model.active_food_fluid_period(
                self.spell_activity.id))

    def test_second_into_period(self):
        """
        Test that period is active if last obs was at 07:00:00 that morning
        """
        self.test_utils_model.create_and_complete_food_and_fluid_obs_activity(
            100, 100,
            '1988-01-12 07:00:00', self.patient.id
        )
        self.assertTrue(
            self.food_fluid_model.active_food_fluid_period(
                self.spell_activity.id)
        )

    def test_second_after_period(self):
        """
        Test that period is not active if last obs was at 07:00:00 the next
        morning
        """
        self.test_utils_model.create_and_complete_food_and_fluid_obs_activity(
            100, 100,
            '1988-01-13 07:00:00', self.patient.id
        )
        self.assertFalse(
            self.food_fluid_model.active_food_fluid_period(
                self.spell_activity.id)
        )

    def test_second_before_period_end(self):
        """
        Test that period is active if last obs was at 06:59:59 the next
        morning
        """
        self.test_utils_model.create_and_complete_food_and_fluid_obs_activity(
            100, 100,
            '1988-01-13 06:59:59', self.patient.id
        )
        self.assertTrue(
            self.food_fluid_model.active_food_fluid_period(
                self.spell_activity.id)
        )

    def test_no_observations_in_period(self):
        """
        Test that period is not active if no observations of any type were
        recorded during that period
        """
        self.assertFalse(
            self.food_fluid_model.active_food_fluid_period(
                self.spell_activity.id)
        )

    def test_other_observation_in_period(self):
        """
        Test that period is not active if observations of other types but
        no food and fluid observations were recorded during that period
        """
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(NO_RISK_DATA)
        self.assertFalse(
            self.food_fluid_model.active_food_fluid_period(
                self.spell_activity.id))
