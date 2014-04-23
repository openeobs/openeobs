from openerp.osv import orm
import logging

_logger = logging.getLogger(__name__)


class t4_clinical_api(orm.AbstractModel):
    _name = 't4.clinical.api'
    _inherit = 't4.clinical.api'

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
        return activity_pool.cancel(cr, uid, activity_id, context=context) if activity_ids else False

    # def submit(self, cr, uid, activity_id, data, context=None):