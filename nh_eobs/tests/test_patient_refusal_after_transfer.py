# -*- coding: utf-8 -*-
from openerp.addons.nh_eobs.tests.common import test_data_creator
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestPatientRefusalAfterTransfer(TransactionCase):

    def setUp(self):
        super(TestPatientRefusalAfterTransfer, self).setUp()
        test_data_creator.admit_and_place_patient(self)
        self.domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        self.observation_test_utils = self.env['observation_test_utils']

        open_obs_activities = self.activity_model.search(self.domain)
        self.first_obs_after_placement = open_obs_activities[0]
        self.assertEqual(len(open_obs_activities), 1)

    def test_obs_frequency_after_refusal_with_unknown_risk(self):
        self.api_model.transfer(self.hospital_number, {'location': 'WB'})
        test_data_creator.place_patient(self)

        obs_activity_after_refusal = \
            self.observation_test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )
        obs_after_refusal = obs_activity_after_refusal.data_ref
        self.assertEqual(obs_after_refusal.frequency, 15)

    def test_obs_frequency_after_refusal_with_no_risk(self):
        self.initial_no_risk_obs_activity = \
            self.observation_test_utils.create_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.NO_RISK_DATA
            )

        self.api_model.transfer(self.hospital_number, {'location': 'WB'})
        test_data_creator.place_patient(self)

        obs_activity_after_refusal = \
            self.observation_test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )
        obs_after_refusal = obs_activity_after_refusal.data_ref
        self.assertEqual(obs_after_refusal.frequency, 15)


    def test_obs_frequency_after_refusal_with_medium_risk(self):
        self.initial_medium_risk_obs_activity = \
            self.observation_test_utils.create_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.MEDIUM_RISK_DATA
            )

        self.api_model.transfer(self.hospital_number, {'location': 'WB'})
        test_data_creator.place_patient(self)

        obs_activity_after_refusal = \
            self.observation_test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )
        obs_after_refusal = obs_activity_after_refusal.data_ref
        self.assertEqual(obs_after_refusal.frequency, 15)