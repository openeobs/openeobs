# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetEwsObservations(TransactionCase):

    def setUp(self):
        super(TestGetEwsObservations, self).setUp()
        self.observation_report_model = \
            self.env['report.nh.clinical.observation_report']
        self.patient_model = self.env['nh.clinical.patient']
        self.activity_model = self.env['nh.activity']
        self.activity_pool = self.registry('nh.activity')
        self.spell_model = self.env['nh.clinical.spell']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {'patient_id': self.patient.id, 'pos_id': 1}
        )

        self.spell_activity = \
            self.activity_model.browse(self.spell_activity_id)

        self.spell = self.spell_activity.data_ref

        # Fails in spell.get_patient_by_id() if not started.
        self.activity_pool.start(self.env.cr, self.env.uid,
                                 self.spell_activity_id)

        self.cancel_reason_placement = \
            self.browse_ref('nh_eobs.cancel_reason_placement')

        self.ews_activity_id = self.ews_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'patient_id': self.patient.id}
        )
        self.activity_pool.cancel(self.env.cr, self.env.uid,
                                  self.ews_activity_id)

        self.observation_report = self.observation_report_model.new({})
        self.observation_report.start_time = False
        self.observation_report.end_time = False

    def call_get_ews_observations(self):
        self.ews_list = self.observation_report_model.get_ews_observations(
            self.observation_report, self.spell_activity_id
        )

    def test_ews_list_length(self):
        self.call_get_ews_observations()
        self.assertEquals(len(self.ews_list), 1)

    def test_cancelled_ews_returned(self):
        self.call_get_ews_observations()
        cancelled_ews_returned = \
            [ews for ews in self.ews_list if ews['state'] == 'cancelled']

        self.assertEqual(len(cancelled_ews_returned), 1,
                         "Unexpected number of cancelled EWS observations.")

    def test_no_ews_with_placement_cancellation_reason_returned(self):
        self.ews_cancelled_due_to_placement_activity_id = \
            self.ews_model.create_activity(
                {'parent_id': self.spell_activity_id},
                {'patient_id': self.patient.id}
            )
        self.activity_pool.cancel_with_reason(
            self.env.cr, self.env.uid,
            self.ews_cancelled_due_to_placement_activity_id,
            self.cancel_reason_placement.id
        )

        self.call_get_ews_observations()

        cancelled_ews_returned = \
            [ews for ews in self.ews_list if ews['state'] == 'cancelled']
        ews_cancelled_due_to_placement = \
            [ews for ews in cancelled_ews_returned
             if ews['cancel_reason_id']
             and ews['cancel_reason_id'][0] is self.cancel_reason_placement.id]

        self.assertEqual(len(ews_cancelled_due_to_placement), 0,
                         "There should not be any EWS observations "
                         "returned that were cancelled due to a patient "
                         "placement.")