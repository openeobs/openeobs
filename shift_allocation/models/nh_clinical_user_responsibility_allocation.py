# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv


class NhClinicalUserResponsibilityAllocation(orm.Model):
    """
    This activity is meant to audit the allocation of responsibility of
    users to locations.
    """
    _name = 'nh.clinical.user.responsibility.allocation'
    _inherit = ['nh.activity.data']
    _description = "Assign User Locations Responsibility"

    _columns = {
        'responsible_user_id': fields.many2one('res.users', 'User'),
        'location_ids': fields.many2many(
            'nh.clinical.location', 'user_allocation_location_rel',
            'user_allocation_id', 'location_id', string='Locations'),
    }

    _order = 'id desc'

    def complete(self, cr, uid, activity_id, context=None):
        """
        Calls :meth:`complete<activity.nh_activity.complete>` and then
        sets updates the ``location_ids`` list for the user.

        If the user is in the `HCA` or `Nurse` user groups the method
        will automatically assign every location child of the ones
        provided on top of them. If the user is not within those user
        groups, that will also be done when the location is not of
        `ward` usage.

        :returns: ``True``
        :rtype: bool
        """

        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        if not activity.data_ref:
            raise osv.except_osv(
                'Error!', "Can't complete the activity without data!")
        if not activity.data_ref.responsible_user_id:
            raise osv.except_osv(
                'Error!',
                "Can't complete the activity without selecting a responsible "
                "user for the selected locations.")
        res = super(NhClinicalUserResponsibilityAllocation, self).complete(
            cr, uid, activity_id, context=context)

        locations = self.get_allocation_locations(cr, uid, activity.data_ref,
                                                  context=context)
        values = {'location_ids': [[6, False, list(set(locations))]]}

        user_pool = self.pool['res.users']
        user_pool.write(
            cr, uid, activity.data_ref.responsible_user_id.id, values,
            context=context)
        return res

    def get_allocation_locations(self, cr, uid, allocation_obj, context=None):
        """
        Get a list locations to allocate the user to.

        :param cr: Cursor
        :param uid: User ID to perform operation with
        :param allocation_obj: The activity data ref from a user responsibility
            allocation
        :param context: Odoo context
        :return: list of location ids
        """
        location_pool = self.pool.get('nh.clinical.location')
        locations = []
        if not any(
                [g.name in ['NH Clinical HCA Group', 'NH Clinical Nurse Group']
                 for g in allocation_obj.responsible_user_id.groups_id]
        ):
            for loc in allocation_obj.location_ids:
                if loc.usage == 'ward':
                    locations.append(loc.id)
                else:
                    locations += location_pool.search(
                        cr, uid, [['id', 'child_of', loc.id]], context=context)
        else:
            for loc in allocation_obj.location_ids:
                locations += location_pool.search(
                    cr, uid, [['id', 'child_of', loc.id]], context=context)
        return locations
