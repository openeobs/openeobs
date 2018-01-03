from openerp.tests.common import TransactionCase
from openerp.osv.osv import except_osv
from openerp.exceptions import AccessDenied
from openerp.addons.nh_eobs_ldap.models.web_main import MainSession
import mock


class TestChangePassword(TransactionCase):
    """
    Test the /web/session/change_password JSON endpoint
    """

    def test_password_not_set(self):
        """
        Test that if the password is not set then an error dictionary is
        returned
        """
        request = mock.MagicMock()
        result = MainSession._change_password(
            request,
            (
                {
                    'name': 'old_pwd',
                    'value': 'admin'
                 },
                {
                    'name': 'new_password',
                    'value': 'admin'
                },
                {
                    'name': 'confirm_pwd',
                    'value': ''
                }
            )
        )
        self.assertEqual(
            result.get('error'),
            'You cannot leave any password empty.'
        )

    def test_passwords_dont_match(self):
        """
        Test that if the new password and the confirm password don't match
        then an error dictionary is returned
        """
        request = mock.MagicMock()
        result = MainSession._change_password(
            request,
            (
                {
                    'name': 'old_pwd',
                    'value': 'admin'
                },
                {
                    'name': 'new_password',
                    'value': 'foo'
                },
                {
                    'name': 'confirm_pwd',
                    'value': 'bar'
                }
            )
        )
        self.assertEqual(
            result.get('error'),
            'The new password and its confirmation must be identical.'
        )

    def test_old_password_wrong(self):
        """
        Test that if the old password provided is wrong then an error
        dictionary is returned
        """
        request = mock.MagicMock()
        request.session.model('res.users').change_password.side_effect = \
            AccessDenied()
        result = MainSession._change_password(
            request,
            (
                {
                    'name': 'old_pwd',
                    'value': 'not correct'
                },
                {
                    'name': 'new_password',
                    'value': 'foo'
                },
                {
                    'name': 'confirm_pwd',
                    'value': 'foo'
                }
            )
        )
        self.assertEqual(
            result.get('error'),
            'The old password you provided is incorrect, '
            'your password was not changed.'
        )

    def test_ad_authed_account(self):
        """
        Test that if the account is authenticated by Active Directory that an
        error dictionary is returned
        """
        error_msg = "Cannot change password for Trust managed account. " \
                    "Please contact IT to change your password."
        request = mock.MagicMock()
        request.session.model('res.users').change_password.side_effect = \
            except_osv('Warning!', error_msg)
        result = MainSession._change_password(
            request,
            (
                {
                    'name': 'old_pwd',
                    'value': 'admin'
                },
                {
                    'name': 'new_password',
                    'value': 'foo'
                },
                {
                    'name': 'confirm_pwd',
                    'value': 'foo'
                }
            )
        )
        self.assertEqual(
            result.get('error'),
            error_msg
        )

    def test_change_password(self):
        """
        Test that can change password successfully
        """
        request = mock.MagicMock()
        request.session.model('res.users').change_password.return_value = True
        result = MainSession._change_password(
            request,
            (
                {
                    'name': 'old_pwd',
                    'value': 'admin'
                },
                {
                    'name': 'new_password',
                    'value': 'foo'
                },
                {
                    'name': 'confirm_pwd',
                    'value': 'foo'
                }
            )
        )
        self.assertEqual(
            result,
            {'new_password': 'foo'}
        )
