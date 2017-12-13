from openerp.tests.common import SingleTransactionCase
from openerp.osv.osv import except_osv


class TestResUsersChangePassword(SingleTransactionCase):
    """
    Test that the change_password method override on the res.users model has
    been applied successfully
    """

    @classmethod
    def setUpClass(cls):
        super(TestResUsersChangePassword, cls).setUpClass()
        cls.user_pool = cls.registry('res.users')

        def patch_user_pool_write(*args, **kwargs):
            return True

        def patch_user_pool_check(*args, **kwargs):
            return True

        def patch_user_pool_read(*args, **kwargs):
            context = kwargs.get('context')
            test = context.get('test') if context else ''
            if test == 'ad_user':
                return {
                    'ldap_authenticated': True
                }
            return {
                'ldap_authenticated': False
            }

        cls.user_pool._patch_method('write', patch_user_pool_write)
        cls.user_pool._patch_method('check', patch_user_pool_check)
        cls.user_pool._patch_method('read', patch_user_pool_read)

    @classmethod
    def tearDownClass(cls):
        super(TestResUsersChangePassword, cls).tearDownClass()
        cls.user_pool._revert_method('write')
        cls.user_pool._revert_method('check')
        cls.user_pool._revert_method('read')

    def test_raises_on_changing_ad_password(self):
        with self.assertRaises(except_osv):
            self.user_pool.change_password(
                self.cr, 666, 'old_password', 'new_password',
                context={'test': 'ad_user'})
        pass

    def test_dont_raise_on_changing_non_ad_password(self):
        self.user_pool.change_password(
            self.cr, 666, 'old_password', 'new_password')
