from openerp.osv import orm, osv
from openerp.tools.translate import _


class EOBSChangePasswordWizard(orm.TransientModel):
    """
    Change password wizard displayed in the more menu on user.management
    screen
    """
    _name = "change.password.wizard"
    _inherit = "change.password.wizard"

    def default_get(self, cr, uid, fields, context=None):
        """
        Override the default get for password change so that user's who have
        been set up via AD can't have their passwords changed

        :param cr: Odoo cursor
        :param uid: user doing the action
        :param fields: fields to get
        :param context: Odoo context
        :return: list of mappings of user id and user name for users not added
        via AD
        :raises: if no non-AD users are selected
        """
        if context is None:
            context = {}
        user_model = self.pool['res.users']
        user_ids = context.get('active_ids') or []
        data_to_return = {
            'user_ids': [
                [6, 0, []]
            ]
        }
        non_ad_authed_users = [
            {'user_id': user.id, 'user_login': user.login}
            for user in user_model.browse(cr, uid, user_ids, context=context)
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
