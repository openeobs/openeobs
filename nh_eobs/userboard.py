from openerp.osv import orm, fields, osv


class nh_change_password_wizard(osv.TransientModel):
    _name = "change.password.wizard"
    _inherit = "change.password.wizard"

    def _default_user_ids(self, cr, uid, context=None):
        if context is None:
            context = {}
        user_model = self.pool['res.users']
        user_ids = context.get('active_ids') or []
        return [
            (0, 0, {'user_id': user.id, 'user_login': user.login})
            for user in user_model.browse(cr, uid, user_ids, context=context)
        ]

    _defaults = {
        'user_ids': _default_user_ids,
    }

class nh_clinical_userboard(orm.Model):
    _name = "nh.clinical.userboard"
    _inherits = {'res.users': 'user_id'}
    _auto = False
    _table = "nh_clinical_userboard"
    _columns = {
        'user_id': fields.many2one('res.users', 'User', required=1, ondelete='restrict'),
        'name': fields.char('Name', size=64, required=True),
        'login': fields.char('Login', size=64, required=True),
        'password': fields.char('Password', size=64),
        'hca': fields.boolean('HCA'),
        'nurse': fields.boolean('Nurse'),
        'ward_manager': fields.boolean('Ward Manager'),
        'doctor': fields.boolean('Doctor')
    }

    def responsibility_allocation(self, cr, uid, ids, context=None):
        user = self.browse(cr, uid, ids[0], context=context)
        context.update({'default_user_id': user.id})
        view = {
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.responsibility.allocation',
            'name': 'Location Responsibility Allocation',
            'view_mode': 'form',
            'view_type': 'tree,form',
            'target': 'new',
            'context': context,
        }
        return view

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        hca = vals.get('hca')
        nurse = vals.get('nurse')
        ward_manager = vals.get('ward_manager')
        doctor = vals.get('doctor')
        check_groups = any([hca, nurse, ward_manager, doctor])
        if not check_groups:
            raise osv.except_osv('Error!', 'At least one role must be selected.')
        user_pool = self.pool['res.users']
        groups_pool = self.pool['res.groups']
        user_write_vals = {}
        groups = []
        user_write_vals.update({'name': vals['name']})
        user_write_vals.update({'login': vals['login'], 'password': vals['login']})
        if hca:
            groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical HCA Group')], context=context)
        if nurse:
            groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical Nurse Group')], context=context)
        if ward_manager:
            groups += groups_pool.search(cr, uid, [('name', 'in', ['NH Clinical Ward Manager Group', 'Contact Creation'])], context=context)
        if doctor:
            groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical Doctor Group')], context=context)
        groups += groups_pool.search(cr, uid, [('name', '=', 'Employee')], context=context)
        user_write_vals.update({'groups_id': [[6, False, groups]]})
        return user_pool.create(cr, uid, user_write_vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        for user in self.browse(cr, uid, ids, context=context):
            hca = vals.get('hca') if isinstance(vals.get('hca'), bool) else user.hca
            nurse = vals.get('nurse') if isinstance(vals.get('nurse'), bool) else user.nurse
            ward_manager = vals.get('ward_manager') if isinstance(vals.get('ward_manager'), bool) else user.ward_manager
            doctor = vals.get('doctor') if isinstance(vals.get('doctor'), bool) else user.doctor
            check_groups = any([hca, nurse, ward_manager, doctor])
            if not check_groups:
                raise osv.except_osv('Error!', 'At least one role must be selected.')
            user_pool = self.pool['res.users']
            groups_pool = self.pool['res.groups']
            user_write_vals = {}
            groups = []
            if vals.get('name'):
                user_write_vals.update({'name': vals['name']})
            if vals.get('login'):
                user_write_vals.update({'login': vals['login']})
            if hca:
                groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical HCA Group')], context=context)
            if nurse:
                groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical Nurse Group')], context=context)
            if ward_manager:
                groups += groups_pool.search(cr, uid, [('name', 'in', ['NH Clinical Ward Manager Group', 'Contact Creation'])], context=context)
            if doctor:
                groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical Doctor Group')], context=context)
            groups += groups_pool.search(cr, uid, [('name', '=', 'Employee')], context=context)
            user_write_vals.update({'groups_id': [[6, False, groups]]})
            user_pool.write(cr, uid, [user.user_id.id], user_write_vals, context=context)
        return True

    def init(self, cr):
        cr.execute("""
            drop view if exists %s;
            create or replace view %s as (
                with user_groups as (
                    select
                        users.id as id,
                        array_agg(rgroup.name) as groups
                    from res_users users
                    inner join res_groups_users_rel gur on gur.uid = users.id
                    inner join res_groups rgroup on rgroup.id = gur.gid
                    group by users.id
                )
                select
                    users.id as id,
                    users.id as user_id,
                    partner.name as name,
                    users.login as login,
                    users.password as password,
                    case
                        when ug.groups @> '{"NH Clinical HCA Group"}' then true
                        else false
                    end as hca,
                    case
                        when ug.groups @> '{"NH Clinical Nurse Group"}' then true
                        else false
                    end as nurse,
                    case
                        when ug.groups @> '{"NH Clinical Ward Manager Group"}' then true
                        else false
                    end as ward_manager,
                    case
                        when ug.groups @> '{"NH Clinical Doctor Group"}' then true
                        else false
                    end as doctor
                from res_users users
                inner join res_partner partner on partner.id = users.partner_id
                inner join user_groups ug on ug.id = users.id
                where ug.groups @> '{"NH Clinical HCA Group"}' or ug.groups @> '{"NH Clinical Nurse Group"}' or ug.groups @> '{"NH Clinical Ward Manager Group"}' or ug.groups @> '{"NH Clinical Doctor Group"}'
            )
        """ % (self._table, self._table))


class nh_clinical_admin_userboard(orm.Model):
    _name = "nh.clinical.admin.userboard"
    _inherits = {'res.users': 'user_id'}
    _auto = False
    _table = "nh_clinical_admin_userboard"
    _columns = {
        'user_id': fields.many2one('res.users', 'User', required=1, ondelete='restrict'),
        'name': fields.char('Name', size=64, required=True),
        'login': fields.char('Login', size=64, required=True),
        'password': fields.char('Password', size=64),
        'active': fields.boolean('Active'),
        'hca': fields.boolean('HCA'),
        'nurse': fields.boolean('Nurse'),
        'ward_manager': fields.boolean('Ward Manager'),
        'doctor': fields.boolean('Doctor'),
        'kiosk': fields.boolean('eObs Kiosk'),
        'admin': fields.boolean('Open eObs Administrator')
    }

    def responsibility_allocation(self, cr, uid, ids, context=None):
        user = self.browse(cr, uid, ids[0], context=context)
        context.update({'default_user_id': user.id})
        view = {
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.responsibility.allocation',
            'name': 'Location Responsibility Allocation',
            'view_mode': 'form',
            'view_type': 'tree,form',
            'target': 'new',
            'context': context,
        }
        return view

    def deactivate(self, cr, uid, ids, context=None):
        user_pool = self.pool['res.users']
        if uid in ids:
            raise osv.except_osv('Error!', 'You cannot deactivate yourself!')
        return user_pool.write(cr, uid, ids, {'active': False}, context=context)

    def activate(self, cr, uid, ids, context=None):
        user_pool = self.pool['res.users']
        return user_pool.write(cr, uid, ids, {'active': True}, context=context)

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        hca = vals.get('hca')
        nurse = vals.get('nurse')
        ward_manager = vals.get('ward_manager')
        doctor = vals.get('doctor')
        admin = vals.get('admin')
        kiosk = vals.get('kiosk')
        check_groups = any([hca, nurse, ward_manager, doctor, admin, kiosk])
        if not check_groups:
            raise osv.except_osv('Error!', 'At least one role must be selected.')
        user_pool = self.pool['res.users']
        groups_pool = self.pool['res.groups']
        user_write_vals = {}
        groups = []
        user_write_vals.update({'name': vals['name']})
        user_write_vals.update({'login': vals['login'], 'password': vals['login']})
        if hca:
            groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical HCA Group')], context=context)
        if nurse:
            groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical Nurse Group')], context=context)
        if ward_manager:
            groups += groups_pool.search(cr, uid, [('name', 'in', ['NH Clinical Ward Manager Group', 'Contact Creation'])], context=context)
        if doctor:
            groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical Doctor Group')], context=context)
        if admin:
            groups += groups_pool.search(cr, uid, [('name', 'in', ['NH Clinical Admin Group', 'Contact Creation'])], context=context)
        if kiosk:
            groups += groups_pool.search(cr, uid, [('name', 'in', ['NH Clinical Kiosk Group'])], context=context)
        groups += groups_pool.search(cr, uid, [('name', '=', 'Employee')], context=context)
        user_write_vals.update({'groups_id': [[6, False, groups]]})
        return user_pool.create(cr, uid, user_write_vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        for user in self.browse(cr, uid, ids, context=context):
            hca = vals.get('hca') if isinstance(vals.get('hca'), bool) else user.hca
            nurse = vals.get('nurse') if isinstance(vals.get('nurse'), bool) else user.nurse
            ward_manager = vals.get('ward_manager') if isinstance(vals.get('ward_manager'), bool) else user.ward_manager
            doctor = vals.get('doctor') if isinstance(vals.get('doctor'), bool) else user.doctor
            admin = vals.get('admin') if isinstance(vals.get('admin'), bool) else user.admin
            kiosk = vals.get('kiosk') if isinstance(vals.get('kiosk'), bool) else user.kiosk
            check_groups = any([hca, nurse, ward_manager, doctor, admin])
            if not check_groups:
                raise osv.except_osv('Error!', 'At least one role must be selected.')
            user_pool = self.pool['res.users']
            groups_pool = self.pool['res.groups']
            user_write_vals = {}
            groups = []
            if vals.get('name'):
                user_write_vals.update({'name': vals['name']})
            if vals.get('login'):
                user_write_vals.update({'login': vals['login']})
            if hca:
                groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical HCA Group')], context=context)
            if nurse:
                groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical Nurse Group')], context=context)
            if ward_manager:
                groups += groups_pool.search(cr, uid, [('name', 'in', ['NH Clinical Ward Manager Group', 'Contact Creation'])], context=context)
            if doctor:
                groups += groups_pool.search(cr, uid, [('name', '=', 'NH Clinical Doctor Group')], context=context)
            if admin:
                groups += groups_pool.search(cr, uid, [('name', 'in', ['NH Clinical Admin Group', 'Contact Creation'])], context=context)
            if kiosk:
                groups += groups_pool.search(cr, uid, [('name', 'in', ['NH Clinical Kiosk Group'])], context=context)
            groups += groups_pool.search(cr, uid, [('name', '=', 'Employee')], context=context)
            user_write_vals.update({'groups_id': [[6, False, groups]]})
            user_pool.write(cr, uid, [user.user_id.id], user_write_vals, context=context)
        return True

    def init(self, cr):
        cr.execute("""
            drop view if exists %s;
            create or replace view %s as (
                with user_groups as (
                    select
                        users.id as id,
                        array_agg(rgroup.name) as groups
                    from res_users users
                    inner join res_groups_users_rel gur on gur.uid = users.id
                    inner join res_groups rgroup on rgroup.id = gur.gid
                    group by users.id
                )
                select
                    users.id as id,
                    users.id as user_id,
                    users.active as active,
                    partner.name as name,
                    users.login as login,
                    users.password as password,
                    case
                        when ug.groups @> '{"NH Clinical HCA Group"}' then true
                        else false
                    end as hca,
                    case
                        when ug.groups @> '{"NH Clinical Nurse Group"}' then true
                        else false
                    end as nurse,
                    case
                        when ug.groups @> '{"NH Clinical Ward Manager Group"}' then true
                        else false
                    end as ward_manager,
                    case
                        when ug.groups @> '{"NH Clinical Doctor Group"}' then true
                        else false
                    end as doctor,
                    case
                        when ug.groups @> '{"NH Clinical Kiosk Group"}' then true
                        else false
                    end as kiosk,
                    case
                        when ug.groups @> '{"NH Clinical Admin Group"}' then true
                        else false
                    end as admin
                from res_users users
                inner join res_partner partner on partner.id = users.partner_id
                inner join user_groups ug on ug.id = users.id
                where users.id != 1 and (ug.groups @> '{"NH Clinical HCA Group"}' or ug.groups @> '{"NH Clinical Nurse Group"}' or ug.groups @> '{"NH Clinical Ward Manager Group"}' or ug.groups @> '{"NH Clinical Doctor Group"}' or ug.groups @> '{"NH Clinical Kiosk Group"}' or ug.groups @> '{"NH Clinical Admin Group"}')
            )
        """ % (self._table, self._table))