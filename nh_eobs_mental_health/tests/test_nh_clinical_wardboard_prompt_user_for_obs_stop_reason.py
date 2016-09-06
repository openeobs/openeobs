# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestNhClinicalWardBoardPromptUserForObsStopReason(TransactionCase):

    def setUp(self):
        super(TestNhClinicalWardBoardPromptUserForObsStopReason, self).setUp()

    def test_returns_action_dictionary(self):
        pme_model = self.env['nh.clinical.wardboard']
        action = pme_model.prompt_user_for_obs_stop_reason()
        self.assertTrue(isinstance(action, dict))

    def test_creates_patient_monitoring_exception_record(self):
        pass

    def test_raises_exception_when_more_than_one_reason(self):
        pass