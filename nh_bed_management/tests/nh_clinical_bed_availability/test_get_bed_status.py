# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetBedStatus(TransactionCase):

    def setUp(self):
        super(TestGetBedStatus, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.bed = self.test_utils.bed
        self.ward = self.test_utils.ward

        self.available = 'available'
        self.occupied = 'occupied'

        self.bed_availability_model = self.env['nh.clinical.bed_availability']

    def test_returns_occupied_when_patient_allocated_to_it(self):
        record = self.bed_availability_model.create({
            'location': self.bed.id
        })
        expected = self.occupied
        actual = record.bed_status
        self.assertEqual(expected, actual)

    def test_returns_available_when_no_patient_allocated_to_it(self):
        record = self.bed_availability_model.create({
            'location': self.bed.id
        })
        self.assertEqual(self.occupied, record.bed_status)

        self.test_utils.discharge_patient()

        # Must manually recompute. Odoo does this for us when a view is
        # reloaded.
        self.env.add_todo(record._fields['bed_status'], record)
        record.recompute()

        expected = self.available
        actual = record.bed_status

        self.assertEqual(expected, actual)
