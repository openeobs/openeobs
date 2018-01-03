from openerp.tests.common import TransactionCase


class TestAuthLdapGetOrCreateUserFlag(TransactionCase):
    """
    Test that the ldap_authenticated flag is set on the res.users model
    """

    def setUp(self):
        super(TestAuthLdapGetOrCreateUserFlag, self).setUp()
        self.ldap_model = self.env['res.company.ldap']
        self.user_model = self.env['res.users']

        self.ldap_conf = {
            'ldap_server': '127.0.0.1',
            'ldap_server_port': 389,
            'ldap_tls': False,
            'create_user': True,
            'user': False,
            'company': 1
        }

        self.ldap_entry = (
            'test',
            {
                'cn': ('foo', 'bar')
            }
        )

    def test_add_flag_on_creating_user(self):
        """
        Test that the ldap_authenticated flag is set when creating a user
        via the auth_ldap module
        """
        self.ldap_model.get_or_create_user(
            self.ldap_conf,
            'test_user',
            self.ldap_entry
        )
        user = self.user_model.search([['login', '=', 'test_user']])[0]
        self.assertEqual(user.ldap_authenticated, True)
