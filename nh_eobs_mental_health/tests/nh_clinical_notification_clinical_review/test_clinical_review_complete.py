# -*- coding: utf-8 -*-
from openerp.addons.nh_eobs_mental_health.tests.common \
    import test_data_creator_clinical_review
from openerp.tests.common import TransactionCase


class TestComplete(TransactionCase):

    def setUp(self):
        super(TestComplete, self).setUp()
        test_data_creator_clinical_review\
            .create_patient_and_spell_and_complete_clinical_review(self)
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
