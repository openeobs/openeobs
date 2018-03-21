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

    def get_latest_shift_for_ward(self, ward_id):
        latest_shift_for_ward_search_results = self.search(
            [('ward', '=', ward_id)],
            order='id desc', limit=1
        )
        return latest_shift_for_ward_search_results

    def user_on_shift(self, ward_id):
        latest_shift = self.get_latest_shift_for_ward(ward_id)
        user_on_shift = self.env.user in latest_shift.hcas \
            or self.env.user in latest_shift.nurses
        return user_on_shift
