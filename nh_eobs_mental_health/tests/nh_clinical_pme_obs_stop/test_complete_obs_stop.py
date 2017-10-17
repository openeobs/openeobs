# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


set_obs_stop_value_arg = None


class TestCompleteObsStop(TransactionCase):

    def setUp(self):
        super(TestCompleteObsStop, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.activity_model = self.env['nh.activity']
        self.obs_stop_model = self.env['nh.clinical.pme.obs_stop']

        self.activity_obs_stop = self.test_utils.create_activity_obs_stop()
        self.obs_stop = self.activity_obs_stop.data_ref

    def test_calls_set_obs_stop(self):
        def mock_set_obs_stop_flag(*args, **kwargs):
            global set_obs_stop_value_arg
            set_obs_stop_value_arg = args[1]
            return mock_set_obs_stop_flag.origin(*args, **kwargs)

        self.obs_stop_model._patch_method('set_obs_stop_flag',
                                          mock_set_obs_stop_flag)

        try:
            self.obs_stop.complete(self.activity_obs_stop.id)
            self.assertFalse(set_obs_stop_value_arg)
        finally:
            self.obs_stop_model._revert_method('set_obs_stop_flag')

    def test_creates_new_ews(self):
        self.test_utils.get_open_obs()
        ews_before_id = self.test_utils.ews_activity.id

        self.obs_stop.complete(self.activity_obs_stop.id)

        self.test_utils.get_open_obs()
        ews_after_id = self.test_utils.ews_activity.id
        self.assertEqual(self.test_utils.ews_activity.state, 'scheduled')
        self.assertNotEqual(ews_before_id, ews_after_id)
