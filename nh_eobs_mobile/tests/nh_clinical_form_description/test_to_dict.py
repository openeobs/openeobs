# -*- coding: utf-8 -*-
import openerp
from openerp.addons import nh_observations
from openerp.tests.common import TransactionCase


class TestToDict(TransactionCase):

    class Model(object):
        an_obs_selection_field = nh_observations.fields.Selection(
            selection=['foo', 'bar'],
            string="I'm a teensy little obs field.",
            required=True
        )
        an_obs_character_field = nh_observations.fields.Char(
            size=100
        )
        an_odoo_field = openerp.fields.Selection(
            selection=['foo', 'bar'],
            string="I'm a teensy little odoo field.",
            required=True
        )

        _fields = {
            'an_obs_selection_field': an_obs_selection_field,
            'an_odoo_field': an_odoo_field
        }

        @staticmethod
        def get_obs_field_order():
            return ['obb', 'odd']

        an_obs_selection_field.name = 'obb'
        an_odoo_field.name = 'odd'
        an_obs_selection_field.necessary = True

    def setUp(self):
        super(TestToDict, self).setUp()
        self.form_description_model = self.env['nh.clinical.form_description']
        self.model = self.Model()

    def test_returns_list_of_dicts(self):
        form_description = \
            self.form_description_model.to_dict(self.model)

        self.assertTrue(list, type(form_description))
        for field_description in form_description:
            self.assertTrue(dict, type(field_description))

    def test_returns_only_obs_fields(self):
        form_description = \
            self.form_description_model.to_dict(self.model)

        self.assertEqual(1, len(form_description))
        self.assertEqual(form_description[0]['name'], 'obb')

    def test_adds_size_to_field_description(self):
        form_description = \
            self.form_description_model.to_dict(self.model)
        character_field_description = [
            field_description for field_description
            in form_description
            if field_description['name'] == 'an_obs_character_field'
        ][0]

        self.assertIn('size', character_field_description)
        self.assertEqual(100, character_field_description['size'])
