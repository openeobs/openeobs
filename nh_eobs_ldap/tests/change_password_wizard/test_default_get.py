from openerp.tests.common import TransactionCase
from openerp.osv.osv import except_osv


class TestDefaultGet(TransactionCase):
    """
    Test the default_get method of the the change.password.wizard model
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestDefaultGet, self).setUp()
        self.wizard_model = self.env['change.password.wizard']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.user_model = self.env['res.users']
        self.nurse = self.test_utils.create_nurse(location_id=1)
        self.hca = self.test_utils.create_hca(location_id=1)
        self.nurse.write({'ldap_authenticated': True})

    def test_ad_authed_users(self):
        """
        Test that default_get raises if all the users are authenticated by
        Active Directory
        """
        with self.assertRaises(except_osv):
            self.wizard_model\
                .with_context({'active_ids': [self.nurse.id]})\
                .create([])

    def test_non_authed_users(self):
        """
        Test that default_get returns the list of users if all of them aren't
        authenticated by Active Directory
        """
        wizard = self.wizard_model\
            .with_context({'active_ids': [self.hca.id]})\
            .create([])
        self.assertEqual(wizard.user_ids.user_id.id, self.hca.id)

    def test_strips_ad_authed_users(self):
        """
        Test that default_get only returns a list of user's that aren't
        authenticated by Active Directory when a mix of users is passed
        """
        wizard = self.wizard_model \
            .with_context({'active_ids': [self.nurse.id, self.hca.id]}) \
            .create([])
        self.assertEqual(wizard.user_ids.user_id.id, self.hca.id)
