from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import datetime as dt, timedelta as td
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID


class cancel_notifications_wizard(osv.TransientModel):

    _name = 't4.clinical.cancel_notifications'
    _columns = {
        'date_limit': fields.datetime('Cancel Until', required=True)
    }
    _defaults = {
        'date_limit': (dt.now() + td(days=-1)).strftime(DTF)
    }

    def submit(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)

        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        user_locations = [l.id for l in user.location_ids]
        activity_pool = self.pool['t4.activity']
        domain = [
            ('date_deadline', '<=', data.date_limit),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', 'ilike', '%notification%'),
            ('location_id.parent_id', 'in', user_locations)
        ]
        notification_ids = activity_pool.search(cr, SUPERUSER_ID, domain, context=context)

        [activity_pool.cancel(cr, SUPERUSER_ID, n, context=context) for n in notification_ids]

        cancel_reason_id = self.pool['t4.cancel.reason'].search(cr, uid, [('name', '=', 'Cancelled by Ward Manager')], context=context)

        activity_pool.write(cr, SUPERUSER_ID, notification_ids, {'terminate_uid': uid, 'cancel_reason_id': cancel_reason_id[0]}, context=context)

        return {'type': 'ir.actions.act_window_close'}