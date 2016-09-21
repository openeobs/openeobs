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
        self.wardboard_model = self.env['nh.clinical.wardboard']
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

        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient
        })

        self.ews_activity_id = self.ews_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'patient_id': self.patient.id}
        )

        self.activity_pool.cancel(self.env.cr, self.env.uid, self.ews_activity_id)

        data = self.observation_report_model.new({})
        data.start_time = False
        data.end_time = False

        self.ews_list = self.observation_report_model.get_ews_observations(
            data, self.spell_activity_id
        )

    def test_ews_list_length(self):
        self.assertEquals(len(self.ews_list), 1)

    def test_cancelled_ews_returned(self):
        cancelled_ews = \
            [ews for ews in self.ews_list if ews['state'] == 'cancelled']
        self.assertEqual(len(cancelled_ews), 1,
                         "Unexpected number of cancelled EWS observations.")