# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestPatientStatus(TransactionCase):

    def setUp(self):
        super(TestPatientStatus, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.bed = self.test_utils.bed
        self.ward = self.test_utils.ward

        self.available = 'Available'
        self.occupied = 'Occupied'

    def test_returns_in_ward_if_patient_current_location_is_not_bed(self):
        pass

    def test_returns_off_ward_if_patient_current_location_is_bed(self):
        pass

    def test_returns_none_if_bed_is_available(self):
        pass

    def test_returns_none_if_location_is_not_a_bed(self):
        pass

    def test_raises_exception_if_no_patient_ids_field(self):
        pass
