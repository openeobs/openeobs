# -*- coding: utf-8 -*-
from openerp.addons.nh_eobs.tests.common import test_data_creator
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestGetLastFullObs(TransactionCase):

    def setUp(self):
        super(TestGetLastFullObs, self).setUp()
        test_data_creator.admit_and_place_patient(self)

        self.observation_test_utils = self.env['observation_test_utils']

        self.domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]

    def test_returns_full_obs(self):
        self.initial_medium_risk_obs_activity = \
            self.observation_test_utils.create_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.MEDIUM_RISK_DATA
            )
        obs_activity = \
            self.ews_model.get_last_full_obs_activity(self.spell_activity_id)
        self.assertEqual(self.initial_medium_risk_obs_activity.id,
                         obs_activity.id)

    def test_returns_none_when_no_full_obs(self):
        obs_activity = \
            self.ews_model.get_last_full_obs_activity(self.spell_activity_id)
        self.assertEqual(obs_activity,
                         None)

    def test_returns_obs_from_before_transfer_after_placement(
            self):
        self.initial_medium_risk_obs_activity = \
            self.observation_test_utils.create_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.MEDIUM_RISK_DATA
            )

        self.api_model.transfer(self.hospital_number, {'location': 'WB'})
        test_data_creator.place_patient(self)

        obs_activity = \
            self.ews_model.get_last_full_obs_activity(self.spell_activity_id)
        self.assertEqual(self.initial_medium_risk_obs_activity.id,
                         obs_activity.id)

    def test_returns_obs_from_before_transfer_after_placement_and_refusal(
            self):
        self.initial_medium_risk_obs_activity = \
            self.observation_test_utils.create_ews_obs_activity(
                self.patient.id, self.spell_activity_id,
                clinical_risk_sample_data.MEDIUM_RISK_DATA
            )

        self.api_model.transfer(self.hospital_number, {'location': 'WB'})
        test_data_creator.place_patient(self)

        self.partial_obs_activity = \
            self.observation_test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity_id
            )

        obs_activity = \
            self.ews_model.get_last_full_obs_activity(self.spell_activity_id)
        self.assertEqual(self.initial_medium_risk_obs_activity.id,
                         obs_activity.id)
