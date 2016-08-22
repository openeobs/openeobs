from openerp.tests.common import TransactionCase


class TestStaffReallocationIntegration(TransactionCase):

    def setUp(self):
        super(TestStaffReallocationIntegration, self).setUp()
        cr, uid = self.cr, self.uid

        # set up pools
        self.location_pool = self.registry('nh.clinical.location')
        self.user_pool = self.registry('res.users')
        self.allocating_pool = self.registry('nh.clinical.allocating')
        self.allocation_pool = self.registry('nh.clinical.staff.reallocation')
        self.activity_pool = self.registry('nh.activity')
        self.resp_allocation_pool = self.registry(
            'nh.clinical.user.responsibility.allocation')
        self.patient_pool = self.registry('nh.clinical.patient')
        self.unfollow_pool = self.registry('nh.clinical.patient.unfollow')

        # get the ward, beds
        wards = self.location_pool.search(cr, uid, [['usage', '=', 'ward']])
        if not wards:
            raise ValueError('Unable to find ward to use for test')
        self.ward = wards[0]

        beds = self.location_pool.search(
            cr, uid, [['usage', '=', 'bed'], ['parent_id', '=', self.ward]])
        if not beds:
            raise ValueError('Unable to find beds to use for test')
        self.beds_in_ward = beds
        self.bed = beds[0]

        hcas = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical HCA Group'],
            ['location_ids', 'in', self.beds_in_ward]
        ])
        if not hcas:
            raise ValueError('Unable to find HCAs to use for test')
        self.hcas = hcas
        self.hca = hcas[0]

        nurses = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Nurse Group'],
            ['location_ids', 'in', self.beds_in_ward]
        ])
        if not nurses:
            raise ValueError('Unable to find Nurses to use for test')
        self.nurses = nurses
        self.nurse = nurses[0]

        shift_coordinators = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Shift Coordinator Group'],
            ['location_ids', 'in', [self.ward]]
        ])
        if not shift_coordinators:
            raise ValueError('Unable to find Shift Coordinators to use for test')
        self.shift_coordinator = shift_coordinators[0]

        senior_managers = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Senior Manager Group'],
            ['location_ids', 'in', [self.ward]]
        ])
        if not senior_managers:
            raise ValueError('Unable to find Senior Manager to use for test')
        self.senior_managers = senior_managers

        doctors = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Doctor Group'],
            ['location_ids', 'in', [self.ward]]
        ])
        if not doctors:
            raise ValueError('Unable to find Doctor to use for test')
        self.doctors = doctors
        self.wizard = self.allocation_pool.create(self.cr, self.shift_coordinator,
                                                  {})

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
        cr, uid = self.cr, self.uid

        # TODO: Add a follower to a patient to ensure it get removed
        self.allocation_pool.write(cr, self.shift_coordinator, self.wizard, {
            'user_ids': self.nurses.remove(self.nurse)
        })
        self.allocation_pool.reallocate(cr, self.shift_coordinator, self.wizard)

        wizard = self.allocation_pool.read(cr, uid, self.wizard,
                                           ['stage', 'allocating_ids'])

        self.assertEqual(wizard.get('stage'), 'allocation')

        # Check for responsibility allocations
        allocating_ids = self.allocating_pool.read(
            cr, uid, wizard.get('allocating_ids'), ['nurse_id'])
        for allocating_id in allocating_ids:
            self.assertNotEqual(allocating_id['nurse_id'], self.nurse)

    def test_reallocate_no_change(self):
        """
        Test that after reallocate is called the following has happened
        - Stage is changed to allocation
        """
        cr, uid = self.cr, self.uid
        self.allocation_pool.reallocate(cr, self.shift_coordinator, self.wizard)
        wizard = self.allocation_pool.read(cr, uid, self.wizard, ['stage'])
        self.assertEqual(wizard.get('stage'), 'allocation')

    def test_complete(self):
        """
        Test that on completing that the wizard now:
        - create responsibility allocation activities for the users and
        locations in the wizard
        """
        cr, uid = self.cr, self.uid
        self.allocation_pool.reallocate(cr, self.shift_coordinator, self.wizard)
        self.allocation_pool.complete(cr, self.shift_coordinator, self.wizard)
        resp_allocations = self.resp_allocation_pool.search(
            cr, uid, [['responsible_user_id', 'in', [self.nurse, self.hca]]])
        for resp_allocation in self.resp_allocation_pool.read(
                cr, uid, resp_allocations, ['location_ids']):
            self.assertIn(self.bed, resp_allocation.get('location_ids'))

    def test_shift_coordinator_uses_twice(self):
        """
        Test that on completing that the wizard now:
        - create responsibility allocation activities for the users and
        locations in the wizard
        """
        cr, uid = self.cr, self.uid
        self.allocation_pool.reallocate(cr, self.shift_coordinator, self.wizard)
        self.allocation_pool.complete(cr, self.shift_coordinator, self.wizard)

        wizard_2 = self.allocation_pool.create(cr, self.shift_coordinator, {})
        self.allocation_pool.reallocate(cr, self.shift_coordinator, wizard_2)
        self.allocation_pool.complete(cr, self.shift_coordinator, wizard_2)

        wm_loc = self.user_pool.read(cr, uid, self.shift_coordinator,
                                     ['location_ids'])
        self.assertIn(self.ward, wm_loc.get('location_ids'))
