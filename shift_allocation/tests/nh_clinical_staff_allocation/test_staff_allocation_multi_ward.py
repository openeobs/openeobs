from openerp.tests.common import TransactionCase


class TestStaffAllocationMultiWard(TransactionCase):

    def setUp(self):
        super(TestStaffAllocationMultiWard, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.allocation_pool = self.env['nh.clinical.staff.allocation']
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
        self.dual_ward_hca = self.test_utils_model.create_hca()
        self.dual_ward_nurse = self.test_utils_model.create_nurse()
        dual_beds = [self.bed.id, self.other_bed.id]
        self.allocation_pool.responsibility_allocation_activity(
            self.dual_ward_nurse.id, dual_beds)
        self.allocation_pool.responsibility_allocation_activity(
            self.dual_ward_hca.id, dual_beds)

        self.wizard = self.allocation_pool \
            .sudo(self.shift_coordinator) \
            .create({'ward_id': self.ward.id})

        self.wizard.submit_ward()
        self.wizard.deallocate()
        self.wizard.write({
            'user_ids': [[6, 0, [
                self.dual_ward_hca.id,
                self.dual_ward_nurse.id
            ]]]
        })
        self.wizard.submit_users()
        self.wizard.allocating_ids.write(
            {
                'nurse_id': self.dual_ward_nurse.id,
                'hca_ids': [[6, 0, [self.dual_ward_hca.id]]],
                'location_id': self.bed.id
            })
        self.wizard.complete()

    def test_deallocate_only_affects_chosen_ward(self):
        """
        On Doing a shift change the following should only happen to the chosen
        ward (Ward A in this test), All other wards should be unaffected
        - Ward A Nurse should be deallocated
        - Ward A HCA should be deallocated
        - Ward B Nurse should remain allocated to beds
        - Ward B HCA should remain allocated to beds
        - Dual Ward Nurse should be deallocated from beds in Ward A but
          not Ward B
        - Dual Ward HCA should be deallocated from beds in Ward A but not
          Ward B
        """
        self.assertEqual(self.nurse.location_ids.ids, [])
        self.assertIn(self.other_bed.id, self.other_nurse.location_ids.ids)
        self.assertIn(self.bed.id, self.dual_ward_nurse.location_ids.ids)
        self.assertIn(self.other_bed.id, self.dual_ward_nurse.location_ids.ids)

        self.assertEqual(self.hca.location_ids.ids, [])
        self.assertIn(self.other_bed.id, self.other_hca.location_ids.ids)
        self.assertIn(self.bed.id, self.dual_ward_hca.location_ids.ids)
        self.assertIn(self.other_bed.id, self.dual_ward_hca.location_ids.ids)

        self.assertIn(self.ward.id,  self.shift_coordinator.location_ids.ids)
        self.assertIn(
            self.other_ward.id, self.other_shift_coordinator.location_ids.ids)
