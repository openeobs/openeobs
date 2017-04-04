# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestCompletePme(TransactionCase):

    def setUp(self):
        super(TestCompletePme, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.pme_model = self.env['nh.clinical.patient_monitoring_exception']

        pme_activity_id = self.pme_model.create_activity(
            {'spell_activity_id': self.spell_activity.id},
            {
                'spell': self.spell.id
            }
        )
        self.pme_activity = self.activity_model.browse(pme_activity_id)
        self.pme = self.pme_activity.data_ref
        self.pme.start(self.pme_activity.id)

    def test_completes_pme_activity(self):
        state = self.pme_activity.state
        self.assertEqual(state, 'started')
        self.pme.complete(self.pme_activity.id)
        state = self.pme_activity.state
        self.assertEqual(state, 'completed')
