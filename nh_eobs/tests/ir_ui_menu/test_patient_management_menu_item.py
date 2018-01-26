from .menu_item_common import MenuItemCase


class TestPatientManagementMenuItem(MenuItemCase):
    """
    Test that the Patient Management menu header is shown or hidden for various
    user groups
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestPatientManagementMenuItem, self).setUp()
        self.allowed_groups = \
            self.get_groups_for_menu_item('Patient Management')

    def test_hca_group(self):
        """
        Test that the HCA group can see the menu item
        """
        self.assertTrue('NH Clinical HCA Group' in self.allowed_groups)

    def test_nurse_group(self):
        """
        Test that the Nurse group can see the menu item
        """
        self.assertTrue('NH Clinical Nurse Group' in self.allowed_groups)

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
