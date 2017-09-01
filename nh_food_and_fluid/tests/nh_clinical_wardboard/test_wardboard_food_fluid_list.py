# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestWardboardFoodFluidChart(TransactionCase):

    def setUp(self):
        super(TestWardboardFoodFluidChart, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.model_data_model = self.env['ir.model.data']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

    def test_wardboard_food_fluid_list(self):
        wardboard = self.wardboard_model.get_by_spell_activity_id(
            self.spell_activity.id
        )
        wardboard_food_fluid_chart = wardboard.wardboard_food_fluid_list()
        self.assertEqual(
            wardboard_food_fluid_chart.get('domain'),
            [
                ('patient_id', '=', self.test_utils.patient_id),
                ('state', '=', 'completed')
            ]
        )
        self.assertEqual(
            wardboard_food_fluid_chart.get('name'), wardboard.full_name)
