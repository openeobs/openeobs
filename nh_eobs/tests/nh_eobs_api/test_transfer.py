# -*- coding: utf-8 -*-
from openerp.addons.nh_eobs.tests.common import test_data_creator_transfer
from openerp.tests.common import TransactionCase


class TestTransfer(TransactionCase):

    def setUp(self):
        super(TestTransfer, self).setUp()
        test_data_creator_transfer.admit_and_place_patient(self)
        self.domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
