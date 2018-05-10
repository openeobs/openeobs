from openerp.osv.osv import except_osv

from .user_management_case import UserManagementCase


class TestCreate(UserManagementCase):
    """
    Test the create override.
    """
    def call_test(self, created_user_role, user_to_create_with,
                  create_with_ward_responsibility=False):
        creation_values = {
            'name': 'HCA2',
            'login': 'hca2',
            'category_id': [[4, created_user_role.id]]
        }
        if create_with_ward_responsibility:
            creation_values['ward_ids'] = [(6, 0, [self.ward.id])]
        if user_to_create_with:
            self.user_management_model = \
                self.user_management_model.sudo(
                    user_to_create_with
                )
        self.created_user = self.user_management_model.create(
            creation_values
        )

    def _assert_user_created(self, expected_group_name):
        self.assertTrue(self.created_user, msg="HCA user not created")
        self.assertEqual(self.created_user.name, 'HCA2')
        self.assertEqual(self.created_user.login, 'hca2')
        groups = [g.name for g in self.created_user.groups_id]
        self.assertTrue(
            expected_group_name in groups,
            msg="User created without '{}'.".format(expected_group_name)
        )
        self.assertTrue('Employee' in groups,
                        msg="User created without Employee group")

    def test_shift_coordinator_can_create_hca(self):
        """
        Test that creating a user, creates a user
        """
        self.call_test(
            created_user_role=self.hca_role,
            user_to_create_with=self.shift_coordinator
        )
        self._assert_user_created(expected_group_name='NH Clinical HCA Group')

    def test_superuser_can_create_hca(self):
        self.call_test(
            created_user_role=self.hca_role,
            user_to_create_with=self.superuser
        )
        self._assert_user_created(expected_group_name='NH Clinical HCA Group')

    def test_superuser_can_create_system_administrator(self):
        self.call_test(
            created_user_role=self.system_admin_role,
            user_to_create_with=self.superuser
        )
        self._assert_user_created(
            expected_group_name='NH Clinical Admin Group'
        )

    def test_cannot_create_hca_with_ward_responsibility(self):
        with self.assertRaises(except_osv):
            self.call_test(
                created_user_role=self.hca_role,
                user_to_create_with=self.superuser,
                create_with_ward_responsibility=True
            )

    def test_cannot_create_nurse_with_ward_responsibility(self):
        with self.assertRaises(except_osv):
            self.call_test(
                created_user_role=self.nurse_role,
                user_to_create_with=self.superuser,
                create_with_ward_responsibility=True
            )

    def test_can_create_shift_coordinator_with_ward_responsibility(self):
        self.call_test(
            created_user_role=self.shift_coordinator_role,
            user_to_create_with=self.superuser,
            create_with_ward_responsibility=True
        )
        self._assert_user_created(
            expected_group_name='NH Clinical Shift Coordinator Group'
        )
