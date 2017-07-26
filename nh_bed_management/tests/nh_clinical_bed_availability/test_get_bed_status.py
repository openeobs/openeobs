# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetBedStatus(TransactionCase):

    def setUp(self):
        super(TestGetBedStatus, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.bed = self.test_utils.bed
        self.ward= self.test_utils.ward

        self.available = 'Available'
        self.occupied = 'Occupied'

    def call_test(self, location):
        bed_availability_model = self.env['nh.clinical.bed_availability']
        return bed_availability_model._get_bed_status(location)

    def test_returns_available_when_no_patient_allocated_to_it(self):
        self.test_utils.discharge_patient()
        bed = self.bed.read()[0]
        expected = self.available
        actual = self.call_test(bed)
        self.assertEqual(expected, actual)

    def test_returns_occupied_when_patient_allocated_to_it(self):
        bed = self.bed.read()[0]
        expected = self.occupied
        actual = self.call_test(bed)
        self.assertEqual(expected, actual)

    def test_returns_none_if_location_is_not_bed(self):
        ward = self.ward.read()[0]
        actual = self.call_test(ward)
        self.assertIsNone(actual)

    def test_raises_value_error_if_no_usage_field_on_passed_location(self):
        with self.assertRaises(ValueError):
            location = {
                'plop'
            }
            self.call_test(location)

    def test_invalid_value_raises_exception(self):
        pass
