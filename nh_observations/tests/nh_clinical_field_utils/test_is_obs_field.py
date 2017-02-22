# -*- coding: utf-8 -*-
from openerp import fields as odoo_fields
from openerp.addons.nh_observations import fields as nh_obs_fields
from openerp.tests.common import TransactionCase


class TestIsObsField(TransactionCase):
    """Test `nh.clinical.field_utils` method `is_obs_field`."""
    def setUp(self):
        super(TestIsObsField, self).setUp()
        self.field_utils = self.env['nh.clinical.field_utils']

    def test_obs_field_returns_true(self):
        field = nh_obs_fields.Selection()
        is_obs_field = self.field_utils.is_obs_field(field)
        self.assertTrue(is_obs_field)

    def test_odoo_field_returns_false(self):
        field = odoo_fields.Selection()
        is_obs_field = self.field_utils.is_obs_field(field)
        self.assertTrue(is_obs_field)
