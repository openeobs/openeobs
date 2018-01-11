from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import api


class EOBSResUsers(osv.osv):
    """
    Override of the Odoo's res.users class to add ldap_authenticated flag
    and override change_password to prevent ldap authenticated users from
    changing the password (as this will come from LDAP)
    """
    _name = "res.users"
    _inherit = "res.users"

    _columns = {
        'ldap_authenticated': fields.boolean(
            'User account is authenticated via LDAP/AD?')
    }

    _defaults = {
        'ldap_authenticated': False
    }

    @api.model
    def change_password(self, old_passwd, new_passwd):
        """Change current user password. Old password must be provided
        explicitly to prevent hijacking an existing user session, or for cases
        where the cleartext password is not used to authenticate requests.

        :return: True
        :raise: openerp.exceptions.AccessDenied when old password is wrong
        :raise: except_osv when password change is attemped on an account
        setup via Active Directory
        :raise: except_osv when new password is not set or empty
        """
        if self.ldap_authenticated:
            raise osv.except_osv(_('Warning!'), _(
                "Cannot change password for Trust managed account. "
                "Please contact IT to change your password."
            ))
        return super(EOBSResUsers, self)\
            .change_password(old_passwd, new_passwd)
