# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestStartPatientMonitoringException(TransactionCase):
    """
    Test :method:`start_obs_stop` in
    :class:`NHClinicalWardboard<nh_eobs_mental_health.nh_clinical_wardboard>`.
    """
    def setUp(self):
        super(TestStartPatientMonitoringException, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.wardboard_model = self.env['nh.clinical.wardboard']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier',
            'other_identifier': 'an_other_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {'patient_id': self.patient.id, 'pos_id': 1}
        )

        self.spell_activity = self.activity_model.browse(
            self.spell_activity_id
        )

        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient
        })

    def test_raises_error_when_no_reason_given(self):
        """
        Test an error is raised when trying to start a patient monitoring
        exception with no reasons passed.
        :return:
        """
        no_reasons = []
        with self.assertRaises(ValueError):
            self.wardboard.start_obs_stop(
                no_reasons,
                self.spell_activity.id,
                self.spell_activity_id
            )

    def test_raises_error_when_multiple_reasons_given(self):
        """
        Test an error is raised when trying to start a patient monitoring
        exception with multiple reasons passed.
        :return:
        """
        reason_one = self.reason_model.create({'display_text': 'reason one'})
        reason_two = self.reason_model.create({'display_text': 'reason two'})
        multiple_reasons = [reason_one, reason_two]
        with self.assertRaises(ValueError):
            self.wardboard.start_obs_stop(
                multiple_reasons,
                self.spell_activity.id,
                self.spell_activity_id
            )
