# -*- coding: utf-8 -*-
"""
Would have preferred this module to be in nh_observations as that is where the
method under tests is, but need to be able to create observation records in
order to test. The earliest place observation records can be created is in
nh_ews because 'nh.clinical.patient.observation' is an abstract model.
"""
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestCurrentPatientRefusalWasTriggeredBy(TransactionCase):
    """
    Test whether or not a patient's current refusal was triggered by the
    refused obs activity passed.
    """

    def setUp(self):
        super(TestCurrentPatientRefusalWasTriggeredBy, self).setUp()
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        self.location_model = self.env['nh.clinical.location']
        self.activity_model = self.env['nh.activity']
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()

        self.spell_activity_id = self.test_utils_model.spell_activity_id
        self.patient = self.test_utils_model.patient

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

    def test_full_obs_since_first_refused_obs(self):
        """
        Test when a full obs has occurred since the first refused obs.
        """
        self.test_utils_model.complete_obs(
            self.spell_activity_id, clinical_risk_sample_data.LOW_RISK_DATA
        )
        self.assertFalse(
            self.ews_model.current_patient_refusal_was_triggered_by(
                self.refused_obs_activity
            )
        )

    def test_partial_obs_since_first_refused_obs(self):
        """
        Test when a partial obs has occurred since the first refused obs.
        """
        self.test_utils_model.complete_obs(
            self.spell_activity_id,
            clinical_risk_sample_data.PARTIAL_DATA_AWAY_FROM_BED
        )
        self.assertTrue(
            self.ews_model.current_patient_refusal_was_triggered_by(
                self.refused_obs_activity
            )
        )

    def test_transfer_since_last_refused(self):
        """
        Test transfer since the last refused observation.
        """
        self.location_model = self.env['nh.clinical.location']
        self.test_utils_model.search_for_hospital_and_pos()
        self.hospital = self.test_utils_model.hospital
        self.ward = self.location_model.new({
            'name': 'Ward A',
            'code': 'WA',
            'usage': 'ward',
            'parent_id': self.hospital.id,
            'type': 'poc'
        })

        api_model = self.env['nh.clinical.api']
        hospital_number = self.patient.other_identifier
        data = {'location': self.ward.code}
        api_model.transfer(hospital_number, data)

        self.assertFalse(
            self.ews_model.current_patient_refusal_was_triggered_by(
                self.refused_obs_activity
            )
        )
