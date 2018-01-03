# -*- coding: utf-8 -*-
from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.tests.common import TransactionCase


class TestGetRefusalFrequency(TransactionCase):
    def setUp(self):
        super(TestGetRefusalFrequency, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.config_model = self.env['ir.config_parameter']

        self.test_utils.admit_and_place_patient(create_placement=False)
        self.test_utils.copy_instance_variables(self)

    def test_placement_frequency_used(self):
        """
        If a patient has never had a full observation then the 'placement
        frequency' is used (because they have not had a full observation since
        being placed in a bed).
        """
        expected_frequency = 30
        self.config_model.set_param('placement', expected_frequency)
        refused_obs_activity = \
            self.test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity.id)

        actual_frequency = \
            self.frequencies_model.get_refusal_frequency(refused_obs_activity)
        self.assertEqual(expected_frequency, actual_frequency)

    def test_transfer_frequency_used(self):
        """
        If a patient has not had a full observation since being transferred
        then the 'transfer frequency' is used.
        """
        expected_frequency = 15
        self.config_model.set_param('transfer', expected_frequency)
        self.test_utils.transfer_patient(self.test_utils.ward.code)
        refused_obs_activity = \
            self.test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity.id)

        actual_frequency = \
            self.frequencies_model.get_refusal_frequency(refused_obs_activity)
        self.assertEqual(expected_frequency, actual_frequency)

    def test_risk_frequency_used(self):
        """
        If a patient has had a full observation since any special events like
        transfers or obs stops then the ordinary frequency for that risk is
        used.
        """
        expected_frequency = 30
        self.config_model.set_param('no_risk', expected_frequency)
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(clinical_risk_sample_data.NO_RISK_DATA,
                                     self.test_utils.ews_activity.id)
        refused_obs_activity = \
            self.test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity.id)

        actual_frequency = \
            self.frequencies_model.get_refusal_frequency(refused_obs_activity)
        self.assertEqual(expected_frequency, actual_frequency)

    def test_risk_frequency_is_same_as_transfer_frequency(self):
        """
        If a patient has had a full observation since any special events like
        transfers or obs stops then the ordinary frequency for that risk is
        used.
        """
        expected_frequency = 15
        self.config_model.set_param('no_risk', expected_frequency)
        self.config_model.set_param('transfer', expected_frequency)
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(clinical_risk_sample_data.NO_RISK_DATA,
                                     self.test_utils.ews_activity.id)
        refused_obs_activity = \
            self.test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity.id)

        actual_frequency = \
            self.frequencies_model.get_refusal_frequency(refused_obs_activity)
        self.assertEqual(expected_frequency, actual_frequency)

    def test_frequency_capped(self):
        """
        No matter which frequency is used, if it is greater than 24 hours then
        it is capped to 24 hours.
        """
        expected_frequency = 4320
        self.config_model.set_param('no_risk', expected_frequency)
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(clinical_risk_sample_data.NO_RISK_DATA,
                                     self.test_utils.ews_activity.id)
        refused_obs_activity = \
            self.test_utils.refuse_open_obs(
                self.patient.id, self.spell_activity.id)

        expected_frequency = 1440
        actual_frequency = \
            self.frequencies_model.get_refusal_frequency(refused_obs_activity)
        self.assertEqual(expected_frequency, actual_frequency)
