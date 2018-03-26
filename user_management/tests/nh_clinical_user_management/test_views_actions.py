from .user_management_case import UserManagementCase


class TestViewsActions(UserManagementCase):
    """
    Test that the views and actions returned by the server are correct
    """

    def setUp(self):
        super(TestViewsActions, self).setUp()
        self.hca = self.test_utils_model.create_hca()

    def test_allocate_responsibility(self):
        hca_record = self.user_management_model.sudo(self.shift_coordinator)\
            .browse(self.hca.id)
        res = hca_record.allocate_responsibility()
        self.assertDictEqual(
            res,
            {
                'type': 'ir.actions.act_window',
                'res_model': 'nh.clinical.responsibility.allocation',
                'name': 'Location Responsibility Allocation',
                'view_mode': 'form',
                'view_type': 'tree,form',
                'target': 'new',
                'context': {
                    'default_user_id': self.hca.id
                }
            }
        )

    def test_fields_view_get_tree(self):
        """
        Test that fields_view_get returns the correct result when asking for
        the tree view
        """
        self.assertTrue(
            self.user_management_model.sudo(self.shift_coordinator)
                .fields_view_get(view_id=None, view_type='tree')
        )

    def test_fields_view_get_form(self):
        """
        Test that fields_view_get returns the correct result when asking for
        the form view
        """
        res = self.user_management_model.sudo(self.shift_coordinator)\
            .fields_view_get()
        self.assertTrue(res)
        domain = res['fields']['category_id']['domain']
        self.assertEqual(len(domain), 1)
        self.assertEqual(domain[0][0], 'id')
        self.assertEqual(domain[0][1], 'in')
        ids = domain[0][2]
        self.assertIn(self.shift_coordinator_role.id, ids)
        self.assertIn(self.nurse_role.id, ids)
        self.assertIn(self.hca_role.id, ids)
