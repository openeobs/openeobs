# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestCalculateScore(TransactionCase):

    def setUp(self):
        super(TestCalculateScore, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.weight_model = self.env['nh.clinical.patient.observation.weight']
        self.height_model = self.env['nh.clinical.patient.observation.height']
        self.activity_model = self.env['nh.activity']

    def test_falsey_score_when_no_height_obs_performed_for_patient(self):
        obs = self.weight_model.create({
            'patient_id': self.patient.id,
            'weight': 56.1
        })
        self.assertFalse(obs.score)

    def test_height_obs_performed_for_patient_updates_score(self):
        weight = 56.1
        height = 1.7
        obs_height_activity_id = self.height_model.create_activity({}, {
            'patient_id': self.patient.id,
            'height': height
        })
        self.activity_model.complete(obs_height_activity_id)
        obs_weight = self.weight_model.create({
            'patient_id': self.patient.id,
            'weight': weight
        })
        expected = round(self.weight_model.calculate_bmi(weight, height), 1)
        actual = round(obs_weight.score, 1)

        self.assertEqual(expected, actual)

    def test_accepts_dict(self):
        weight = 56.1
        height = 1.7
        bmi = 19.4
        obs_height_activity_id = self.height_model.create_activity({}, {
            'patient_id': self.patient.id,
            'height': height
        })
        self.activity_model.complete(obs_height_activity_id)
        obs_weight = self.weight_model.create({
            'patient_id': self.patient.id,
            'weight': weight
        })
        obs_data = obs_weight.read()[0]
        expected = bmi
        actual = round(self.weight_model.calculate_score(obs_data), 1)

        self.assertEqual(expected, actual)
