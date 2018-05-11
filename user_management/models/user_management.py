import copy

from openerp import SUPERUSER_ID
from openerp.osv import orm, fields, osv


class NhClinicalUserManagement(orm.Model):
    """
    SQL View that shows the users related to clinical roles and allows
    to edit their roles and location responsibilities.
    """
    _name = "nh.clinical.user.management"
    _inherits = {
        'res.users': 'user_id'
    }
    _auto = False
    _table = "nh_clinical_user_management"
    _ward_ids_not_editable = ['Nurse', 'HCA']

    def _get_ward_ids(self, cr, uid, ids, field, args, context=None):
        """
        Function field to return list of ward location ids for each user.

        :param cr: Odoo Cursor
        :param uid: User carrying out action
        :param ids: IDs of records to look up
        :param field: Field function attached to
        :param args: Arguments for function
        :param context: Odoo context
        :return: map of user IDs to ward location IDs
        :rtype: dict
        """
        res = {}
        for user in self.browse(cr, uid, ids, context=context):
            res[user.id] = [
                loc.id for loc in user.location_ids if loc.usage == 'ward'
            ]
        return res

    def _get_categories(self, cr, uid, ids, field, args, context=None):
        """
        Function field to return list of category IDs for each user.

        :param cr: Odoo cursor
        :param uid: User carrying out action
        :param ids: IDs to look up
        :param field: field attached to
        :param args: arguments for function
        :param context: Odoo context
        :return: mapping of user IDs to category IDs
        :rtype: dict
        """
        res = {}
        for user in self.browse(cr, uid, ids, context=context):
            res[user.id] = [cat.id for cat in user.partner_id.category_id]
        return res

    def _categories_search(self, cr, uid, obj, name, args, domain=None,
                           context=None):
        """
        Search function for category_ids field.

        :param cr: Odoo cursor
        :param uid: user carrying out action
        :param obj: expression from Odoo's ORM
        :param name: table name
        :param args: Arguments for
        :param domain: Search Domain
        :param context: Odoo Context
        :return: domain for conducting search
        """
        arg1, op, arg2 = args[0]
        arg2 = arg2 if isinstance(arg2, (list, tuple)) else [arg2]
        all_ids = self.search(cr, uid, [])
        value_map = self._get_categories(cr, uid, all_ids, 'category_ids',
                                         None, context=context)
        ids = [
            k for k, v in value_map.items() if set(v or []) & set(arg2 or [])
        ]
        return [('id', 'in', ids)]

    _columns = {
        'user_id': fields.many2one('res.users', 'User', required=1,
                                   ondelete='restrict'),
        'ward_ids': fields.function(
            _get_ward_ids, type='many2many', relation='nh.clinical.location',
            string='Ward Responsibility', domain=[['usage', '=', 'ward']]),
        'category_ids': fields.function(
            _get_categories, type='many2many', relation='res.partner.category',
            string='Roles', fnct_search=_categories_search)
    }

    def create(self, cr, uid, vals, context=None):
        """
        Redirects to the res.users :meth:`create<openerp.models.Model.create>`
        method.

        If ``ward_ids`` is provided, `responsibility allocation`
        is created and completed to assign the user to those wards.

        :returns: res.users id
        :rtype: int
        """
        user_pool = self.pool['res.users']
        alloc_pool = self.pool['nh.clinical.user.responsibility.allocation']
        activity_pool = self.pool['nh.activity']
        user_data = vals.copy()
        if vals.get('ward_ids'):
            user_data.pop('ward_ids', None)
        user_id = user_pool.create(cr, uid, user_data, context=context)

        if vals.get('ward_ids') and vals.get('ward_ids')[0][2]:
            locations = vals.get('ward_ids')
            user = self.browse(cr, uid, user_id, context=context)
            editable = any(
                [c.name not in self._ward_ids_not_editable
                 for c in user.category_id]
            )
            if not editable:
                raise osv.except_osv(
                    'Role Error!',
                    'This user cannot be assigned with ward responsibility!')
            activity_id = alloc_pool.create_activity(cr, uid, {}, {
                'responsible_user_id': user_id,
                'location_ids': locations}, context=context)
            activity_pool.complete(cr, uid, activity_id, context=context)
        return user_id

    def write(self, cr, uid, ids, vals, context=None):
        """
        Checks if the user is allowed to execute the action (needs to
        be related to an equal ranking role or greater as the users
        that are being edited) and then redirects to the res.users
        :meth:`write<openerp.models.Model.write>` method.

        If ``ward_ids`` is edited, a `responsibility allocation`
        is created and completed to assign the users to those wards.

        :returns: ``True``
        :rtype: bool
        """
        if uid == SUPERUSER_ID:
            return super(NhClinicalUserManagement, self)\
                .write(cr, uid, ids, vals, context=None)

        user_pool = self.pool['res.users']
        category_pool = self.pool['res.partner.category']
        alloc_pool = self.pool['nh.clinical.user.responsibility.allocation']
        activity_pool = self.pool['nh.activity']
        u = user_pool.browse(cr, uid, uid, context=context)
        category_ids = [c.id for c in u.category_id]
        child_ids = []
        for c in category_ids:
            child_ids += category_pool.get_child_of_ids(cr, uid, c,
                                                        context=context)
        for user in self.browse(cr, uid, ids, context=context):
            ucids = [c.id for c in user.category_id]
            if any([i for i in ucids if i not in child_ids]):
                raise osv.except_osv(
                    'Permission Error!',
                    'You are not allowed to edit this user!')
        user_data = vals.copy()
        if vals.get('ward_ids'):
            user_data.pop('ward_ids', None)
        res = user_pool.write(cr, uid, ids, user_data, context=context)

        if vals.get('ward_ids'):
            locations = vals.get('ward_ids')
            for user in self.browse(cr, uid, ids, context=context):
                editable = any(
                    [c.name not in self._ward_ids_not_editable
                     for c in user.category_id]
                )
                if not editable:
                    raise osv.except_osv(
                        'Role Error!',
                        'This user cannot be assigned with ward '
                        'responsibility!')
            for user_id in ids:
                activity_id = alloc_pool.create_activity(cr, uid, {}, {
                    'responsible_user_id': user_id,
                    'location_ids': locations}, context=context)
                activity_pool.complete(cr, uid, activity_id, context=context)
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
        Extension of Odoo's ``fields_view_get`` method that returns a
        description of the view in dictionary format. This extension is
        adding a domain limit on the form view ``category_id`` field so
        users can only select roles of the same ranking level or lower
        as the ones they are related to.

        :returns: view description
        :rtype: dict
        """
        ctx = context.copy()
        ctx['partner_category_display'] = 'short'
        res = super(NhClinicalUserManagement, self).fields_view_get(
            cr, uid, view_id, view_type, ctx, toolbar, submenu)

        if uid == SUPERUSER_ID:
            return res

        if view_type == 'form' and res['fields'].get('category_id'):
            user_pool = self.pool['res.users']
            category_pool = self.pool['res.partner.category']
            u = user_pool.browse(cr, uid, uid, context=ctx)
            category_ids = [c.id for c in u.category_id]
            child_ids = []
            for c in category_ids:
                child_ids += category_pool.get_child_of_ids(
                    cr, uid, c, context=ctx)
            res['fields']['category_id']['domain'] = [['id', 'in', child_ids]]
        return res

    def allocate_responsibility(self, cr, uid, ids, context=None):
        """
        Return Reponsibility Allocation wizard for user to frontend.

        :param cr: Odoo cursor
        :param uid: User carrying out action
        :param ids: Records IDs
        :param context: Odoo Context
        :return: Odoo ir.actions.act_window definition with user ID set in
        context
        :rtype: dict
        """
        user = self.browse(cr, uid, ids[0], context=context)
        new_context = copy.deepcopy(context.copy())
        new_context.update({'default_user_id': user.id})
        view = {
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.responsibility.allocation',
            'name': 'Location Responsibility Allocation',
            'view_mode': 'form',
            'view_type': 'tree,form',
            'target': 'new',
            'context': new_context,
        }
        return view

    def deactivate(self, cr, uid, ids, context=None):
        """
        Writes ``False`` on the users ``active`` field.

        :returns: ``True``
        :rtype: bool
        """
        user_pool = self.pool['res.users']
        if uid in ids:
            raise osv.except_osv('Error!', 'You cannot deactivate yourself!')
        return user_pool.write(cr, uid, ids, {'active': False},
                               context=context)

    def activate(self, cr, uid, ids, context=None):
        """
        Writes ``True`` on the users ``active`` field.

        :returns: ``True``
        :rtype: bool
        """
        user_pool = self.pool['res.users']
        return user_pool.write(cr, uid, ids, {'active': True}, context=context)

    def init(self, cr):
        cr.execute("""
            drop view if exists %s;
            create or replace view %s as (
                select
                    users.id as id,
                    users.id as user_id
                from res_users users
                inner join res_partner partner on partner.id = users.partner_id
            )
        """ % (self._table, self._table))
