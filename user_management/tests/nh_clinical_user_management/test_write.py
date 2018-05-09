from openerp.osv.orm import except_orm

from .user_management_case import UserManagementCase


class TestUserCRUD(UserManagementCase):
    """
    Test CRUD operations on users within user management
    """
    def call_test(self, user=None):
        hca_data = {
            'name': 'HCA2',
            'login': 'hca2',
            'category_id': [[4, self.hca_role.id]]
        }
        if user:
            self.user_management_model = self.user_management_model.sudo(user)
        self.hca = self.user_management_model.create(hca_data)

    def _assert_subordinate_updated(self, update):
        self.assertTrue(update)
        self.assertEqual(self.hca.name, 'TU2')
        self.assertEqual(self.hca.login, 'tu2')
        groups = [g.name for g in self.hca.groups_id]
        self.assertFalse('NH Clinical HCA Group' in groups,
                         msg="HCA group not removed")
        self.assertTrue('NH Clinical Nurse Group' in groups,
                        msg="Nurse group missing")
        self.assertTrue('Employee' in groups, msg="Employee group removed")

    def test_can_update_subordinate(self):
        """
        Test that superior users can update subordinate user groups
        """
        self.call_test(user=self.shift_coordinator)
        update_data = {
            'name': 'TU2',
            'login': 'tu2',
            'category_id': [[6, 0, [self.nurse_role.id]]]
        }
        update = self.hca.sudo(self.shift_coordinator).write(update_data)
        self._assert_subordinate_updated(update)

    def test_superuser_can_update_subordinate(self):
        self.call_test()
        update_data = {
            'name': 'TU2',
            'login': 'tu2',
            'category_id': [[6, 0, [self.nurse_role.id]]]
        }
        update = self.hca.write(update_data)
        self._assert_subordinate_updated(update)

    def test_cant_update_superiors(self):
        """
        Test that an exception is thrown when subordinate user tries to
        update
        user that is superior to them
        """
        self.call_test(user=self.shift_coordinator)

        update_data = {
            'name': 'TU3',
            'login': 'tu3',
            'category_id': [[6, 0, [self.nurse_role.id]]]
        }
        with self.assertRaises(except_orm):
            self.shift_coordinator.sudo(self.hca).write(update_data)

    def test_superuser_can_update_superiors(self):
        self.call_test()

        update_data = {
            'name': 'TU3',
            'login': 'tu3',
            'category_id': [[6, 0, [self.nurse_role.id]]]
        }
        self.shift_coordinator.write(update_data)
