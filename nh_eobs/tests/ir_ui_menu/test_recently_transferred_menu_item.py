from .menu_item_common import MenuItemCase


class TestRecentlyTransferredMenuItem(MenuItemCase):
    """
    Test that the Recently Transferred menu item is shown or hidden for various
    user groups
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestRecentlyTransferredMenuItem, self).setUp()
        self.allowed_groups = \
            self.get_groups_for_menu_item('Recently Transferred')

    def test_hca_group(self):
        """
        Test that the HCA group cannot see the menu item
        """
        self.assertFalse('NH Clinical HCA Group' in self.allowed_groups)

    def test_nurse_group(self):
        """
        Test that the Nurse group cannot see the menu item
        """
        self.assertFalse('NH Clinical Nurse Group' in self.allowed_groups)

    def test_doctor_group(self):
        """
        Test that the Doctor group can see the menu item
        """
        self.assertTrue('NH Clinical Doctor Group' in self.allowed_groups)

    def test_shift_coordinator_group(self):
        """
        Test that the Shift Coordinator group can see the menu item
        """
        self.assertTrue(
            'NH Clinical Shift Coordinator Group' in self.allowed_groups)

    def test_senior_manager_group(self):
        """
        Test that the Senior Manager group can see the menu item
        """
        self.assertTrue(
            'NH Clinical Senior Manager Group' in self.allowed_groups)

    def test_system_admin_group(self):
        """
        test that the System Admin group cannot see the menu item
        """
        self.assertTrue(
            'NH Clinical Admin Group' in self.allowed_groups)
