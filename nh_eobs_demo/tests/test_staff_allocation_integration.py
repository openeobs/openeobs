from openerp.tests.common import TransactionCase


class TestStaffAllocationIntegration(TransactionCase):

    def setUp(self):
        super(TestStaffAllocationIntegration, self).setUp()
        cr, uid = self.cr, self.uid

        # set up pools
        self.location_pool = self.registry('nh.clinical.location')
        self.user_pool = self.registry('res.users')
        self.allocating_pool = self.registry('nh.clinical.allocating')
        self.allocation_pool = self.registry('nh.clinical.staff.allocation')
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

        hcas = self.user_pool.search(cr, uid, [['groups_id.name', '=',
                                               'NH Clinical HCA Group']])
        if not hcas:
            raise ValueError('Unable to find HCAs to use for test')
        self.hca = hcas[0]

        nurses = self.user_pool.search(cr, uid, [['groups_id.name', '=',
                                                 'NH Clinical Nurse Group']])
        if not nurses:
            raise ValueError('Unable to find Nurses to use for test')
        self.nurse = nurses[0]

        shift_coordinators = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Shift Coordinator Group']])
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
                                                  {'ward_id': self.ward})

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

    def test_submit_ward(self):
        """
        Test that after submit ward is called the following has happened:
        - Wizard is on stage 'review'
        - Wizard now has location_ids set to beds in ward
        - All users are still allocated to the wards to the wards they were
          allocated to
        """
        cr, uid = self.cr, self.uid
        self.allocation_pool.submit_ward(cr, self.shift_coordinator, self.wizard)

        # Get the wizard
        wizard = self.allocation_pool.read(cr, uid, self.wizard,
                                           ['stage', 'location_ids'])
        self.assertEqual(wizard.get('stage'), 'review')
        locations = [self.ward] + self.beds_in_ward
        self.assertEqual(wizard.get('location_ids'), locations)
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
        cr, uid = self.cr, self.uid

        # TODO: Add a follower to a patient to ensure it get removed
        self.allocation_pool.submit_ward(cr, self.shift_coordinator, self.wizard)
        self.allocation_pool.deallocate(cr, self.shift_coordinator, self.wizard)

        wizard = self.allocation_pool.read(cr, uid, self.wizard,
                                           ['stage', 'location_ids',
                                            'allocating_ids'])

        self.assertEqual(wizard.get('stage'), 'users')
        locations = [self.ward] + self.beds_in_ward
        self.assertEqual(wizard.get('location_ids'), locations)

        # User allocation check
        self.assertFalse(self.check_user_groups('hca', locations))
        self.assertFalse(self.check_user_groups('nurse', locations))
        self.assertTrue(self.check_user_groups('shift_coordinator', locations))
        self.assertTrue(self.check_user_groups('senior_manager', locations))
        self.assertTrue(self.check_user_groups('doctor', locations))

        # Patient Follower Check
        patient_ids = self.patient_pool.search(cr, uid, [
            ['current_location_id', 'in', locations]])
        patients = self.patient_pool.read(cr, uid, patient_ids,
                                          ['follower_ids'])
        for patient in patients:
            self.assertFalse(self.hca in patient.get('follower_ids'))
            self.assertFalse(self.nurse in patient.get('follower_ids'))

        # Check for responsibility allocations
        allocating_ids = self.allocating_pool.read(
            cr, uid, wizard.get('allocating_ids'), ['location_id'])
        for allocating_id in allocating_ids:
            self.assertIn(allocating_id['location_id'][0], locations)

    def test_submit_users(self):
        """
        Test that on submitting users that the wizard is now:
        - on stage 'allocation'
        - holding the list of user_ids from the roll call(filled in by the GUI)
        """
        cr, uid = self.cr, self.uid
        self.allocation_pool.submit_ward(cr, self.shift_coordinator, self.wizard)
        self.allocation_pool.deallocate(cr, self.shift_coordinator, self.wizard)
        self.allocation_pool.write(cr, uid, self.wizard, {
            'user_ids': [[6, 0, [self.hca, self.nurse]]]})
        self.allocation_pool.submit_users(cr, self.shift_coordinator, self.wizard)
        wizard = self.allocation_pool.read(cr, self.shift_coordinator, self.wizard,
                                           ['stage', 'user_ids'])
        self.assertEqual(wizard.get('stage'), 'allocation')
        self.assertEqual(wizard.get('user_ids'), [self.hca, self.nurse])

    def test_complete(self):
        """
        Test that on completing that the wizard now:
        - create responsibility allocation activities for the users and
        locations in the wizard
        """
        cr, uid = self.cr, self.uid
        self.allocation_pool.submit_ward(cr, self.shift_coordinator, self.wizard)
        self.allocation_pool.deallocate(cr, self.shift_coordinator, self.wizard)
        self.allocation_pool.write(cr, uid, self.wizard, {
            'user_ids': [[6, 0, [self.hca, self.nurse]]]})
        self.allocation_pool.submit_users(cr, self.shift_coordinator, self.wizard)
        wizard = self.allocation_pool.read(cr, self.shift_coordinator, self.wizard,
                                           ['allocating_ids'])
        self.allocating_pool.write(cr, uid, wizard.get('allocating_ids')[0],
                                   {
                                       'nurse_id': self.nurse,
                                       'hca_ids': [[6, 0, [self.hca]]],
                                       'location_id': self.bed})
        self.allocation_pool.complete(cr, self.shift_coordinator, self.wizard)
        resp_allocations = self.resp_allocation_pool.search(
            cr, uid, [['responsible_user_id', 'in', [self.nurse, self.hca]]])
        for resp_allocation in self.resp_allocation_pool.read(
                cr, uid, resp_allocations, ['location_ids']):
            self.assertEqual(resp_allocation.get('location_ids'), [self.bed])
