# -*- coding: utf-8 -*-
from openerp import exceptions
from openerp.addons.nh_observations import frequencies
from openerp.tests.common import TransactionCase


class TestFieldValidation(TransactionCase):

    def setUp(self):
        super(TestFieldValidation, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)

        self.notification_frequency_model = \
            self.env['nh.clinical.notification.frequency']
        self.frequency = frequencies.as_list()[0][0]

    def test_not_observation_model_name_fails_validation(self):
        not_an_observation = 'nh.clinical.patient.blooblah'
        with self.assertRaises(exceptions.ValidationError):
            self.notification_frequency_model.create({
                'frequency': self.frequency,
                'observation': not_an_observation,
                'patient_id': self.patient.id
            })

    def test_observation_model_name_passes_validation(self):
        an_observation = 'nh.clinical.patient.observation.foo'
        self.notification_frequency_model.create({
            'frequency': self.frequency,
            'observation': an_observation,
            'patient_id': self.patient.id
        })
