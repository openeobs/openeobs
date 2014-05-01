from openerp.osv import orm, osv
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class t4_clinical_api(orm.AbstractModel):
    _name = 't4.clinical.api'
    _inherit = 't4.clinical.api'

    # # # # # # # #
    #  ACTIVITIES #
    # # # # # # # #

    def getActivities(self, cr, uid, ids, context=None):
        domain = [('id', 'in', ids)] if ids else []
        activity_pool = self.pool['t4.clinical.activity']
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        activity_values = activity_pool.read(cr, uid, activity_ids, [], context=context)
        return activity_values

    def cancel(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            raise osv.except_osv(_('Error!'), 'Activity ID not found: %s' % activity_id)
        return activity_pool.cancel(cr, uid, activity_id, context=context)

    def submit(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            raise osv.except_osv(_('Error!'), 'Activity ID not found: %s' % activity_id)
        return activity_pool.submit(cr, uid, activity_id, data, context=context)

    def unassign(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            raise osv.except_osv(_('Error!'), 'Activity ID not found: %s' % activity_id)
        return activity_pool.unassign(cr, uid, activity_id, context=context)

    def assign(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        user_pool = self.pool['res.users']
        user_id = uid
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            raise osv.except_osv(_('Error!'), 'Activity ID not found: %s' % activity_id)
        if data.get('user_id'):
            user_id = data['user_id']
            domain = [('id', '=', user_id)]
            user_ids = user_pool.search(cr, uid, domain, context=context)
            if not user_ids:
                raise osv.except_osv(_('Error!'), 'User ID not found: %s' % user_id)
        return activity_pool.assign(cr, uid, activity_id, user_id, context=context)

    def complete(self, cr, uid, activity_id, data, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        domain = [('id', '=', activity_id)]
        activity_ids = activity_pool.search(cr, uid, domain, context=context)
        if not activity_ids:
            raise osv.except_osv(_('Error!'), 'Activity ID not found: %s' % activity_id)
        return activity_pool.complete(cr, uid, activity_id, data, context=context)

    # # # # # # #
    #  PATIENTS #
    # # # # # # #
