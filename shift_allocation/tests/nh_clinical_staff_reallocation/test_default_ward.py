from openerp.tests.common import SingleTransactionCase
from openerp.osv import osv


class TestStaffReallocationDefaultWard(SingleTransactionCase):

    WARDS = [128, 256, 512]

    @classmethod
    def setUpClass(cls):
        super(TestStaffReallocationDefaultWard, cls).setUpClass()
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.allocation_pool = cls.registry('nh.clinical.staff.reallocation')

        def mock_location_search(*args, **kwargs):
            context = kwargs.get('context')
            if context:
                if context == 'get_ward_none':
                    return []
                if context == 'get_ward_multi':
                    return cls.WARDS
            return [1]
        cls.location_pool._patch_method('search', mock_location_search)

    @classmethod
    def tearDownClass(cls):
        cls.location_pool._revert_method('search')
        super(TestStaffReallocationDefaultWard, cls).tearDownClass()

    def test_raises_on_user_not_assigned(self):
        """
        Test that it raises an exception when the user is not assigned to any
        wards
        """
        with self.assertRaises(osv.except_osv) as error:
            self.allocation_pool._get_default_ward(self.cr, self.uid,
                                                   context='get_ward_none')
        self.assertEqual(error.exception.name, 'Shift Management Error!')
        self.assertEqual(error.exception.value,
                         'You must be in charge of a ward to do this task!')

    def test_returns_first_ward_id(self):
        """
        Test that it returns the first ward ID from the search
        """
        ward = self.allocation_pool._get_default_ward(self.cr, self.uid,
                                                      context='get_ward_multi')
        self.assertEqual(ward, self.WARDS[0])

    def test_returns_ward(self):
        """
        Test that it returns the ward it finds
        """
        ward = self.allocation_pool._get_default_ward(self.cr, self.uid)
        self.assertEqual(ward, 1)
