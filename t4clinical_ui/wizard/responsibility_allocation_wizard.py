from openerp.osv import osv, fields


class responsibility_allocation_wizard(osv.TransientModel):

    _name = 't4.clinical.responsibility.allocation'
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'location_ids': fields.many2many('t4.clinical.location',
                                         'allocation_location_rel', 'allocation_id', 'location_id', string='Locations'),
        'clear_locations': fields.boolean('Clear All Locations')
    }

    def onchange_user_id(self, cr, uid, ids, user_id, context=None):
        user_pool = self.pool['res.users']
        if not user_id:
            return {}
        user = user_pool.browse(cr, uid, user_id, context=context)
        location_ids = [l.id for l in user.location_ids]
        return {'value': {'location_ids': [[6, False, location_ids]]}}

    def onchange_clear(self, cr, uid, ids, clear, context=None):
        value = {
            'location_ids': [[6, False, []]]
        }
        if clear:
            value['clear_locations'] = False
        return {'value': value}

    def submit(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context=context)

        vals = {'location_ids': [[6, False, [l.id for l in data.location_ids]]]}

        user_pool = self.pool['res.users']
        user_pool.write(cr, uid, data.user_id.id, vals, context=context)

        return {'type': 'ir.actions.act_window_close'}