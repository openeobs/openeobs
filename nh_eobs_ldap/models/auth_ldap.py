from openerp.osv import osv
import logging
import ldap
from openerp import api

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
        connection = super(EOBSUsersLDAP, self).connect(conf)
        connection.set_option(ldap.OPT_REFERRALS, 0)
        return connection

    @api.multi
    def get_or_create_user(self, conf, login, ldap_entry):
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
            conf,
            login,
            ldap_entry
        )
        user_model = self.env['res.users']
        user_obj = user_model.browse(user_id)
        user_obj.sudo().write(
            {
                'ldap_authenticated': True
            }
        )
        return user_id
