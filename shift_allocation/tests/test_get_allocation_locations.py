from openerp.tests.common import SingleTransactionCase


class TestGetAllocationLocations(SingleTransactionCase):
    """
    Test the get_allocation_locations method on the
    nh.clinical.user.responsibility.allocation model
    """

    @classmethod
    def setUpClass(cls):
        super(TestGetAllocationLocations, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.alloc_pool = \
            cls.registry('nh.clinical.user.responsibility.allocation')
        groups_pool = cls.registry('res.groups')
        user_pool = cls.registry('res.users')

        # create Locations for use in test - in DB as need .id
        cls.ward_id = cls.location_pool.create(cr, uid, {
            'code': 'TESTWARD',
            'usage': 'ward',
            'name': 'Test Ward',
            'pos_id': 1
        })
        cls.ward = cls.location_pool.browse(cr, uid, cls.ward_id)

        cls.bed_id = cls.location_pool.create(cr, uid, {
            'code': 'TESTBED',
            'usage': 'bed',
            'name': 'Test Bed',
            'parent_id': cls.ward_id,
            'pos_id': 1
        })
        cls.bed = cls.location_pool.browse(cr, uid, cls.bed_id)

        # create groups & users - in memory
        hca_group = groups_pool.new(cr, uid, {
            'name': 'NH Clinical HCA Group'
        })
        cls.hca = user_pool.new(cr, uid, {
            'name': 'HCA',
            'login': 'hca',
            'groups_id': hca_group
        })

        nurse_group = groups_pool.new(cr, uid, {
            'name': 'NH Clinical Nurse Group'
        })
        cls.nurse = user_pool.new(cr, uid, {
            'name': 'Nurse',
            'login': 'nurse',
            'groups_id': nurse_group
        })

        shift_coordinator_group = groups_pool.new(cr, uid, {
            'name': 'NH Clinical Shift Coordinator Group'
        })
        cls.shift_coordinator = user_pool.new(cr, uid, {
            'name': 'Shift Coordinator',
            'login': 'shift_coordinator',
            'groups_id': shift_coordinator_group
        })

        senior_manager_group = groups_pool.new(cr, uid, {
            'name': 'NH Clinical Senior Manager Group'
        })

        cls.senior_manager = user_pool.new(cr, uid, {
            'name': 'Senior Manager',
            'login': 'senior_manager',
            'groups_id': senior_manager_group
        })

        doctor_group = groups_pool.new(cr, uid, {
            'name': 'NH Clinical Doctor Group'
        })

        cls.doctor = user_pool.new(cr, uid, {
            'name': 'Doctor',
            'login': 'doctor',
            'groups_id': doctor_group
        })

    def setUp(self):

        def mock_location_search(*args, **kwargs):
            """
            Mock out the location search used by get_allocation_locations to
            find the child_ids of a location
            :param args:
            :param kwargs:
            :return: A list of Bed IDS - in this case 'bed_search' as we won't
            use it
            """
            return ['bed_search']

        self.location_pool._patch_method('search', mock_location_search)

    def tearDown(self):
        self.location_pool._revert_method('search')
        super(TestGetAllocationLocations, self).tearDown()

    def get_locations(self, user, locations):
        """
        Helper function to get the
        :param user: user to use
        :param locations: location to use
        :return: Location list
        """
        cr, uid = self.cr, self.uid
        allocation = self.alloc_pool.new(cr, uid, {
            'responsible_user_id': user,
            'location_ids': locations
        })
        return self.alloc_pool.get_allocation_locations(
            cr, uid, allocation)

    def test_hca_group_ward(self):
        """
        If a HCA is assigned to the ward function should return beds in ward
        """
        locations = self.get_locations(self.hca, self.ward)
        self.assertEqual(locations, ['bed_search'])

    def test_hca_group_bed(self):
        """
        If a HCA is assigned to a bed function should return the bed
        """
        locations = self.get_locations(self.hca, self.bed)
        self.assertEqual(locations, ['bed_search'])

    def test_nurse_group_ward(self):
        """
        If a nurse is assigned to a ward function should return beds in ward
        """
        locations = self.get_locations(self.nurse, self.ward)
        self.assertEqual(locations, ['bed_search'])

    def test_nurse_group_bed(self):
        """
        If a nurse is assigned to a bed function should return bed
        """
        locations = self.get_locations(self.nurse, self.bed)
        self.assertEqual(locations, ['bed_search'])

    def test_shift_coordinator_group_ward(self):
        """
        If a ward manager is assigned to a ward function should return ward
        """
        locations = self.get_locations(self.shift_coordinator, self.ward)
        self.assertEqual(locations, [self.ward_id])

    def test_shift_coordinator_group_bed(self):
        """
        If a ward manager is assigned to a bed function should return bed
        """
        locations = self.get_locations(self.shift_coordinator, self.bed)
        self.assertEqual(locations, ['bed_search'])

    def test_senior_manager_group_ward(self):
        """
        If a senior manager is assigned to a ward function should return ward
        """
        locations = self.get_locations(self.senior_manager, self.ward)
        self.assertEqual(locations, [self.ward_id])

    def test_senior_manager_group_bed(self):
        """
        If a senior manager is assigned to a bed function should return bed
        """
        locations = self.get_locations(self.senior_manager, self.bed)
        self.assertEqual(locations, ['bed_search'])

    def test_doctor_group_ward(self):
        """
        If a doctor is assigned to a ward function should return ward
        """
        locations = self.get_locations(self.doctor, self.ward)
        self.assertEqual(locations, [self.ward_id])

    def test_doctor_group_bed(self):
        """
        If a doctor is assigned to a bed function should return bed
        """
        locations = self.get_locations(self.doctor, self.bed)
        self.assertEqual(locations, ['bed_search'])
