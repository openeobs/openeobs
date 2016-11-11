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

    def test_open_obs_cancelled(self):
        open_obs_activities = self.activity_model.search(self.domain)
        first_obs_after_placement = open_obs_activities[0]
        self.assertEqual(len(open_obs_activities), 1)

        self.api_model.transfer(self.hospital_number, {'location': 'WB'})

        open_obs_activities = self.activity_model.search(self.domain)
        self.assertEqual(len(open_obs_activities), 0)
        self.assertEqual(first_obs_after_placement.state, 'cancelled')
        cancel_reason = self.env['ir.model.data'].get_object(
            'nh_eobs', 'cancel_reason_transfer'
        )
        self.assertEqual(
            first_obs_after_placement.cancel_reason_id, cancel_reason
        )
