from openerp.tests.common import TransactionCase
from openerp.osv.osv import except_osv


class TestResUsersChangePassword(TransactionCase):
    """
    Test that the change_password method override on the res.users model has
    been applied successfully
    """

    def setUp(self):
        super(TestResUsersChangePassword, self).setUp()
        user_model = self.env['res.users']
        self.user = user_model.browse(self.uid)

    def test_raises_on_changing_ad_password(self):
        self.user.write({'ldap_authenticated': True})
        with self.assertRaises(except_osv):
            self.user.change_password('admin', 'new_password')

    def test_dont_raise_on_changing_non_ad_password(self):
        self.user.change_password('admin', 'new_password')
