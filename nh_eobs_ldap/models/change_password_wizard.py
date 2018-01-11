from openerp.osv import orm, osv
from openerp.tools.translate import _
from openerp import api


class EOBSChangePasswordWizard(orm.TransientModel):
    """
    Change password wizard displayed in the more menu on user.management
    screen
    """
    _name = "change.password.wizard"
    _inherit = "change.password.wizard"

    @api.model
    def default_get(self, fields):
        """
        Override the default get for password change so that user's who have
        been set up via AD can't have their passwords changed

        :param fields: fields to get
        :return: list of mappings of user id and user name for users not added
        via AD
        :raises: if no non-AD users are selected
        """
        user_model = self.env['res.users']
        user_ids = self._context.get('active_ids') or []
        data_to_return = {
            'user_ids': [
                [6, 0, []]
            ]
        }
        non_ad_authed_users = [
            {'user_id': user.id, 'user_login': user.login}
            for user in user_model.browse(user_ids)
            if not user.ldap_authenticated
        ]
        if not non_ad_authed_users:
            raise osv.except_osv(_('Warning!'), _(
                "Cannot change password for Trust managed account. "
                "Please contact IT to change your password."
            ))
        for user in non_ad_authed_users:
            data_to_return['user_ids'].append([0, 0, user])
        return data_to_return
