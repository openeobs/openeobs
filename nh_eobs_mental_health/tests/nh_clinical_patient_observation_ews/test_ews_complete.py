from openerp.tests import SavepointCase

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data


class TestComplete(SavepointCase):
    """
    Test that the complete method of the nh.clinical.patient.observation.ews
    model schedules a cron to call the 'schedule_clinical_review_notification'
    method in X days depending on the clinical risk of the patient.
    """

    def setUp(self):
        super(TestComplete, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.cron_model = self.env['ir.cron']

    def call_test(self,
                  risk=None,
                  expected_days_til_clinical_review_triggers=None):
        if risk != 'unknown':
            self.test_utils_model.get_open_obs()
            obs_data = self.test_utils_model._get_risk_data(risk)
            self.test_utils_model.complete_obs(obs_data)
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.REFUSED_DATA)

        self._assert_cron_interval(expected_days_til_clinical_review_triggers)

    def _get_latest_cron(self):
        cron = self.cron_model.search([
            ('name', 'like', 'Clinical Review')
        ], order='id desc', limit=1)
        return cron

    def _assert_cron_interval(self,
                              expected_days_til_clinical_review_triggers=None):
        cron = self._get_latest_cron()
        actual_days_til_clinical_review_triggers = cron.interval_number
        self.assertEqual(expected_days_til_clinical_review_triggers,
                         actual_days_til_clinical_review_triggers)

    def test_schedules_clinical_review_cron_in_7_day_no(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with no clinical risk results in an ir.cron being set up
        to call schedule_clinical_review_notification in 7 days.
        """
        self.call_test(risk='no', expected_days_til_clinical_review_triggers=7)

    def test_schedules_clinical_review_cron_in_7_day_low(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with low clinical risk results in an ir.cron being set up
        to call schedule_clinical_review_notification in 7 days.
        """
        self.call_test(risk='low',
                       expected_days_til_clinical_review_triggers=7)

    def test_schedules_clinical_review_cron_in_1_day_med(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with medium clinical risk results in an ir.cron being
        set up to call schedule_clinical_review_notification in 1 day.
        """
        self.call_test(risk='medium',
                       expected_days_til_clinical_review_triggers=1)

    def test_schedules_clinical_review_cron_in_1_day_high(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with high clinical risk results in an ir.cron being
        set up to call schedule_clinical_review_notification in 1 day.
        """
        self.call_test(risk='high',
                       expected_days_til_clinical_review_triggers=1)

    def test_schedules_clinical_review_cron_in_1_day_unknown(self):
        """
        Test that completing a partial observation with the reason 'refused'
        for a patient with unknown clinical risk results in an ir.cron being
        set up to call schedule_clinical_review_notification in 1 day.
        """
        self.call_test(risk='unknown',
                       expected_days_til_clinical_review_triggers=1)

    def test_dont_schedule_clinical_review_cron_if_full(self):
        """
        Test that completing a full observation for a patient results in
        no ir.cron being set up to call schedule_clinical_review_notification.
        """
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.LOW_RISK_DATA)
        cron = self._get_latest_cron()
        self.assertFalse(cron)

    def test_dont_schedule_clinical_review_cron_if_not_refused(self):
        """
        Test that completing a partial observation with a reason that isn't
        refused results in no ir.cron being set up to called
        schedule_clinical_review_notification
        """
        cron = self._get_latest_cron()
        self.assertFalse(cron)

    def test_dont_schedule_clinical_review_cron_is_parent_partial(self):
        """
        Test completing a refused observation for a patient who's already
        considered refusing that no ir.cron being set up to call
        schedule_clinical_review_notification
        """
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.PARTIAL_DATA_ASLEEP)
        cron = self._get_latest_cron()
        self.assertFalse(cron)

    def test_dont_schedule_clinical_review_cron_is_parent_refused(self):
        """
        Test completing a refused observation for a patient who's already
        considered refusing that no ir.cron being set up to call
        schedule_clinical_review_notification
        """
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.REFUSED_DATA)
        cron = self._get_latest_cron()
        self.assertEqual(1, len(cron))

        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.REFUSED_DATA)
        cron = self._get_latest_cron()
        # Still 1 so none was created when patient already in refusal.
        self.assertEqual(1, len(cron))

    def test_dont_schedule_clinical_review_cron_is_parent_full(self):
        """
        Test completing a refused observation for a patient who's not already
        considered refusing that a ir.cron is set up to call
        schedule_clinical_review_notification
        """
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(
            clinical_risk_sample_data.LOW_RISK_DATA)
        cron = self._get_latest_cron()
        self.assertFalse(cron)
