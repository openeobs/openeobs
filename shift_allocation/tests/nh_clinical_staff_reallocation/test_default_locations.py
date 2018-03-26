from openerp.tests.common import SingleTransactionCase


class TestStaffReallocationDefaultLocations(SingleTransactionCase):

    BEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    @classmethod
    def setUpClass(cls):
        super(TestStaffReallocationDefaultLocations, cls).setUpClass()
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.allocation_pool = cls.registry('nh.clinical.staff.reallocation')

        def mock_get_default_wards(*args, **kwargs):
            context = kwargs.get('context')
            if context and context == 'check_get_ward':
                global ward_called
                ward_called = True
            return 666

        def mock_location_search(*args, **kwargs):
            context = kwargs.get('context')
            if context:
                if context == 'check_get_ward':
                    return []
                if context == 'check_search':
                    global location_search
                    location_search = args[3][0]
                    return [0]
            return cls.BEDS
        cls.allocation_pool._patch_method('_get_default_ward',
                                          mock_get_default_wards)
        cls.location_pool._patch_method('search', mock_location_search)

    @classmethod
    def tearDownClass(cls):
        cls.allocation_pool._revert_method('_get_default_ward')
        cls.location_pool._revert_method('search')
        super(TestStaffReallocationDefaultLocations, cls).tearDownClass()

    def test_calls_get_default_ward(self):
        """
        Test that it calls get_default_ward
        """
        self.allocation_pool._get_default_locations(self.cr, self.uid,
                                                    context='check_get_ward')
        self.assertTrue(ward_called)

    def test_uses_ward_id(self):
        """
        Test that it uses ward ID when searching for locations
        """
        self.allocation_pool._get_default_locations(self.cr, self.uid,
                                                    context='check_search')
        self.assertEqual(location_search, ['id', 'child_of', 666])

    def test_returns_beds(self):
        """
        Test that it returns the beds it finds
        """
        beds = self.allocation_pool._get_default_locations(self.cr, self.uid)
        self.assertEqual(beds, self.BEDS)
