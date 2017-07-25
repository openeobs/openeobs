from openerp.tests.common import TransactionCase


class TestUserLevelAssigingBedManagerRole(TransactionCase):
    """
    Test that only users at the System Administrator level can assign
    users to the Bed Manager role
    """

    def setUp(self):
        super(TestUserLevelAssigingBedManagerRole, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.user_management_model = self.env['nh.clinical.user.management']
        self.category_model = self.env['res.partner.category']
        self.test_utils.admit_and_place_patient()
        self.shift_coordinator = self.test_utils.create_shift_coordinator()
        self.test_utils.create_system_admin()

    def get_role_names(self, view):
        roles = self.category_model.browse(
            view.get('fields')
                .get('category_id')
                .get('domain')[0][2]
        )
        return [role.name for role in roles]

    def test_shift_coordinator_cant_assign(self):
        """
        Test that users at the shift coordinator level cannot assign
        the Bed Manager role
        """
        roles = self.get_role_names(
            self.user_management_model
                .sudo(self.shift_coordinator)
                .fields_view_get()
        )
        self.assertTrue('Bed Manager' not in roles)

    def test_system_admin_can_assign(self):
        """
        Test that users at the system administrator level can assign the
        Bed Manager role
        """
        roles = self.get_role_names(
            self.user_management_model
                .sudo(self.test_utils.system_admin)
                .fields_view_get()
        )
        self.assertTrue('Bed Manager' in roles)

    def test_super_user_cant_assign(self):
        """
        Test that users at the super user level can assign the Bed Manager
        role
        """
        roles = self.get_role_names(
            self.user_management_model.fields_view_get()
        )
        self.assertTrue('Bed Manager' not in roles)
