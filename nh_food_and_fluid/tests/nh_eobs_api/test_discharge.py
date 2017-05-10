# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestDischarge(TransactionCase):
    def setUp(self):
        super(TestDischarge, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.f_and_f_review_activity = \
            self.test_utils.create_f_and_f_review_activity()

    def call_test(self):
        api_model = self.env['nh.eobs.api']
        data = {
            'family_name': 'Snow',
            'given_name': 'Jon',
            'location': self.test_utils.ward.code
        }
        api_model.discharge(self.patient.other_identifier, data)

    def test_cancels_f_and_f_review_task(self):
        self.assertEqual('new', self.f_and_f_review_activity.state)
        self.call_test()
        self.assertEqual('cancelled', self.f_and_f_review_activity.state)

    def test_sets_cancel_reason_to_discharge(self):
        self.assertFalse(self.f_and_f_review_activity.cancel_reason_id)

        self.call_test()

        cancel_reason_discharge = self.test_utils.browse_ref(
            'nh_clinical.cancel_reason_discharge')
        expected = cancel_reason_discharge.id
        actual = self.f_and_f_review_activity.cancel_reason_id.id
        self.assertEqual(expected, actual)

    def test_only_cancels_tasks_for_patients_spell(self):
        self.test_utils.create_patient_and_spell()
        f_and_f_review_activity_2 = self.test_utils\
            .create_f_and_f_review_activity(
                self.test_utils.spell_activity)

        self.call_test()

        expected = {
            'spell_1': 'cancelled',
            'spell_2': 'new'
        }
        actual = {
            'spell_1': self.f_and_f_review_activity.state,
            'spell_2': f_and_f_review_activity_2.state
        }
        self.assertEqual(expected, actual)
