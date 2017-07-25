# -*- coding: utf-8 -*-
from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    def create_bed_manager(self):
        self.category_model = self.env['res.partner.category']
        self.user_model = self.env['res.users']
        self.bed_manager_role = \
            self.category_model.search([('name', '=', 'Bed Manager')])[0]
        self.bed_manager = self.user_model.create({
            'name': 'Bed Manager',
            'login': 'bed.manager',
            'password': 'bed.manager',
            'category_id': [[4, self.bed_manager_role.id]],
            'location_ids': [[6, 0, [self.ward.id]]]
        })
