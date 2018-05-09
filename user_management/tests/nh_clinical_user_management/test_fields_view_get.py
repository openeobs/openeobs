from openerp.tests.common import SavepointCase


class TestFieldsViewGet(SavepointCase):

    def setUp(self):
        super(TestFieldsViewGet, self).setUp()
        self.user_management_model = self.env['nh.clinical.user.management']

    def test_no_category_ids_domain_for_superuser(self):
        """
        No domain means the available values for the 'Roles' field are not
        limited so the superuser can properly edit this field.
        """
        fields_view = self.user_management_model.sudo().fields_view_get()
        roles_domain = fields_view['fields']['category_id']['domain']
        self.assertEqual(roles_domain, [])
