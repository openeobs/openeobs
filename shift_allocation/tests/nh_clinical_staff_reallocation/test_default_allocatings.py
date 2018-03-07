from openerp.tests.common import SingleTransactionCase


class TestStaffReallocationDefaultAllocatings(SingleTransactionCase):

    BEDS = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    @classmethod
    def setUpClass(cls):
        super(TestStaffReallocationDefaultAllocatings, cls).setUpClass()
        cr, uid = cls.cr, cls.uid
        cls.allocating_pool = cls.registry('nh.clinical.allocating')
        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.allocation_pool = cls.registry('nh.clinical.staff.reallocation')

        nurse_group = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Nurse Group']])
        hca_group = cls.groups_pool.search(
            cr, uid, [['name', '=', 'NH Clinical HCA Group']])

        cls.bed = cls.location_pool.create(cr, uid, {
            'usage': 'bed',
            'name': 'Loc3',
            'type': 'poc',
            'parent_id': 1,
        })

        cls.nurse = cls.users_pool.create(cr, uid, {
            'name': 'Nurse 1',
            'groups_id': [[6, 0, nurse_group]],
            'login': 'complete_test_nurse1',
            'location_ids': [[6, 0, [cls.bed]]]
        })
        cls.hca = cls.users_pool.create(cr, uid, {
            'name': 'HCA 1',
            'groups_id': [[6, 0, hca_group]],
            'login': 'complete_test_hca1',
            'location_ids': [[6, 0, [cls.bed]]]
        })

        cls.bed_browse = cls.location_pool.browse(cr, uid, cls.bed)

        def mock_get_default_locations(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'check_get_locations':
                global location_called
                location_called = True
            return [cls.bed]

        def mock_location_browse(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'check_search':
                global sent_location_id
                sent_location_id = args[3]
            return mock_location_browse.origin(*args, **kwargs)

        def mock_allocating_create(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'check_create':
                global write_data
                write_data = args[3]
            return 1

        cls.allocation_pool._patch_method('_get_default_locations',
                                          mock_get_default_locations)
        cls.location_pool._patch_method('browse', mock_location_browse)
        cls.allocating_pool._patch_method('create', mock_allocating_create)

    @classmethod
    def tearDownClass(cls):
        cls.allocation_pool._revert_method('_get_default_locations')
        cls.location_pool._revert_method('browse')
        cls.allocating_pool._revert_method('create')
        super(TestStaffReallocationDefaultAllocatings, cls).tearDownClass()

    def test_calls_get_default_locations(self):
        """
        Test that it calls get_default_location
        """
        self.allocation_pool._get_default_allocatings(
            self.cr, self.uid, context={'test': 'check_get_locations'})
        self.assertTrue(location_called)

    def test_uses_location_ids_in_search(self):
        """
        Test that it uses location IDs when searching for users
        """
        self.allocation_pool._get_default_allocatings(
            self.cr, self.uid, context={'test': 'check_search'})
        self.assertEqual(sent_location_id[0], self.bed)

    def test_creates_allocating(self):
        """
        Test that it returns the users it finds
        """
        self.allocation_pool._get_default_allocatings(
            self.cr, self.uid, context={'test': 'check_create'})
        self.assertEqual(write_data, {
            'location_id': self.bed,
            'nurse_id': self.nurse,
            'hca_ids': [[6, 0, [self.hca]]]
        })
