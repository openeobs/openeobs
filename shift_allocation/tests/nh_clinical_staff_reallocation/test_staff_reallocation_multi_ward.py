from openerp.tests.common import TransactionCase


class TestStaffReallocationMultiWard(TransactionCase):

    def setUp(self):
        super(TestStaffReallocationMultiWard, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.allocation_pool = self.env['nh.clinical.staff.allocation']
        self.reallocation_pool = self.env['nh.clinical.staff.reallocation']
        self.user_pool = self.env['res.users']
        self.patient_pool = self.env['nh.clinical.patient']
        self.allocating_pool = self.env['nh.clinical.allocating']
        self.resp_allocation_pool = \
            self.env['nh.clinical.user.responsibility.allocation']
        self.test_utils_model.create_locations()
        self.test_utils_model.create_users()
        self.test_utils_model.create_patient()
        self.test_utils_model.admit_patient()
        self.test_utils_model.placement = \
            self.test_utils_model.create_placement()
        self.test_utils_model.place_patient()
        self.shift_coordinator = \
            self.test_utils_model.create_shift_coordinator()
        items_needed = [
            'ward',
            'other_ward',
            'hca',
            'nurse',
            'bed',
            'other_bed',
            'doctor'
        ]
        for item in items_needed:
            self.test_utils_model.copy_instance_variable_if_exists(self, item)

        self.other_nurse = self.test_utils_model.create_nurse(
            location_id=self.other_bed.id)
        self.other_hca = self.test_utils_model.create_hca(
            location_id=self.other_bed.id)
        self.other_shift_coordinator = \
            self.test_utils_model.create_shift_coordinator(
                location_id=self.other_ward.id)
        self.bed_2_ward_1 = self.test_utils_model.create_location(
            'bed', self.ward.id)
        self.bed_2_ward_2 = self.test_utils_model.create_location(
            'bed', self.other_ward.id
        )
        self.dual_ward_hca = self.test_utils_model.create_hca()
        self.dual_ward_nurse = self.test_utils_model.create_nurse()
        dual_beds = [self.bed_2_ward_1.id, self.bed_2_ward_2.id]
        self.reallocation_pool.responsibility_allocation_activity(
            self.dual_ward_nurse.id, dual_beds)
        self.reallocation_pool.responsibility_allocation_activity(
            self.dual_ward_hca.id, dual_beds)

        self.allocation_pool \
            .sudo(self.shift_coordinator) \
            .create({
                'ward_id': self.ward.id,
                'user_ids': [(6, 0, [
                    self.nurse.id, self.hca.id,
                    self.dual_ward_nurse.id, self.dual_ward_hca.id
                ])]
            })\
            .complete()

        self.wizard = self.reallocation_pool \
            .sudo(self.shift_coordinator) \
            .create({})

        self.wizard.reallocate()
        self.wizard.complete()

    def test_reallocate_only_affects_chosen_ward(self):
        """
        On Doing reallocation everyone should keep their allocations
        """
        self.assertEqual(self.nurse.location_ids.ids, [self.bed.id])
        self.assertEqual(
            self.other_nurse.location_ids.ids, [self.other_bed.id])
        self.assertEqual(
            self.dual_ward_nurse.location_ids.ids,
            [self.bed_2_ward_1.id, self.bed_2_ward_2.id]
        )
        self.assertEqual(self.hca.location_ids.ids, [self.bed.id])
        self.assertEqual(self.other_hca.location_ids.ids, [self.other_bed.id])
        self.assertEqual(
            self.dual_ward_hca.location_ids.ids,
            [self.bed_2_ward_1.id, self.bed_2_ward_2.id]
        )
        self.assertEqual(
            self.shift_coordinator.location_ids.ids, [self.ward.id])
        self.assertEqual(
            self.other_shift_coordinator.location_ids.ids,
            [self.other_ward.id]
        )
