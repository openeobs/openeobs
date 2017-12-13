from openerp.tests.common import SingleTransactionCase


class TestAuthLdapGetOrCreateUserFlag(SingleTransactionCase):
    """
    Test that the ldap_authenticated flag is set on the res.users model
    """

    @classmethod
    def setUpClass(cls):
        super(TestAuthLdapGetOrCreateUserFlag, cls).setUpClass()
        cls.ldap_pool = cls.registry('res.company.ldap')
        cls.user_pool = cls.registry('res.users')

        cls.ldap_conf = {
            'ldap_server': '127.0.0.1',
            'ldap_server_port': 389,
            'ldap_tls': False,
            'create_user': True,
            'user': False
        }

        def patch_user_create(*args, **kwargs):
            return 666

        def patch_user_copy(*args, **kwargs):
            return 666

        def patch_map_ldap_attr(*args, **kwargs):
            return {}

        def mock_user_write(*args, **kwargs):
            global flag_passed
            vals = args[4]
            if vals.get('ldap_authenticated'):
                flag_passed = True

        cls.ldap_pool._patch_method('map_ldap_attributes', patch_map_ldap_attr)
        cls.user_pool._patch_method('create', patch_user_create)
        cls.user_pool._patch_method('copy', patch_user_copy)
        cls.user_pool._patch_method('write', mock_user_write)

    @classmethod
    def tearDownClass(cls):
        cls.ldap_pool._revert_method('map_ldap_attributes')
        cls.user_pool._revert_method('create')
        cls.user_pool._revert_method('copy')
        cls.user_pool._revert_method('write')
        super(TestAuthLdapGetOrCreateUserFlag, cls).tearDownClass()

    def test_add_flag_on_creating_user(self):
        """
        Test that the ldap_authenticated flag is set when creating a user
        via the auth_ldap module
        """
        cr, uid = self.cr, self.uid
        self.ldap_pool.get_or_create_user(
            cr, uid, self.ldap_conf, 'test_user', None)
        self.assertEqual(flag_passed, True)
