# -*- coding: utf -*-
from openerp.models import Model, fields, api


class NhClinicalFrequenciesEws(Model):

    _name = 'nh.clinical.frequencies.ews'
    _inherit = 'nh.clinical.frequencies'

    low_risk_minimum = fields.Integer(default=15)
    medium_risk_minimum = fields.Integer(default=15)
    high_risk_minimum = fields.Integer(default=15)

    low_risk_maximum = fields.Integer(default=15)
    medium_risk_maximum = fields.Integer(default=15)
    high_risk_maximum = fields.Integer(default=15)

    low_risk = fields.Integer(
        default=15, min=low_risk_minimum, max=low_risk_maximum)
    medium_risk = fields.Integer(
        default=15, min=medium_risk_minimum, max=medium_risk_maximum)
    high_risk = fields.Integer(
        default=15, min=high_risk_minimum, max=high_risk_maximum)

    placement = fields.Integer(default=15)

    obs_restart = fields.Integer(default=15)

    @api.constrains('low_risk', 'medium_risk', 'high_risk')
    def _in_min_max_range(self):
        pass
