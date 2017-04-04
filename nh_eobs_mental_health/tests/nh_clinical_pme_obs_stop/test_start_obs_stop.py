# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.tests.common import TransactionCase


class TestStartObsStop(TransactionCase):

    def setUp(self):
        super(TestStartObsStop, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.obs_stop_model = self.env['nh.clinical.pme.obs_stop']

        self.activity_obs_stop = self.test_utils.create_activity_obs_stop()
        self.obs_stop = self.activity_obs_stop.data_ref

        self.test_utils.get_open_obs()

    def test_cancels_all_open_ews(self):
        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('state', 'not in', ['completed', 'cancelled']),
            ('parent_id', '=', self.spell_activity.id)
        ]
        activities_ews_open = self.activity_model.search(domain)
        self.assertTrue(len(activities_ews_open) > 0)

        self.obs_stop.start(self.activity_obs_stop.id)
        activities_ews_open = self.activity_model.search(domain)
        self.assertEqual(len(activities_ews_open), 0)

        self.assertEqual(self.test_utils.ews_activity.state, 'cancelled')

    def test_pme_cancel_reason_set(self):
        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('state', 'not in', ['completed', 'cancelled']),
            ('parent_id', '=', self.spell_activity.id)
        ]
        activities_ews_open = self.activity_model.search(domain)
        self.assertTrue(len(activities_ews_open) > 0)

        self.assertFalse(activities_ews_open.cancel_reason_id)

        self.obs_stop.start(self.activity_obs_stop.id)
        cancel_reason_pme = \
            self.env['ir.model.data'].get_object(
                'nh_eobs', 'cancel_reason_patient_monitoring_exception'
            )
        self.assertEqual(cancel_reason_pme.id,
                         activities_ews_open.cancel_reason_id.id)

    def test_raises_on_failing_to_cancel(self):
        self.obs_stop_model._patch_method('cancel_open_ews', lambda a, b: None)
        spell_activity_id = self.obs_stop.spell.activity_id.id
        try:
            with self.assertRaises(osv.except_osv):
                self.obs_stop.start(spell_activity_id)
        finally:
            self.obs_stop_model._revert_method('cancel_open_ews')
