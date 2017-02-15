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

    def test_wardboard_neuro_list(self):
        wardboard = self.wardboard_model.browse(self.test_utils.patient_id)
        wardboard_neuro_chart = wardboard.wardboard_neuro_list()
        self.assertEqual(
            wardboard_neuro_chart.get('domain'),
            [
                ('patient_id', '=', self.test_utils.patient_id),
                ('state', '=', 'completed')
            ]
        )
        self.assertEqual(
            wardboard_neuro_chart.get('name'), wardboard.full_name)
