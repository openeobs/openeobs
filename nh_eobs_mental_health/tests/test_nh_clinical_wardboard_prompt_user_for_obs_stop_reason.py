# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestNhClinicalWardBoardPromptUserForObsStopReason(TransactionCase):

    def setUp(self):
        super(TestNhClinicalWardBoardPromptUserForObsStopReason, self).setUp()

    def test_returns_dictionary(self):
        pme_model = self.env['nh.clinical.wardboard']
        action = pme_model.prompt_user_for_obs_stop_reason()
        self.assertTrue(isinstance(action, dict))

