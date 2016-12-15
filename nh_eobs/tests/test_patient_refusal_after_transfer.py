# -*- coding: utf-8 -*-
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestPatientRefusalAfterTransfer(TransactionCase):

    def setUp(self):
        super(TestPatientRefusalAfterTransfer, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]

        open_obs_activities = self.activity_model.search(self.domain)
        self.first_obs_after_placement = open_obs_activities[0]
        self.assertEqual(len(open_obs_activities), 1)

    def test_obs_frequency_after_refusal_with_unknown_risk(self):
        self.api_model.transfer(self.hospital_number, {'location': 'WB'})
        self.test_utils_model.place_patient()

        obs_activity_after_refusal = \
            self.test_utils_model.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )
        obs_after_refusal = obs_activity_after_refusal.data_ref
        self.assertEqual(obs_after_refusal.frequency, 15)

    def test_obs_frequency_after_refusal_with_no_risk(self):
        self.initial_no_risk_obs_activity = \
            self.test_utils_model.create_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.NO_RISK_DATA
            )

        self.api_model.transfer(self.hospital_number, {'location': 'WB'})
        self.test_utils_model.place_patient()

        obs_activity_after_refusal = \
            self.test_utils_model.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )
        obs_after_refusal = obs_activity_after_refusal.data_ref
        self.assertEqual(obs_after_refusal.frequency, 15)

    def test_obs_frequency_after_refusal_with_medium_risk(self):
        self.initial_medium_risk_obs_activity = \
            self.test_utils_model.create_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.MEDIUM_RISK_DATA
            )

        self.api_model.transfer(self.hospital_number, {'location': 'WB'})
        self.test_utils_model.place_patient()

        obs_activity_after_refusal = \
            self.test_utils_model.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )
        obs_after_refusal = obs_activity_after_refusal.data_ref
        self.assertEqual(obs_after_refusal.frequency, 15)
