# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetRefusalFrequency(TransactionCase):
    """
    Test override of `get_refusal_frequency` that adds a condition for obs
    """
    def setUp(self):
        super(TestGetRefusalFrequency, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.frequencies_model = self.env['nh.clinical.frequencies.ews']
        self.config_model = self.env['ir.config_parameter']

        self.test_utils.admit_and_place_patient(create_placement=False)
        self.test_utils.copy_instance_variables(self)

        self.config_model.set_param('placement', 30)
        self.config_model.set_param('transfer', 60)
        self.config_model.set_param('obs_restart', 120)
        self.config_model.set_param('no_risk', 240)

    def test_obs_restart_frequency_used(self):
        """
        If a patient has not had a full observation since their obs stop status
        has ended then the 'obs restart frequency' is used.
        """
        expected_frequency = 15
        self.config_model.set_param('obs_restart', expected_frequency)

        self.test_utils.start_pme()
        self.test_utils.end_pme()
        self.patient.follower_ids = [1]
        refused_obs_activity = self.test_utils.refuse_open_obs(
            self.patient.id, self.spell_activity.id)

        actual_frequency = refused_obs_activity.data_ref.frequency
        self.assertEqual(expected_frequency, actual_frequency)
