# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetDataVisualisationResource(TransactionCase):

    def setUp(self):
        super(TestGetDataVisualisationResource, self).setUp()
        self.weight_model = self.env['nh.clinical.patient.observation.weight']

    def test_returns_path_to_js(self):
        expected = '/nh_weight/static/src/js/chart.js'
        actual = self.weight_model.get_data_visualisation_resource()
        self.assertEqual(expected, actual)
