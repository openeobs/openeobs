from openerp import http
from openerp.http import request
from openerp.osv.osv import except_osv
from openerp.addons.web.controllers.main import Session
import openerp.modules as addons
from openerp.tools.translate import _
import operator


class MainSession(Session):
    """
    A class to change the nh_eobs_api.controllers.routes method
    """

    @staticmethod
    def _change_password(request, fields):
        """
        Actual implementation behind the change_password call. This is a
        reimplementation of the method as the original method silences
        exceptions so we can't see if the exception is from a password
        issue or the res.user check for the ldap_authenticated flag.

        :param fields: submitted fields
        :return: the new password or an error
        """
        old_password, new_password, confirm_password = \
            operator.itemgetter('old_pwd', 'new_password', 'confirm_pwd')(
                dict(map(operator.itemgetter('name', 'value'), fields)))
        password_set = old_password.strip() \
            and new_password.strip() \
            and confirm_password.strip()
        if not password_set:
            return {'error': _('You cannot leave any password empty.'),
                    'title': _('Change Password')}
        if new_password != confirm_password:
            return {
                'error': _('The new password and its confirmation '
                           'must be identical.'),
                'title': _('Change Password')
            }
        try:
            users_model = request.session.model('res.users')
            user = users_model.browse(request.uid)
            if user.change_password(old_password, new_password):
                return {'new_password': new_password}
        except Exception as e:
            if isinstance(e, except_osv) \
                    and 'Trust managed account' in e.value:
                        return {'error': _(e.value),
                                'title': _(e.name)}
            return {'error': _(
                'The old password you provided is incorrect, '
                'your password was not changed.'),
                'title': _('Change Password')}

    @http.route('/web/session/change_password', type='json', auth="user")
    def change_password(self, fields):
        """
        Override the change_password endpoint of the JSON-RPC API used by the
        Odoo frontend

        :param fields: submitted fields
        :return: the new password or an error
        """
        return self._change_password(request, fields)

    def __init__(self):
        loaded = addons.module.loaded
        if 'nh_eobs_ldap' in loaded:
            Session.change_password = self.change_password
        super(MainSession, self).__init__()
