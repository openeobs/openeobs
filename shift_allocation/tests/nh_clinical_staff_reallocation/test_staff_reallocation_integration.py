from openerp.tests.common import TransactionCase


class TestStaffReallocationIntegration(TransactionCase):

    def setUp(self):
        super(TestStaffReallocationIntegration, self).setUp()
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
        # self.other_nurse = self.test_utils_model.create_nurse()
        self.allocation_pool \
            .sudo(self.shift_coordinator) \
            .create({
                'ward_id': self.ward.id,
                'user_ids': [(6, 0, [self.nurse.id, self.hca.id])]
            }) \
            .complete()
        self.wizard = self.reallocation_pool \
            .sudo(self.shift_coordinator) \
            .create({'ward_id': self.ward.id})

    def check_user_groups(self, group, locations):
        groups_to_name = {
            'hca': 'NH Clinical HCA Group',
            'nurse': 'NH Clinical Nurse Group',
            'shift_coordinator': 'NH Clinical Shift Coordinator Group',
            'senior_manager': 'NH Clinical Senior Manager Group',
            'doctor': 'NH Clinical Doctor Group'
        }
        users = self.user_pool.search(self.cr, self.uid, [
            ['groups_id.name', '=', groups_to_name.get(group)],
            ['location_ids', 'in', locations]
        ])
        return users

    def test_reallocate_change(self):
        """
        Test that after reallocate is called the following has happened
        - Stage is changed to allocation
        - The users not present in the wizard are removed
        """
        self.wizard.write({
            'user_ids': [[6, 0, [self.hca.id]]]
        })
        self.wizard.reallocate()
        self.assertEqual(self.wizard.stage, 'allocation')

        for allocating_id in self.wizard.allocating_ids:
            self.assertNotEqual(allocating_id.nurse_id.id, self.nurse.id)

    def test_reallocate_no_change(self):
        """
        Test that after reallocate is called the following has happened
        - Stage is changed to allocation
        """
        self.wizard.reallocate()
        self.assertEqual(self.wizard.stage, 'allocation')

    def test_complete(self):
        """
        Test that on completing that the wizard now:
        - create responsibility allocation activities for the users and
        locations in the wizard
        """
        self.wizard.reallocate()
        self.wizard.complete()
        resp_allocations = self.resp_allocation_pool.search(
            [['responsible_user_id', 'in', [self.nurse.id, self.hca.id]]])
        for resp_allocation in resp_allocations:
            self.assertIn(self.bed.id, resp_allocation.location_ids.ids)

    def test_shift_coordinator_uses_twice(self):
        """
        Test that on completing that the wizard now:
        - create responsibility allocation activities for the users and
        locations in the wizard
        """
        self.wizard.reallocate()
        self.wizard.complete()

        wizard_2 = self.reallocation_pool\
            .sudo(self.shift_coordinator)\
            .create({})
        wizard_2.reallocate()
        wizard_2.complete()
        # may need to update reference for sc
        shift_coordinator_update = \
            self.user_pool.browse(self.shift_coordinator.id)
        self.assertIn(self.ward.id, shift_coordinator_update.location_ids.ids)
