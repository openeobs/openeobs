# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestTransferCancelsReviewTasks(TransactionCase):
    def setUp(self):
        super(TestTransferCancelsReviewTasks, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.f_and_f_review_activity = \
            self.test_utils.create_f_and_f_review_activity()

    def call_test(self):
        """Override to call `nh_eobs_api.transfer()` instead."""
        self.hospital_number = self.test_utils.hospital_number
        self.env['nh.eobs.api'].transfer(self.hospital_number, {
            'from_location': 'WA',
            'location': 'WB'
        })

    def test_cancels_f_and_f_review_task(self):
        state_before = self.f_and_f_review_activity.state
        self.assertEqual(state_before, 'new')

        self.call_test()

        state_after = self.f_and_f_review_activity.state
        self.assertEqual(state_after, 'cancelled')

    def test_only_cancels_tasks_for_patients_spell(self):
        self.test_utils.create_patient_and_spell()

        f_and_f_review_activity_2 = self.test_utils\
            .create_f_and_f_review_activity(
                spell_activity=self.test_utils.spell_activity)

        self.call_test()

        expected = {
            'spell_1': 'cancelled',
            'spell_2': 'new'
        }
        actual = {
            'spell_1': self.f_and_f_review_activity.state,
            'spell_2': f_and_f_review_activity_2.state
        }
        self.assertDictEqual(expected, actual)

    def test_cancels_with_transfer_reason(self):
        self.assertFalse(self.f_and_f_review_activity.cancel_reason_id)

        self.call_test()

        cancel_reason_transfer = \
            self.test_utils.browse_ref('nh_eobs.cancel_reason_transfer')
        expected = cancel_reason_transfer.id
        actual = self.f_and_f_review_activity.cancel_reason_id.id
        self.assertEqual(expected, actual)
