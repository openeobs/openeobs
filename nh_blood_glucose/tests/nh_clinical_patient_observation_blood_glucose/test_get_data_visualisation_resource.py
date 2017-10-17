# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetDataVisualisationResource(TransactionCase):

    def setUp(self):
        super(TestGetDataVisualisationResource, self).setUp()
        self.blood_glucose_model = \
            self.env['nh.clinical.patient.observation.blood_glucose']

    def test_returns_path_to_js(self):
        expected = '/nh_blood_glucose/static/src/js/chart.js'
        actual = self.blood_glucose_model.get_data_visualisation_resource()
        self.assertEqual(expected, actual)
