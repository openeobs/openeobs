# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetOpenObsActivity(TransactionCase):
    """Test class for the :method:`get_open_obs_activity` method."""
    def setUp(self):
        super(TestGetOpenObsActivity, self).setUp()
        self.activity_model = self.env['nh.activity']
        self.api_model = self.env['nh.eobs.api']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.patient_id = self.api_model.register(
            self.hospital_number,
            {
                'family_name': 'Testersen',
                'given_name': 'Test'
            }
        )

        self.ews_activity_id = \
            self.ews_model.create_activity({}, {'patient_id': self.patient_id})
        self.ews_activity = self.activity_model.browse(self.ews_activity_id)
        self.ews = self.ews_activity.data_ref

    def test_get_open_obs_activity(self):
        open_obs_list = self.ews.get_open_obs_activity(1)
        self.assertEqual(len(open_obs_list), 1)
        self.assertEqual(self.ews_activity_id, open_obs_list[0].id)
