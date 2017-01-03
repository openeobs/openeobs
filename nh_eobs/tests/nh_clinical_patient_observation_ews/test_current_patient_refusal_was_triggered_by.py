# -*- coding: utf-8 -*-
"""
Extension to nh_ews.tests.nh_clinical_patient_observation
.test_patient_refusal_was_triggered_by for testing patient monitoring
exceptions effect on patient refusals.
"""
from openerp.tests.common import TransactionCase


class TestCurrentPatientRefusalWasTriggeredBy(TransactionCase):
    """
    Test whether or not a patient's current refusal was triggered by the
    refused obs activity passed.
    """

    def setUp(self):
        super(TestCurrentPatientRefusalWasTriggeredBy, self).setUp()
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        self.activity_model = self.env['nh.activity']
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.create_patient_and_spell()

        self.spell_activity_id = self.test_utils_model.spell_activity_id
        self.patient = self.test_utils_model.patient
        self.spell = self.test_utils_model.spell

        self.refused_obs_activity_id = self.ews_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'patient_id': self.patient.id}
        )
        self.refused_obs_activity = self.activity_model.browse(
            self.refused_obs_activity_id
        )
        self.test_utils_model.refuse_open_obs(
            self.patient.id, self.spell_activity_id
        )

    def test_patient_monitoring_exception_since_first_refused_obs(self):
        """
        Test when a patient monitoring exception has started since the first
        refused obs.
        """
        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        pme_activity_id = pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': 1, 'spell': self.spell.id}
        )
        activity_model = self.env['nh.activity']
        activity_model.start(pme_activity_id)
        self.assertFalse(
            self.ews_model.current_patient_refusal_was_triggered_by(
                self.refused_obs_activity
            )
        )
