# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestPatientStatus(TransactionCase):

    def setUp(self):
        super(TestPatientStatus, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.bed = self.test_utils.bed
        self.other_bed = self.test_utils.other_bed
        self.ward = self.test_utils.ward

        self.bed_availability_model = self.env['nh.clinical.bed_availability']

        self.in_ward = 'In Ward'
        self.off_ward = 'Off Ward'

    def call_test(self, location=None):
        return self.bed_availability_model._get_patient_status(location)

    def test_returns_in_ward_if_patient_allocated_to_bed(self):
        bed = self.bed.read()[0]
        expected = self.in_ward
        actual = self.call_test(bed)
        self.assertEqual(expected, actual)

    def test_returns_off_ward_if_patient_current_location_different(self):
        """
        Patient is allocated to their bed but the current location is not the
        bed.
        """
        self.test_utils.start_pme()
        bed = self.bed.read()[0]
        expected = self.off_ward
        actual = self.call_test(bed)
        self.assertEqual(expected, actual)

    def test_returns_none_if_no_patient_allocated_to_bed(self):
        move_model = self.env['nh.clinical.patient.move']
        move_activity_id = move_model.create_activity(
            {
                'spell_activity_id': self.spell_activity.id
            },
            {
                'patient_id': self.patient.id,
                'location_id': self.other_bed.id
            }
        )
        move_model.complete(move_activity_id)

        bed = self.bed.read()[0]
        expected = None
        actual = self.call_test(bed)
        self.assertEqual(expected, actual)

    def test_returns_none_if_location_is_not_a_bed(self):
        ward = self.ward.read()[0]
        expected = None
        actual = self.call_test(ward)
        self.assertEqual(expected, actual)
