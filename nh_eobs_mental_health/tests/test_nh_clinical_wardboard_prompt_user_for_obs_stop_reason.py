# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestNhClinicalWardBoardPromptUserForObsStopReason(TransactionCase):

    def setUp(self):
        super(TestNhClinicalWardBoardPromptUserForObsStopReason, self).setUp()

        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.wizard_model = \
            self.env['nh.clinical.patient_monitoring_exception.select_reason']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {'patient_id': self.patient.id, 'pos_id': 1}
        )
        # self.activity = self.activity_model.browse(self.activity_id)
        # self.spell = self.activity.spell_activity_id.data_ref

        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient
        })

    def test_returns_action_dictionary(self):
        action = self.wardboard.prompt_user_for_obs_stop_reason()
        self.assertTrue(isinstance(action, dict))

    def test_creates_wizard(self):
        wizard_count_before = self.wizard_model.search_count([])
        self.wardboard.prompt_user_for_obs_stop_reason()
        wizard_count_after = self.wizard_model.search_count([])
        self.assertEquals(wizard_count_before + 1, wizard_count_after)

    def test_returned_action_has_id_of_wizard_with_patient_name(self):
        action = self.wardboard.prompt_user_for_obs_stop_reason()
        wizard_id = action['res_id']
        wizard = self.wizard_model.browse(wizard_id)
        patient_name = self.patient.given_name + ' ' + self.patient.family_name
        if not wizard.patient_name == patient_name:
            raise AssertionError("Passed ID does not belong to a wizard "
                                 "model.")

    def test_wizard_flag_set_when_patient_has_open_escalation_tasks(self):
        doctor_assessment_model = \
            self.env['nh.clinical.notification.doctor_assessment']
        doctor_assessment_model.create_activity(
            {'spell_activity_id': self.spell_activity_id},
            {}
        )

        action = self.wardboard.prompt_user_for_obs_stop_reason()
        wizard_id = action['res_id']
        wizard = self.wizard_model.browse(wizard_id)

        self.assertTrue(wizard.spell_has_open_escalation_tasks)