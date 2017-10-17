# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestSetRapidTranq(TransactionCase):

    def setUp(self):
        super(TestSetRapidTranq, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']

        self.activity_rapid_tranq = \
            self.test_utils.create_activity_rapid_tranq()
        self.rapid_tranq = self.activity_rapid_tranq.data_ref

    def test_sets_rapid_tranq_field_on_spell(self):
        self.assertFalse(self.spell.rapid_tranq)
        self.rapid_tranq.set_rapid_tranq(True)
        self.assertTrue(self.spell.rapid_tranq)
