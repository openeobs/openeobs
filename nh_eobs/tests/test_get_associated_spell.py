# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase

class TestGetAssociatedSpell(TransactionCase):

    def setUp(self):
        super(TestGetAssociatedSpell, self).setUp()

        # TODO is there an easier way to do all this?
        pos_model = self.env['nh.clinical.pos']
        pos = pos_model.create({'name': 'test_get_associated_spell_pos',
                                'location_id': 1})

        patient_model = self.env['nh.clinical.patient']
        patient = patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'HN001'
        })

        spell_model = self.env['nh.clinical.spell']
        spell = spell_model.create({
            'patient_id': patient.id,
            'pos_id': pos.id
        })

        activity_model = self.env['nh.activity']
        activity = activity_model.create({
            'data_model': 'nh.clinical.spell',
            'data_ref': spell
        })

        wardboard_model = self.env['nh.clinical.wardboard']
        self.wardboard_id = wardboard_model.create({
            'spell_activity_id': activity.id
        })

        # def mock_activity_browse(*args, **kwargs):
        #     return activity_model.create({'data_ref': spell_id})
        # activity_model._patch_method('browse', )

    def test_returns_spell_record(self):
        wardboard_model = self.env['nh.clinical.wardboard']
        spell_record = wardboard_model.get_associated_spell(self.wardboard_id)
        self.assertTrue(spell_record)
