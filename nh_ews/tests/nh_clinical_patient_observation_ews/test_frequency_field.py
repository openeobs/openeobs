# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestFrequencyField(TransactionCase):
    """Test class for the `frequency` field override."""
    def setUp(self):
        super(TestFrequencyField, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

    def test_ten_minutes_is_valid_frequency_value(self):
        self.ews_model.create({
            'patient_id': self.patient.id,
            'frequency': 10
        })
