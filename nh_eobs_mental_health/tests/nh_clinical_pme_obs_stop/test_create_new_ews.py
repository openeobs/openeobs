# -*- coding: utf-8 -*-
"""
Module containing the TestCreateNewEws task.
"""
from openerp.tests.common import TransactionCase


class TestCreateNewEws(TransactionCase):
    """
    Test `create_new_ews` method of the `nh.clinical.pme.obs_stop` model.
    Used to create a new EWS observation and associated activity when a
    patient comes off of obs stop.
    """
    def setUp(self):
        """
        Setup the test environment.
        """
        super(TestCreateNewEws, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.activity_model = self.env['nh.activity']
        self.obs_stop_model = self.env['nh.clinical.pme.obs_stop']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.activity_obs_stop = self.test_utils.create_activity_obs_stop()
        self.obs_stop = self.activity_obs_stop.data_ref

    def test_new_ews_created(self):
        """
        A new EWS observation is created.
        """
        self.test_utils.get_open_obs()
        ews_before_id = self.test_utils.ews_activity.id

        self.obs_stop.create_new_ews()

        self.test_utils.get_open_obs()
        ews_after_id = self.test_utils.ews_activity.id

        self.assertNotEqual(ews_before_id, ews_after_id)

    def test_ews_due_in_n_minutes_from_config(self):
        """
        The newly created EWS is due in a custom amount of time taken from the
        configuration (key-value pairs stored in the ir_config_parameters
        table).
        """
        config_model = self.env['ir.config_parameter']
        expected_frequency = 240
        config_model.set_param('obs_restart', expected_frequency)

        new_ews_activity_id = self.obs_stop.create_new_ews()
        ews_record = self.activity_model.browse(new_ews_activity_id).data_ref
        actual_frequency = ews_record.frequency

        self.assertEqual(expected_frequency, actual_frequency)
