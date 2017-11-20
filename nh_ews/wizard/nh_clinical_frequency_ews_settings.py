# -*- coding: utf -*-
from openerp import fields, api
from openerp.addons.nh_odoo_fixes import validate
from openerp.models import TransientModel, MAGIC_COLUMNS


class NhClinicalFrequenciesEws(TransientModel):

    _name = 'nh.clinical.frequencies.ews_settings'
    _inherit = 'res.config.settings'

    no_risk_minimum = fields.Integer()
    low_risk_minimum = fields.Integer()
    medium_risk_minimum = fields.Integer()
    high_risk_minimum = fields.Integer()

    no_risk_maximum = fields.Integer()
    low_risk_maximum = fields.Integer()
    medium_risk_maximum = fields.Integer()
    high_risk_maximum = fields.Integer()

    no_risk = fields.Integer(
        min='no_risk_minimum', max='no_risk_maximum')
    low_risk = fields.Integer(
        min='low_risk_minimum', max='low_risk_maximum')
    medium_risk = fields.Integer(
        min='medium_risk_minimum', max='medium_risk_maximum')
    high_risk = fields.Integer(
        min='high_risk_minimum', max='high_risk_maximum')

    placement = fields.Integer()

    obs_restart = fields.Integer()

    @api.constrains('no_risk', 'low_risk', 'medium_risk', 'high_risk')
    def _in_min_max_range(self):
        validate.in_min_max_range(5, 10, self.no_risk)

    @api.multi
    def set_params(self):
        field_names = self._get_field_names()

        config_parameters_model = self.env['ir.config_parameter']
        for field_name in field_names:
            field_value = getattr(self, field_name)
            config_parameters_model.set_param(field_name, field_value)

    @api.model
    def get_default_params(self, field_names):
        current_param_values = {}
        config_parameters_model = self.env['ir.config_parameter']
        for field_name in field_names:
            current_param_values[field_name] = \
                config_parameters_model.get_param(field_name, '')
        return current_param_values

    def _get_field_names(self):
        field_names = [field_name for field_name in self._columns.keys()
                       if field_name not in MAGIC_COLUMNS]
        return field_names
