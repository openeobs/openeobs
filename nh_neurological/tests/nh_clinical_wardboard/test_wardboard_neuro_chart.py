# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestWardboardNeuroChart(TransactionCase):

    def setUp(self):
        super(TestWardboardNeuroChart, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.model_data_model = self.env['ir.model.data']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

    def test_wardboard_neuro_chart(self):
        wardboard = self.wardboard_model.get_by_spell_activity_id(
            self.spell_activity.id
        )
        view_id = self.model_data_model.search(
            [('name', '=', 'view_wardboard_neuro_chart_form')])[0].res_id
        wardboard_neuro_chart = wardboard.wardboard_neuro_chart()
        self.assertEqual(wardboard_neuro_chart.get('view_id'), int(view_id))
        self.assertEqual(
            wardboard_neuro_chart.get('res_id'), wardboard.id)
        self.assertEqual(
            wardboard_neuro_chart.get('name'), wardboard.full_name)
