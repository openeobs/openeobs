# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetOpenObsActivity(TransactionCase):
    """Test class for the :method:`get_open_obs_activity` method."""
    def setUp(self):
        super(TestGetOpenObsActivity, self).setUp()
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.registry('nh.activity')
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {'patient_id': self.patient.id, 'pos_id': 1}
        )

        self.spell_activity = self.activity_model.browse(
            self.spell_activity_id
        )

        self.spell = self.spell_activity.data_ref

        # Fails in spell.get_patient_by_id() if not started.
        self.activity_pool.start(self.env.cr, self.env.uid,
                                 self.spell_activity_id)

        self.ews_activity_id = \
            self.ews_model.create_activity({}, {'patient_id': self.patient.id})
        self.ews_activity = self.activity_model.browse(self.ews_activity_id)
        self.ews = self.ews_activity.data_ref

    def test_get_open_obs_activity(self):
        open_obs_list = self.ews_model.get_open_obs_activity(
            self.spell_activity_id
        )
        self.assertEqual(len(open_obs_list), 1)
        self.assertEqual(self.ews_activity_id, open_obs_list[0].id)
