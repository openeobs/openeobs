from openerp.osv import osv
import logging
import ldap
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class EOBSUsersLDAP(osv.osv):
    """
    Override of the auth_ldap/user_ldap.py file to set the opt_referrals flag
    properly to work with Active Directory server
    """

    _name = 'res.company.ldap'
    _inherit = 'res.company.ldap'

    def connect(self, conf):
        """
        Connect to an LDAP server specified by an ldap
        configuration dictionary.

        :param dict conf: LDAP configuration
        :return: an LDAP object
        """

        uri = 'ldap://%s:%d' % (conf['ldap_server'],
                                conf['ldap_server_port'])

        connection = ldap.initialize(uri)
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if conf['ldap_tls']:
            connection.start_tls_s()
        return connection

    def get_or_create_user(self, cr, uid, conf, login, ldap_entry,
                           context=None):
        """
        Retrieve an active resource of model res_users with the specified
        login. Create the user if it is not initially found.

        :param dict conf: LDAP configuration
        :param login: the user's login
        :param tuple ldap_entry: single LDAP result (dn, attrs)
        :return: res_users id
        :rtype: int
        """
        user_id = super(EOBSUsersLDAP, self).get_or_create_user(
            cr,
            uid,
            conf,
            login,
            ldap_entry,
            context=context
        )
        user_obj = self.pool['res.users']
        user_obj.write(
            cr,
            SUPERUSER_ID,
            user_id,
            {
                'ldap_authenticated': True
            },
            context=context
        )
        return user_id
