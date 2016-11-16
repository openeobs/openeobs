# -*- coding: utf-8 -*-
from openerp.addons.nh_eobs.tests.common import test_data_creator
from openerp.tests.common import TransactionCase


class TestPlacement(TransactionCase):

    def setUp(self):
        super(TestPlacement, self).setUp()
        test_data_creator.admit_patient(self)
        self.domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]

    def test_new_obs_created(self):
        # Only cancel when transfer successful.
        open_obs_activities = self.activity_model.search(self.domain)
        self.assertEqual(len(open_obs_activities), 0)

        test_data_creator.place_patient(self)

        open_obs_activities = self.activity_model.search(self.domain)
        self.assertEqual(len(open_obs_activities), 1)

    def test_new_obs_due_in_15_minutes(self):
        test_data_creator.place_patient(self)

        open_obs_activities = self.activity_model.search(self.domain)
        self.assertEqual(len(open_obs_activities), 1)
        open_obs_activity = open_obs_activities[0]
        self.assertEqual(open_obs_activity.data_ref.frequency, 15)

    def test_new_obs_due_in_15_minutes_after_transfer(self):
        test_data_creator.place_patient(self)
        # open_obs_activities = self.activity_model.search(self.domain)
        # first_obs_after_placement = open_obs_activities[0]
        # TODO Uncomment 2 lines above when EOBS-690 has been completed.

        self.api_model.transfer(self.hospital_number, {'location': 'WB'})

        # Need to check first obs is cancelled otherwise we will get false
        # positives from the later assertions.
        # self.assertEqual(first_obs_after_placement.state, 'cancelled')
        # TODO Uncomment line above when EOBS-690 has been completed.

        # Place patient again on new ward.
        test_data_creator.place_patient(self)

        open_obs_activities = self.activity_model.search(self.domain)
        self.assertEqual(len(open_obs_activities), 1)
        open_obs_activity = open_obs_activities[0]
        self.assertEqual(open_obs_activity.data_ref.frequency, 15)
