# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase

from openerp.addons.nh_clinical.tests.common import helpers


class TestDoctorAllocationDeallocate(TransactionCase):

    def setUp(self):
        super(TestDoctorAllocationDeallocate, self).setUp()

        helpers.create_test_data(self, self.cr, self.uid, iterations=2)
        self.ward_manager_id = self.users['wm'][0]
        self.ward_id = self.locations.keys()[0]
        self.ward_bed_ids = self.locations[self.ward_id]
        self.ward_all_location_ids = [self.ward_id] + self.ward_bed_ids

        self.doctor_allocation_wizard_id = self.doctor_allocation.create(
            self.cr, self.ward_manager_id,
            {'location_ids': [(6, 0, self.ward_all_location_ids)]}
        )

    def test_only_current_ward_is_deallocated(self):
        doctor = self.users_pool.browse(
            self.cr, self.uid, self.users['dr'][0]
        )

        # Allocate another ward to the doctor.
        another_ward_id = self.locations.keys()[1]
        another_ward_bed_ids = self.locations[another_ward_id]
        another_ward_all_location_ids = \
            [another_ward_id] + another_ward_bed_ids
        doctor_new_location_ids = \
            doctor.location_ids.ids + another_ward_all_location_ids
        self.users_pool.write(
            self.cr, self.uid, doctor.id, {
                'location_ids': [(6, 0, doctor_new_location_ids)]
            }
        )

        doctor_location_ids_before = doctor.location_ids.ids
        self.doctor_allocation.deallocate(
            self.cr, self.uid, self.doctor_allocation_wizard_id
        )
        expected = [element for element in doctor_location_ids_before
                    if element not in self.ward_all_location_ids]
        actual = doctor.location_ids.ids
        self.assertSequenceEqual(expected, actual)
