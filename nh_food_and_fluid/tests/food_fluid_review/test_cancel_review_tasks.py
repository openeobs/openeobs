# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestCancelReviewTasks(TransactionCase):
    def setUp(self):
        super(TestCancelReviewTasks, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)

        self.food_and_fluid_review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.activity_model = self.env['nh.activity']

        self.f_and_review_activity_id = \
            self.food_and_fluid_review_model.create_activity(
                {'spell_activity_id': self.spell_activity.id},
                {'patient_id': self.patient.id})
        self.f_and_review_activity = self.activity_model.browse(
            self.f_and_review_activity_id)

    def call_test(self, cancel_reason=None):
        if not cancel_reason:
            cancel_reason = self.browse_ref(
                'nh_eobs.cancel_reason_patient_monitoring_exception')
        self.food_and_fluid_review_model.cancel_review_tasks(
            self.spell_activity.id, cancel_reason)

    def test_state_set_to_cancelled(self):
        state_before = self.f_and_review_activity.state
        self.assertEqual(state_before, 'new')

        self.call_test()

        state_after = self.f_and_review_activity.state
        self.assertEqual(state_after, 'cancelled')

    def test_cancels_all_tasks(self):
        f_and_review_activity_id_2 = \
            self.food_and_fluid_review_model.create_activity(
                {'spell_activity_id': self.spell_activity.id},
                {'patient_id': self.patient.id})
        f_and_review_activity_2 = self.activity_model.browse(
            f_and_review_activity_id_2)

        states_before = [self.f_and_review_activity.state] + \
                        [f_and_review_activity_2.state]
        self.assertEqual(states_before, ['new'] * 2)

        self.call_test()

        states_after = [self.f_and_review_activity.state] + \
                       [f_and_review_activity_2.state]
        self.assertEqual(states_after, ['cancelled'] * 2)

    def test_applies_passed_cancel_reason(self):
        cancel_reason_pme = self.browse_ref(
            'nh_eobs.cancel_reason_patient_monitoring_exception')
        self.call_test()

        expected = cancel_reason_pme.id
        actual = self.f_and_review_activity.cancel_reason_id.id
        self.assertEqual(expected, actual)
