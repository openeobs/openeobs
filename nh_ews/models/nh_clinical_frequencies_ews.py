# -*- coding: utf-8 -*-
from openerp import fields, api
from openerp.models import Model


class NhClinicalFrequenciesEws(Model):

    _name = 'nh.clinical.frequencies.ews'
    _inherit = 'nh.clinical.frequencies'

    none_risk_minimum = fields.Integer(default=0)
    low_risk_minimum = fields.Integer(default=0)
    medium_risk_minimum = fields.Integer(default=0)
    high_risk_minimum = fields.Integer(default=0)

    none_risk_maximum = fields.Integer(default=100)
    low_risk_maximum = fields.Integer(default=100)
    medium_risk_maximum = fields.Integer(default=100)
    high_risk_maximum = fields.Integer(default=100)

    none_risk = fields.Integer(
        default=30, min=low_risk_minimum, max=low_risk_maximum)
    low_risk = fields.Integer(
        default=60, min=low_risk_minimum, max=low_risk_maximum)
    medium_risk = fields.Integer(
        default=240, min=medium_risk_minimum, max=medium_risk_maximum)
    high_risk = fields.Integer(
        default=720, min=high_risk_minimum, max=high_risk_maximum)

    placement = fields.Integer(default=15)

    obs_restart = fields.Integer(default=60)

    @api.constrains('low_risk', 'medium_risk', 'high_risk')
    def _in_min_max_range(self):
        pass
