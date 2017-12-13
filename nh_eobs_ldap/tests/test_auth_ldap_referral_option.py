from openerp.tests.common import SingleTransactionCase
import ldap


class TestAuthLdapReferralOption(SingleTransactionCase):
    """
    Test that the connection method is applying the referral option needed for
    eObs to work with SLaM's Active Directory server
    """

    @classmethod
    def setUpClass(cls):
        super(TestAuthLdapReferralOption, cls).setUpClass()
        cls.ldap_pool = cls.registry('res.company.ldap')

    def test_connection_sets_flag(self):
        """
        Test that the ldap.REFERRALS flag is in the connection options
        """
        connection = self.ldap_pool.connect({
            'ldap_server': '127.0.0.1',
            'ldap_server_port': 389,
            'ldap_tls': False
        })
        self.assertEqual(connection.get_option(ldap.OPT_REFERRALS), 0)
