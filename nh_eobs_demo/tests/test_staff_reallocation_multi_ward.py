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
        if not wards and len(wards) < 2:
            raise ValueError('Unable to find ward to use for test')
        self.ward_a = wards[0]
        self.ward_b = wards[1]

        ward_a_beds = self.location_pool.search(
            cr, uid, [['usage', '=', 'bed'], ['parent_id', '=', self.ward_a]])
        ward_b_beds = self.location_pool.search(
            cr, uid, [['usage', '=', 'bed'], ['parent_id', '=', self.ward_b]])
        if not ward_a_beds and not ward_b_beds:
            raise ValueError('Unable to find beds to use for test')
        self.beds_in_ward_a = ward_a_beds
        self.beds_in_ward_b = ward_b_beds
        self.ward_a_bed = ward_a_beds[0]
        self.ward_b_bed = ward_b_beds[0]

        ward_a_hcas = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical HCA Group'],
            ['location_ids', 'in', ward_a_beds]
        ])
        ward_b_hcas = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical HCA Group'],
            ['location_ids', 'in', ward_b_beds]
        ])
        if not ward_a_hcas and not ward_b_hcas and len(ward_a_hcas) < 2:
            raise ValueError('Unable to find HCAs to use for test')
        self.ward_a_hca = ward_a_hcas[0]
        self.ward_b_hca = ward_b_hcas[0]
        self.dual_ward_hca = ward_a_hcas[1]

        ward_a_nurses = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Nurse Group'],
            ['location_ids', 'in', ward_a_beds]
        ])
        ward_b_nurses = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Nurse Group'],
            ['location_ids', 'in', ward_b_beds]
        ])
        if not ward_a_nurses and not ward_b_nurses and len(ward_a_nurses) < 2:
            raise ValueError('Unable to find Nurses to use for test')
        self.ward_a_nurse = ward_a_nurses[0]
        self.ward_b_nurse = ward_b_nurses[0]
        self.dual_ward_nurse = ward_a_nurses[1]

        ward_a_shift_coordinator = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Shift Coordinator Group'],
            ['location_ids', 'in', [self.ward_a]]
        ])
        ward_b_shift_coordinators = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Shift Coordinator Group'],
            ['location_ids', 'in', [self.ward_b]]
        ])
        if not ward_a_shift_coordinator and not ward_b_shift_coordinators:
            raise ValueError('Unable to find Shift Coordinators to use for test')
        self.ward_a_shift_coordinator = ward_a_shift_coordinator[0]
        self.ward_b_shift_coordinator = ward_b_shift_coordinators[0]

        # Set up the allocation so dual HCA & Nurse are on both wards
        self.allocation_pool.responsibility_allocation_activity(
            cr, uid, self.dual_ward_nurse, [self.ward_a_bed, self.ward_b_bed])
        self.allocation_pool.responsibility_allocation_activity(
            cr, uid, self.dual_ward_hca, [self.ward_a_bed, self.ward_b_bed])
        self.wizard = self.allocation_pool.create(
            self.cr, self.ward_a_shift_coordinator, {})
        self.allocation_pool.reallocate(cr, self.ward_a_shift_coordinator,
                                        self.wizard)
        self.allocation_pool.complete(cr, self.ward_a_shift_coordinator,
                                      self.wizard)

    def test_reallocate_only_affects_chosen_ward(self):
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
        cr, uid = self.cr, self.uid
        ward_a_nurse = self.user_pool.read(cr, uid, self.ward_a_nurse,
                                           ['location_ids'])
        for location in ward_a_nurse.get('location_ids'):
            self.assertIn(location, self.beds_in_ward_a)

        ward_b_nurse = self.user_pool.read(cr, uid, self.ward_b_nurse,
                                           ['location_ids'])
        for location_id in ward_b_nurse.get('location_ids'):
            self.assertIn(location_id, self.beds_in_ward_b)

        dual_ward_nurse = self.user_pool.read(cr, uid, self.dual_ward_nurse,
                                              ['location_ids'])
        self.assertIn(self.ward_a_bed, dual_ward_nurse.get('location_ids'))
        self.assertIn(self.ward_b_bed, dual_ward_nurse.get('location_ids'))

        ward_a_hca = self.user_pool.read(cr, uid, self.ward_a_hca,
                                         ['location_ids'])
        for location in ward_a_hca.get('location_ids'):
            self.assertIn(location, self.beds_in_ward_a)

        ward_b_hca = self.user_pool.read(cr, uid, self.ward_b_hca,
                                         ['location_ids'])
        for location_id in ward_b_hca.get('location_ids'):
            self.assertIn(location_id, self.beds_in_ward_b)

        dual_ward_hca = self.user_pool.read(cr, uid, self.dual_ward_hca,
                                            ['location_ids'])
        self.assertIn(self.ward_a_bed, dual_ward_hca.get('location_ids'))
        self.assertIn(self.ward_b_bed, dual_ward_hca.get('location_ids'))

        ward_a_shift_coordinator = self.user_pool.read(cr, uid,
                                                  self.ward_a_shift_coordinator,
                                                  ['location_ids'])
        self.assertIn(self.ward_a, ward_a_shift_coordinator.get('location_ids'))
        ward_b_shift_coordinator = self.user_pool.read(cr, uid,
                                                  self.ward_b_shift_coordinator,
                                                  ['location_ids'])
        self.assertIn(self.ward_b, ward_b_shift_coordinator.get('location_ids'))
