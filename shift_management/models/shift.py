# -*- coding: utf-8 -*-
from openerp import models, fields


class Shift(models.Model):
    """
    A model representing the nurses and HCAs who are meant to be on a shift.
    Nurses and HCAs must be placed on a shift before they can see their
    patients to perform observations on them.

    Shifts are specific to wards, we do not support the concept of a shift
    that spans multiple wards.
    """
    _name = 'nh.clinical.shift'
    ward = fields.Many2one(comodel_name='nh.clinical.location')
    nurses = fields.Many2many(
        comodel_name='res.users', relation='shift_nurses'
    )
    hcas = fields.Many2many(
        comodel_name='res.users',
        relation='shift_hcas'
    )