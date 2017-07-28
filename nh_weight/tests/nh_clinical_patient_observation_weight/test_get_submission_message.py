# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetSubmissionMessage(TransactionCase):

    def setUp(self):
        super(TestGetSubmissionMessage, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.weight_model = self.env['nh.clinical.patient.observation.weight']
        self.height_model = self.env['nh.clinical.patient.observation.height']
        self.activity_model = self.env['nh.activity']

        self.weight = 79.6
        self.height = 1.77
        self.bmi = 25.4
        self.no_bmi_message = \
            "BMI could not be calculated. Please take height measurement."
        self.partial_message = \
            "BMI could not be calculated as weight was not provided."

    def call_test(self, create_height_obs=False, partial_weight_obs=False):
        if create_height_obs:
            self.obs_height_activity_id = self.height_model.create_activity(
                {},
                {
                    'patient_id': self.patient.id,
                    'height': self.height
                }
            )
            height_act = self.activity_model.browse(
                self.obs_height_activity_id)
            height_act.complete()

        vals = {
            'patient_id': self.patient.id,
            'waist_measurement': 80.4
        }
        if not partial_weight_obs:
            vals['weight'] = self.weight

        self.obs_weight = self.weight_model.create(vals)
        message = self.obs_weight.get_submission_message()
        return message

    def test_message_returned_when_no_height_obs(self):
        expected = self.no_bmi_message
        actual = self.call_test()
        self.assertEqual(expected, actual)

    def test_message_returned_when_partial_weight_obs(self):
        expected = self.partial_message
        actual = self.call_test(partial_weight_obs=True,
                                create_height_obs=True)
        self.assertEqual(expected, actual)

    def test_bmi_returned_when_height_obs(self):
        expected = "Based on the weight submitted, the patient's BMI is {}"\
            .format(self.bmi)
        actual = self.call_test(create_height_obs=True)
        self.assertEqual(expected, actual)
