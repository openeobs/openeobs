# -*- coding: utf-8 -*-
import openerp
from openerp import models
from openerp.addons import nh_observations
from openerp.tests.common import TransactionCase


class TestToDict(TransactionCase):

    class Model(models.AbstractModel):

        a_field = nh_observations.fields.Selection(
            selection=[('a', 'Ay')], string='Stringy', necessary=True
        )
        another_field = openerp.fields.Selection(
            selection=[('b', 'Bee')], string='Stringeth'
        )
        _fields = {
            'a_field': a_field,
            'another_field': another_field
        }

    def setUp(self):
        super(TestToDict, self).setUp()
        self.form_description_model = self.env['nh.clinical.form_description']

    def test_returns_list_of_dicts(self):
        model = self.Model
        form_description = \
            self.form_description_model.to_dict(model)

        self.assertTrue(list, type(form_description))
        for field_description in form_description:
            self.assertTrue(dict, type(field_description))

    def test_returns_all_obs_fields(self):
        model = self.Model
        form_description = \
            self.form_description_model.to_dict(model)
        self.assertEqual(1, len(form_description))

    def test_returns_keys(self):
        pass
