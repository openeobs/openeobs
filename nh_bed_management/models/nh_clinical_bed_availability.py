# -*- coding: utf-8 -*-
from openerp import models, fields


class NhClinicalBedAvailability(models.Model):

    _name = 'nh.clinical.bed_availability'

    locations = fields.Many2one(
        'nh.clinical.location', 'LOCATIONS', required=True
    )
