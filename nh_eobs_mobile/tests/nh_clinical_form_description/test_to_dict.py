# -*- coding: utf-8 -*-
import openerp
from openerp.addons import nh_observations
from openerp.tests.common import TransactionCase


class TestToDict(TransactionCase):

    class Model(object):

        an_obs_field = nh_observations.fields.Selection()
        an_odoo_field = openerp.fields.Selection()

        _fields = {
            'an_obs_field': an_obs_field,
            'an_odoo_field': an_odoo_field
        }

        def get_obs_field_order(self):
            return ['obb', 'odd']

        an_obs_field.name = 'obb'
        an_odoo_field.name = 'odd'
        an_obs_field.necessary = True


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
