from openerp.osv import orm
import logging

_logger = logging.getLogger(__name__)


class t4_ui_location(orm.Model):

    _name = 't4.clinical.location'
    _inherit = 't4.clinical.location'

    def search(self, cr, uid, domain, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('t4_open_form'):
            group_pool = self.pool.get('res.groups')
            group_ids = group_pool.search(cr, uid, [('users', 'in', [uid])], context=context)
            groups = group_pool.read(cr, uid, group_ids, ['name'], context=context)
            group_names = [g.get('name') for g in groups]
            if 'T4 Clinical Ward Manager Group' in group_names:
                for filter in domain:
                    if filter[0] == 'parent_id' and filter[1] == 'in':
                        types = self.read(cr, uid, filter[2], ['type'])
                        if types[0].get('type') == 'pos':
                            user_pool = self.pool.get('res.users')
                            user = user_pool.browse(cr, uid, uid, context=context)
                            location_ids = [l.id for l in user.location_ids]
                            domain += [('id', 'in', location_ids)]
        return super(t4_ui_location, self).search(cr, uid, domain, offset=offset, limit=limit, order=order, context=context, count=count)