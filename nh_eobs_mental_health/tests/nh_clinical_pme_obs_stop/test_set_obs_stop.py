# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestSetObsStop(TransactionCase):

    def setUp(self):
        super(TestSetObsStop, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.obs_stop_model = self.env['nh.clinical.pme.obs_stop']

        self.activity_obs_stop = self.test_utils.create_activity_obs_stop()
        self.obs_stop = self.activity_obs_stop.data_ref

        self.test_utils.get_open_obs()

    def test_sets_obs_stop_field_on_spell(self):
        self.assertFalse(self.spell.obs_stop)
        self.obs_stop.set_obs_stop_flag(True)
        self.assertTrue(self.spell.obs_stop)
