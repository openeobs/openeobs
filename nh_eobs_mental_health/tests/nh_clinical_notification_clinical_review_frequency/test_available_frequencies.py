# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestAvailableFrequencies(TransactionCase):
    """
    Tests that the correct frequencies are available for selection in a
    clinical risk frequency notification depending on the patients current
    clinical risk.
    """
    def setUp(self):
        super(TestAvailableFrequencies, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.test_utils_model \
            .create_patient_and_spell_and_complete_clinical_review()
        self.clinical_review_frequency_notification = \
            self.test_utils_model.clinical_review_frequency_notification

        triggered_ids_domain = [
            ('creator_id', '=', self.clinical_review_notification_activity.id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=',
             'nh.clinical.notification.clinical_review_frequency')
        ]
        self.triggered_ids = self.activity_model.search(triggered_ids_domain)
        self.clinical_review_frequency_notification_activity = \
            self.triggered_ids[0]
        self.clinical_review_frequency_notification = \
            self.clinical_review_frequency_notification_activity.data_ref

    def test_available_frequencies(self):
        """
        Patch method to return clinical risk required for test then get form
        description and check correct frequencies are present.

        :param risk:
        :return:
        """
        form_description = self.clinical_review_frequency_notification \
            .get_form_description(None)
        expected_frequencies = \
            self.clinical_review_frequency_model._FREQUENCIES
        actual_frequencies = form_description[0]['selection']
        self.assertEqual(expected_frequencies, actual_frequencies)
