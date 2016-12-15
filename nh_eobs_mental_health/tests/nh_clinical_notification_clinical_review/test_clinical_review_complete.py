# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestComplete(TransactionCase):

    def setUp(self):
        super(TestComplete, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model \
            .create_patient_and_spell_and_complete_clinical_review()

        self.clinical_review_notification_activity = \
            self.test_utils_model.clinical_review_notification_activity
        self.nurse = self.test_utils_model.nurse
        self.spell_activity_id = self.test_utils_model.spell_activity_id

        self.activity_model = self.env['nh.activity']
        self.env.uid = self.nurse.id

    def test_triggers_clinical_review_frequency_notification(self):
        domain = [
            ('data_model', '=',
             'nh.clinical.notification.clinical_review_frequency'),
            ('parent_id', '=', self.spell_activity_id),
            ('creator_id', '=',
             self.clinical_review_notification_activity.id)
        ]
        clinical_review_frequency_activities = \
            self.activity_model.search(domain)
        self.assertEqual(len(clinical_review_frequency_activities), 1)
