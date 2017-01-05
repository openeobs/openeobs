from openerp.tests.common import TransactionCase
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from datetime import datetime
import time


class TestGetRefusalEpisodesClinicalReview(TransactionCase):
    """
    Test the method that collects the refusal episodes for the spell after
    the clinical review task has been triggered
    """

    def setUp(self):
        super(TestGetRefusalEpisodesClinicalReview, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.get_open_obs()
        self.spell_activity_id = self.test_utils_model.spell_activity_id
        self.refused_obs = clinical_risk_sample_data.REFUSED_DATA
        self.partial_obs = clinical_risk_sample_data.PARTIAL_DATA_ASLEEP
        self.full_obs = clinical_risk_sample_data.MEDIUM_RISK_DATA

    def validate_triggered_review(self, values):
        self.assertEqual(values.get('review_state'), 'new')
        self.assertIsNone(values.get('review_date_terminated'))
        self.assertIsNone(values.get('review_terminate_uid'))
        self.assertIsNone(values.get('freq_state'))
        self.assertIsNone(values.get('freq_date_terminated'))
        self.assertIsNone(values.get('freq_terminate_uid'))

    def validate_completed_review(self, values):
        self.assertEqual(values.get('review_state'), 'completed')
        review_date = datetime.strptime(
            values.get('review_date_terminated'), dtf)
        test_date = datetime.utcnow()
        self.assertEqual(review_date.year, test_date.year)
        self.assertEqual(review_date.month, test_date.month)
        self.assertEqual(review_date.day, test_date.day)
        self.assertEqual(review_date.hour, test_date.hour)
        self.assertEqual(review_date.minute, test_date.minute)
        self.assertEqual(
            values.get('review_terminate_uid'),
            self.test_utils_model.doctor.id
        )
        self.assertEqual(values.get('freq_state'), 'new')
        self.assertIsNone(values.get('freq_date_terminated'))
        self.assertIsNone(values.get('freq_terminate_uid'))

    def validate_cancelled_review(self, values):
        self.assertIsNone(values.get('review_state'))
        self.assertIsNone(values.get('review_date_terminated'))
        self.assertIsNone(values.get('review_terminate_uid'))
        self.assertIsNone(values.get('freq_state'))
        self.assertIsNone(values.get('freq_date_terminated'))
        self.assertIsNone(values.get('freq_terminate_uid'))

    def test_no_refusals(self):
        """
        Test that on finding no refusals the method returns an empty array
        """
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertFalse(values)

    def test_refused_triggered(self):
        """
        Test that having a refusal returns a count of 1 and a new clinical
        review task
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.ews_model.schedule_clinical_review_notification(
            self.test_utils_model.ews_activity.id)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_triggered_review(values[0])

    def test_refused_completed(self):
        """
        Test that having a completing the clinical review task triggers the
        freq task
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.ews_model.schedule_clinical_review_notification(
            self.test_utils_model.ews_activity.id)
        self.test_utils_model.find_and_complete_clinical_review()
        values = self.report_model.get_refusal_episodes(
            self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_completed_review(values[0])

    def test_refused_then_full_triggered(self):
        """
        Test that having a refusal and the cron job triggers the clinical
        review
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.full_obs)
        self.ews_model.schedule_clinical_review_notification(ews_id)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_cancelled_review(values[0])

    def test_refused_then_full_completed(self):
        """
        Test that having a completing the clinical review task triggers the
        freq task
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.full_obs)
        self.ews_model.schedule_clinical_review_notification(ews_id)
        values = self.report_model.get_refusal_episodes(
            self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_cancelled_review(values[0])

    def test_refused_then_partial_triggered(self):
        """
        Test that having a refusal then a partial observation returns a
        count of 1 and triggers clinical review
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.partial_obs)
        self.ews_model.schedule_clinical_review_notification(ews_id)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_triggered_review(values[0])

    def test_refused_then_partial_completed(self):
        """
        Test that having a refusal then a partial observation and completing
        clinical review is in the returned dictionary
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.partial_obs)
        self.ews_model.schedule_clinical_review_notification(ews_id)
        self.test_utils_model.find_and_complete_clinical_review(ews_id)
        values = self.report_model.get_refusal_episodes(
            self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_completed_review(values[0])

    def test_refused_then_refused_triggered(self):
        """
        Test that having a refusal then another refusal triggers only one
        clinical review
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.refused_obs)
        self.ews_model.schedule_clinical_review_notification(ews_id)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 2)
        self.validate_triggered_review(values[0])

    def test_refused_then_refused_completed(self):
        """
        Test that having a refusal then another refusal triggers only one
        clinical review
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.refused_obs)
        self.ews_model.schedule_clinical_review_notification(ews_id)
        self.test_utils_model.find_and_complete_clinical_review(ews_id)
        values = self.report_model.get_refusal_episodes(
            self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 2)
        self.validate_completed_review(values[0])

    def test_refused_then_pme_triggered(self):
        """
        Test that having a refusal then a patient monitoring exception
        returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.start_pme()
        self.ews_model.schedule_clinical_review_notification(ews_id)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_cancelled_review(values[0])

    def test_refused_then_pme_and_refused_after_restart_triggered(self):
        """
        Test that having a refusal then a patient monitoring exception
        then a refusal triggers the review for the latest refusal only
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        first_ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.start_pme()
        self.test_utils_model.end_pme()
        time.sleep(2)
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.ews_model.schedule_clinical_review_notification(first_ews_id)
        self.ews_model.schedule_clinical_review_notification(ews_id)
        time.sleep(2)
        values = self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 2)
        self.assertEqual(values[0].get('count'), 1)
        self.assertEqual(values[1].get('count'), 1)
        self.validate_cancelled_review(values[0])
        self.validate_triggered_review(values[1])

    def test_refused_then_pme_and_refused_after_restart_completed(self):
        """
        Test that having a refusal then a patient monitoring exception
        returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        first_ews_id = self.test_utils_model.ews_activity.id
        self.test_utils_model.start_pme()
        self.test_utils_model.end_pme()
        time.sleep(2)
        self.test_utils_model.get_open_obs()
        self.test_utils_model.complete_obs(self.refused_obs)
        ews_id = self.test_utils_model.ews_activity.id
        self.ews_model.schedule_clinical_review_notification(first_ews_id)
        self.ews_model.schedule_clinical_review_notification(ews_id)
        time.sleep(2)
        self.test_utils_model.find_and_complete_clinical_review(ews_id)
        values = self.report_model.get_refusal_episodes(
            self.spell_activity_id)
        self.assertEqual(len(values), 2)
        self.assertEqual(values[0].get('count'), 1)
        self.assertEqual(values[1].get('count'), 1)
        self.validate_cancelled_review(values[0])
        self.validate_completed_review(values[1])


    def test_refused_then_transfer(self):
        """
        Test that having a refusal then a transfer returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.transfer_patient('WB')
        ews_id = self.test_utils_model.ews_activity.id
        self.ews_model.schedule_clinical_review_notification(ews_id)
        values = self.report_model.get_refusal_episodes(
            self.spell_activity_id)
        self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_cancelled_review(values[0])

    def test_refused_then_discharge(self):
        """
        Test that having a refusal then a discharge returns a count of 1
        """
        self.test_utils_model.complete_obs(self.refused_obs)
        self.test_utils_model.discharge_patient()
        ews_id = self.test_utils_model.ews_activity.id
        self.ews_model.schedule_clinical_review_notification(ews_id)
        values = self.report_model.get_refusal_episodes(
            self.spell_activity_id)
        self.report_model.get_refusal_episodes(self.spell_activity_id)
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].get('count'), 1)
        self.validate_cancelled_review(values[0])
