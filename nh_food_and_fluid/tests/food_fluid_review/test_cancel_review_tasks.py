# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestCancelReviewTasks(TransactionCase):
    """
    Test the `cancel_review_tasks` method of the
    `nh.clinical.notification.food_fluid_review` model.
    """
    def setUp(self):
        super(TestCancelReviewTasks, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.food_and_fluid_review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.activity_model = self.env['nh.activity']

        self.f_and_f_review_activity_id = \
            self.food_and_fluid_review_model.create_activity(
                {'spell_activity_id': self.spell_activity.id},
                {'patient_id': self.patient.id})
        self.f_and_f_review_activity = self.activity_model.browse(
            self.f_and_f_review_activity_id)

    def call_test(self, spell_activity_id=None):
        cancel_reason = self.browse_ref(
            'nh_eobs.cancel_reason_patient_monitoring_exception')
        self.food_and_fluid_review_model.cancel_review_tasks(
            cancel_reason, spell_activity_id=spell_activity_id)

    def test_state_set_to_cancelled(self):
        """
        Sets state of the food and fluid review activity to 'cancelled'.
        :return:
        """
        state_before = self.f_and_f_review_activity.state
        self.assertEqual(state_before, 'new')

        self.call_test()

        state_after = self.f_and_f_review_activity.state
        self.assertEqual(state_after, 'cancelled')

    def test_applies_passed_cancel_reason(self):
        """
        Sets activity's `cancel_reason_id` field to the ID of the patient
        monitoring exception cancel reason.
        :return:
        """
        self.call_test()
        cancel_reason_pme = self.browse_ref(
            'nh_eobs.cancel_reason_patient_monitoring_exception')
        self.assert_cancel_reason_id(cancel_reason_pme.id)

    def assert_cancel_reason_id(self, expected_cancel_reason_id):
        """
        Asserts that the passed cancel reason ID matches the cancel reason ID
        on the classes food and fluid review activity record.
        :param expected_cancel_reason_id:
        :return:
        """
        self.call_test()
        expected = expected_cancel_reason_id
        actual = self.f_and_f_review_activity.cancel_reason_id.id
        self.assertEqual(expected, actual)

    def test_cancels_review_tasks_for_all_spells(self):
        """
        When no `spell_activity_id` is passed then food and fluid review tasks
        for all spells.
        :return:
        """
        self.test_utils.create_patient_and_spell()
        spell_activity_2_id = self.test_utils.spell_activity.id
        patient_2_id = self.test_utils.patient.id

        f_and_f_review_activity_id_2 = \
            self.food_and_fluid_review_model.create_activity(
                {'spell_activity_id': spell_activity_2_id},
                {'patient_id': patient_2_id})
        f_and_f_review_activity_2 = self.activity_model.browse(
            f_and_f_review_activity_id_2)

        self.call_test()

        expected = {
            'spell_1': 'cancelled',
            'spell_2': 'cancelled'
        }
        actual = {
            'spell_1': self.f_and_f_review_activity.state,
            'spell_2': f_and_f_review_activity_2.state
        }
        self.assertDictEqual(expected, actual)

    def test_cancels_all_review_tasks_for_spell_when_spell_activity_id(self):
        """
        When a `spell_activity_id` is passed then only the open food and fluid
        review tasks for that particular spell are cancelled.
        :return:
        """
        self.test_utils.create_patient_and_spell()

        f_and_f_review_activity_2 = self.test_utils \
            .create_f_and_f_review_activity(
                spell_activity=self.test_utils.spell_activity)

        self.call_test(spell_activity_id=self.spell_activity.id)

        expected = {
            'spell_1': 'cancelled',
            'spell_2': 'new'
        }
        actual = {
            'spell_1': self.f_and_f_review_activity.state,
            'spell_2': f_and_f_review_activity_2.state
        }
        self.assertDictEqual(expected, actual)
