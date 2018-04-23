from openerp.tests.common import TransactionCase


class TestStaffAllocationIntegration(TransactionCase):

    def setUp(self):
        super(TestStaffAllocationIntegration, self).setUp()
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
        self.test_utils_model.create_senior_manager()
        items_needed = [
            'ward',
            'senior_manager',
            'hca',
            'nurse',
            'bed',
            'doctor'
        ]
        for item in items_needed:
            self.test_utils_model.copy_instance_variable_if_exists(self, item)
        self.wizard = self.allocation_pool\
            .sudo(self.shift_coordinator)\
            .create({'ward_id': self.ward.id})

    def check_user_groups(self, group, locations):
        groups_to_name = {
            'hca': 'NH Clinical HCA Group',
            'nurse': 'NH Clinical Nurse Group',
            'shift_coordinator': 'NH Clinical Shift Coordinator Group',
            'senior_manager': 'NH Clinical Senior Manager Group',
            'doctor': 'NH Clinical Doctor Group'
        }
        users = self.user_pool.search([
            ['groups_id.name', '=', groups_to_name.get(group)],
            ['location_ids', 'in', list(locations)]
        ])
        return users

    def test_submit_ward(self):
        """
        Test that after submit ward is called the following has happened:
        - Wizard is on stage 'review'
        - Wizard now has location_ids set to beds in ward
        - All users are still allocated to the wards to the wards they were
          allocated to
        """
        self.wizard.submit_ward()
        self.assertEqual(self.wizard.stage, 'review')
        locations = (self.ward.id, self.bed.id)
        self.assertEqual(self.wizard.location_ids._ids, locations)
        self.assertTrue(self.check_user_groups('hca', locations))
        self.assertTrue(self.check_user_groups('nurse', locations))
        self.assertTrue(self.check_user_groups('shift_coordinator', locations))
        self.assertTrue(self.check_user_groups('senior_manager', locations))
        self.assertTrue(self.check_user_groups('doctor', locations))

    def test_deallocate(self):
        """
        Test that after deallocate is called that the following has happend:
        - Wizard is on stage 'users'
        - Wizard has a bunch of allocating ids which correlate to allocating
          pool objects with the bed as a location_id
        - The location_ids for the HCA, Nurse and Ward Manager users have been
          'unlinked' so they no longer are assigned to those beds
        - All patients that are in the ward that had followers (from stand in)
          will no longer have those followers
        - A responsibility allocation activity would be created and completed
        """

        # TODO: Add a follower to a patient to ensure it get removed
        self.wizard.submit_ward()
        self.wizard.deallocate()
        self.assertEqual(self.wizard.stage, 'users')
        locations = (self.ward.id, self.bed.id)
        self.assertEqual(self.wizard.location_ids._ids, locations)
        self.assertFalse(self.check_user_groups('hca', locations))
        self.assertFalse(self.check_user_groups('nurse', locations))
        self.assertTrue(self.check_user_groups('shift_coordinator', locations))
        self.assertTrue(self.check_user_groups('senior_manager', locations))
        self.assertTrue(self.check_user_groups('doctor', locations))

        # Patient Follower Check
        patients = self.patient_pool.search(
            [['current_location_id', 'in', list(locations)]])
        for patient in patients:
            self.assertFalse(self.hca.id in patient.follower_ids._ids)
            self.assertFalse(self.nurse.id in patient.follower_ids._ids)

        for allocating_id in self.wizard.allocating_ids:
            self.assertIn(allocating_id.location_id.id, locations)

    def test_submit_users(self):
        """
        Test that on submitting users that the wizard is now:
        - on stage 'allocation'
        - holding the list of user_ids from the roll call(filled in by the GUI)
        """
        self.wizard.submit_ward()
        self.wizard.deallocate()
        users = [self.hca.id, self.nurse.id]
        self.wizard.write(
            {
                'user_ids': [[6, 0, users]]
            }
        )
        self.wizard.submit_users()
        self.assertEqual(self.wizard.stage, 'allocation')
        self.assertEqual(list(self.wizard.user_ids._ids), users)

    def test_complete(self):
        """
        Test that on completing that the wizard now:
        - create responsibility allocation activities for the users and
        locations in the wizard
        """
        self.wizard.submit_ward()
        self.wizard.deallocate()
        users = (self.hca.id, self.nurse.id)
        self.wizard.write(
            {
                'user_ids': [[6, 0, list(users)]]
            }
        )
        self.wizard.submit_users()
        self.wizard.allocating_ids.write(
            {
                'nurse_id': self.nurse.id,
                'hca_ids': [[6, 0, [self.hca.id]]],
                'location_id': self.bed.id
            }
        )
        self.wizard.complete()
        resp_allocations = self.resp_allocation_pool.search(
            [
                ['responsible_user_id', 'in', [self.nurse.id, self.hca.id]]
            ])
        for resp_allocation in resp_allocations:
            self.assertEqual(resp_allocation.location_ids.ids, [self.bed.id])

    def test_complete_only_sets_staff_in_wizard_on_shift(self):
        """
        Only the staff in the 'Nursing staff on shift' field in the wizard
        should be on the shift after the complete method is called.
        """
        self.wizard.submit_ward()
        self.wizard.deallocate()

        nurse = self.test_utils_model.create_nurse()
        hca = self.test_utils_model.create_hca()
        self.wizard.user_ids -= self.nurse
        self.wizard.user_ids -= self.hca
        self.wizard.user_ids += nurse
        self.wizard.user_ids += hca

        self.wizard.submit_users()
        self.wizard.complete()

        shift_model = self.env['nh.clinical.shift']
        shift = shift_model.get_latest_shift_for_ward(self.ward.id)

        expected_users = nurse + hca
        actual_users = shift.nurses + shift.hcas
        self.assertEqual(expected_users, actual_users)
