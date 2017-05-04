# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetLatestHeight(TransactionCase):

    def setUp(self):
        super(TestGetLatestHeight, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.height_model = self.env['nh.clinical.patient.observation.height']

        self.height = 1.46

    def call_test(self, heights):
        for height in heights:
            activity_id = self.height_model.create_activity(
                {},
                {
                    'patient_id': self.patient.id,
                    'height': height
                }
            )
            self.height_model.complete(activity_id)

    def test_one_obs_with_height(self):
        expected = self.height
        self.call_test([expected])
        actual = self.height_model.get_latest_height(self.patient.id)

        self.assertEqual(expected, actual)

    def test_last_obs_had_height(self):
        expected = self.height
        self.call_test([None, expected])
        actual = self.height_model.get_latest_height(self.patient.id)

        self.assertEqual(expected, actual)

    def test_obs_before_last_had_height(self):
        expected = self.height
        self.call_test([expected, None])
        actual = self.height_model.get_latest_height(self.patient.id)

        self.assertEqual(expected, actual)

    def test_three_obs_ago_had_height(self):
        expected = self.height
        self.call_test([expected, None, None])
        actual = self.height_model.get_latest_height(self.patient.id)

        self.assertEqual(expected, actual)

    def test_obs_but_non_with_height(self):
        expected = None
        self.call_test([None, None, None])
        actual = self.height_model.get_latest_height(self.patient.id)

        self.assertEqual(expected, actual)

    def test_no_height_obs_at_all(self):
        expected = None
        actual = self.height_model.get_latest_height(self.patient.id)

        self.assertEqual(expected, actual)
