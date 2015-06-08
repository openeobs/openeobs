# -*- coding: utf-8 -*-
__author__ = 'lorenzo'
import logging
from openerp.osv import orm, fields, osv

_logger = logging.getLogger(__name__)


class nh_eobs_mobile_nfc(orm.Model):
    """Storing user ID and card's PIN related to that user (for NFC authentication purpose)."""
    _name = 'res.users'
    _inherit = 'res.users'

    _columns = {
        'card_pin': fields.char('Card PIN')
    }

    def get_user_id_from_card_pin(self, cr, uid, card_pin, context=None):
        """Return the user ID related to the card PIN passed as argument."""
        user_id = self.search(cr, uid, [('card_pin', '=', card_pin)], context=context)
        if not user_id:
            _logger.debug('Cannot find a user ID related to the card PIN passed.')
            return False
        else:
            if len(user_id) > 1:
                raise osv.except_osv('Error!', "More than one user ID found!")
            elif len(user_id) == 1:
                _logger.debug('User ID found ! User ID {}'.format(user_id))
                return user_id[0]

    def get_user_login_from_user_id(self, cr, uid, user_id, context=None):
        """Return the user name related to the user ID passed as argument."""
        user_login = self.search_read(cr, uid, domain=[('id', '=', user_id)], fields=['login'], context=context)
        if not user_login:
            _logger.debug('Cannot find a user related to the user ID passed.')
            return False
        else:
            if len(user_login) > 1:
                raise osv.except_osv('Error!', "More than one user found!")
            elif len(user_login) == 1:
                _logger.debug('User found ! User {}'.format(user_login))
                return user_login[0]['login']