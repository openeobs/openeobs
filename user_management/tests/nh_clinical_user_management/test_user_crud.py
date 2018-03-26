from .user_management_case import UserManagementCase
from openerp.osv.orm import except_orm


class TestUserCRUD(UserManagementCase):
    """
    Test CRUD operations on users within user management
    """

    def setUp(self):
        super(TestUserCRUD, self).setUp()
        hca_data = {
            'name': 'HCA2',
            'login': 'hca2',
            'category_id': [[4, self.hca_role.id]]
        }
        self.hca = self.user_management_model\
            .sudo(self.shift_coordinator).create(hca_data)

    def test_creates_user(self):
        """
        Test that creating a user, creates a user
        """
        self.assertTrue(self.hca, msg="HCA user not created")
        self.assertEqual(self.hca.name, 'HCA2')
        self.assertEqual(self.hca.login, 'hca2')
        groups = [g.name for g in self.hca.groups_id]
        self.assertTrue('NH Clinical HCA Group' in groups,
                        msg="User created without HCA group")
        self.assertTrue('Employee' in groups,
                        msg="User created without Employee group")

    def test_can_update_subordinate(self):
        """
        Test that superior users can update subordinate user groups
        """
        update_data = {
            'name': 'TU2',
            'login': 'tu2',
            'category_id': [[6, 0, [self.nurse_role.id]]]
        }
        update = self.hca.sudo(self.shift_coordinator).write(update_data)
        self.assertTrue(update)
        self.assertEqual(self.hca.name, 'TU2')
        self.assertEqual(self.hca.login, 'tu2')
        groups = [g.name for g in self.hca.groups_id]
        self.assertFalse('NH Clinical HCA Group' in groups,
                         msg="HCA group not removed")
        self.assertTrue('NH Clinical Nurse Group' in groups,
                        msg="Nurse group missing")
        self.assertTrue('Employee' in groups, msg="Employee group removed")

    def test_cant_update_superiors(self):
        """
        Test that an exception is thrown when subordinate user tries to
        update
        user that is superior to them
        """
        update_data = {
            'name': 'TU3',
            'login': 'tu3',
            'category_id': [[6, 0, [self.nurse_role.id]]]
        }
        with self.assertRaises(except_orm):
            self.shift_coordinator.sudo(self.hca).write(update_data)
