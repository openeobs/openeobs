# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestWardboardFoodFluidTable(TransactionCase):

    def setUp(self):
        super(TestWardboardFoodFluidTable, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.model_data_model = self.env['ir.model.data']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

    def test_wardboard_neuro_chart(self):
        wardboard = self.wardboard_model.get_by_spell_activity_id(
            self.spell_activity.id
        )
        wardboard_table = wardboard.wardboard_food_fluid_table()
        self.assertEqual(
            wardboard_table.get('res_id'), wardboard.id)
        self.assertEqual(
            wardboard_table.get('name'), wardboard.full_name)
