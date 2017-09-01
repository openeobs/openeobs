# -*- coding: utf-8 -*-
from openerp import fields as odoo_fields
from openerp.addons.nh_observations import fields as nh_obs_fields
from openerp.tests.common import TransactionCase


class TestGetObsFieldsFromFields(TransactionCase):
    """Test `nh.clinical.field_utils` method `get_obs_field_from_fields`."""
    def setUp(self):
        super(TestGetObsFieldsFromFields, self).setUp()
        self.field_utils = self.env['nh.clinical.field_utils']

    def test_odoo_and_obs_fields_passed(self):
        fields = [
            odoo_fields.Selection(),
            odoo_fields.Selection(),
            odoo_fields.Selection(),
            nh_obs_fields.Selection(),
            nh_obs_fields.Selection(),
            nh_obs_fields.Selection()
        ]
        obs_fields = self.field_utils.get_obs_fields_from_fields(fields)
        self.assertEqual(3, len(obs_fields))

    def test_only_odoo_fields_passed(self):
        fields = [
            odoo_fields.Selection(),
            odoo_fields.Selection(),
            odoo_fields.Selection()
        ]
        obs_fields = self.field_utils.get_obs_fields_from_fields(fields)
        self.assertEqual(0, len(obs_fields))

    def test_only_obs_fields_passed(self):
        fields = [
            nh_obs_fields.Selection(),
            nh_obs_fields.Selection(),
            nh_obs_fields.Selection()
        ]
        obs_fields = self.field_utils.get_obs_fields_from_fields(fields)
        self.assertEqual(3, len(obs_fields))
