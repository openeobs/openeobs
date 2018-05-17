# -*- coding: utf-8 -*-
from openerp import models

from openerp.addons.nh_observations import fields as nh_obs_fields


class FieldUtils(models.AbstractModel):
    """
    Provides helpful methods, mainly for distinguishing between Odoo's fields
    and our own extensions of them.
    """
    _inherit = 'nh.clinical.field_utils'

    @classmethod
    def is_obs_field(cls, field):
        fields = (
            nh_obs_fields.Selection,
            nh_obs_fields.Boolean,
            nh_obs_fields.Char,
            nh_obs_fields.Text,
            nh_obs_fields.Integer,
            nh_obs_fields.One2many,
            nh_obs_fields.Many2one,
            nh_obs_fields.Many2Many,
            nh_obs_fields.Float
        )
        return isinstance(field, fields)

    def get_obs_fields_from_model(self, model):
        fields = model._fields.values()
        return self.get_obs_fields_from_fields(fields)

    def get_obs_fields_from_fields(self, fields):
        return [field for field in fields if self.is_obs_field(field)]
