# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.osv import osv, fields


class responsibility_allocation_wizard(osv.TransientModel):

    _name = 'nh.clinical.responsibility.allocation'
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'location_ids': fields.many2many('nh.clinical.location',
                                         'allocation_location_rel',
                                         'allocation_id', 'location_id',
                                         string='Locations'),
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

    def get_location_list(self, cr, uid, location_id, context=None):
        location = self.pool['nh.clinical.location'].browse(cr, uid,
                                                            location_id,
                                                            context=context)
        res = [location.id]
        for child in location.child_ids:
            res += self.get_location_list(cr, uid, child.id, context=context)
        return res

    def submit(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context=context)
        allocation_pool = self.pool[
            'nh.clinical.user.responsibility.allocation'
        ]
        activity_pool = self.pool['nh.activity']

        locations = [loc.id for loc in data.location_ids]

        activity_id = allocation_pool.create_activity(cr, uid, {}, {
            'responsible_user_id': data.user_id.id,
            'location_ids': [[6, False, locations]]}, context=context)
        activity_pool.complete(cr, uid, activity_id, context=context)

        return {'type': 'ir.actions.act_window_close'}
