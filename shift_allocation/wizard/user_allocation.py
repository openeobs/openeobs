# -*- coding: utf-8 -*-
# Part of NHClinical. See LICENSE file for full copyright and licensing details
from openerp.osv import osv, fields
from openerp import api


def list_diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]


def list_intersect(a, b):
    b = set(b)
    return [aa for aa in a if aa in b]


class AllocationWizards(osv.AbstractModel):

    _name = 'nh.clinical.allocation'

    _columns = {
        'create_uid': fields.many2one(
            'res.users',
            'User Executing the Wizard'),
        'create_date': fields.datetime('Create Date')
    }

    def responsibility_allocation_activity(self, cr, uid, user_id,
                                           location_ids, context=None):
        """
        Create and complete a responsibility allocation activity for location
        :param location_ids: Ward ID
        :param context: A context
        :return: True
        """
        activity_pool = self.pool['nh.activity']
        responsibility_allocation_pool = self.pool[
            'nh.clinical.user.responsibility.allocation'
        ]
        activity_id = responsibility_allocation_pool.create_activity(
            cr, uid, {}, {
                'responsible_user_id': user_id,
                'location_ids': [[6, 0, location_ids]]
            }, context=context)
        activity_pool.complete(cr, uid, activity_id, context=context)
        return True

    def unfollow_patients_in_locations(self, cr, uid, location_ids,
                                       context=None):
        """
        Unfollow any patients in the locations currently being reallocated
        :param location_ids: List of location ids
        :param context: context for odoo
        :return: True
        """
        activity_pool = self.pool['nh.activity']
        patient_pool = self.pool['nh.clinical.patient']
        unfollow_pool = self.pool['nh.clinical.patient.unfollow']
        patient_ids = patient_pool.search(
            cr, uid, [['current_location_id', 'in', location_ids]],
            context=context)
        if patient_ids:
            unfollow_activity_id = unfollow_pool.create_activity(cr, uid, {}, {
                'patient_ids': [[6, 0, patient_ids]]}, context=context)
            activity_pool.complete(cr, uid, unfollow_activity_id,
                                   context=context)
        return True

    def complete(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        if not isinstance(ids, int):
            raise ValueError('Invalid ID passed to complete')
        allocating_pool = self.pool['nh.clinical.allocating']
        wizard = self.browse(cr, uid, ids, context=context)
        allocation = {u.id: [l.id for l in u.location_ids] for u in
                      wizard.user_ids}
        for allocating in allocating_pool.browse(
                cr, uid, [a.id for a in wizard.allocating_ids],
                context=context):
            if allocating.nurse_id:
                allocation[allocating.nurse_id.id].append(
                    allocating.location_id.id)
                if allocating.nurse_id.id == uid:
                    allocation[allocating.nurse_id.id].append(
                        wizard.ward_id.id)
            for hca in allocating.hca_ids:
                allocation[hca.id].append(allocating.location_id.id)
        for key, value in allocation.iteritems():
            self.responsibility_allocation_activity(cr, uid, key, value,
                                                    context=context)
        self._create_shift(cr, uid, wizard)
        return {'type': 'ir.actions.act_window_close'}

    def _create_shift(self, cr, uid, wizard):
        """
        Create a shift object based on the data in the wizard record.

        :param cr:
        :param uid:
        :param wizard:
        """
        nurses = wizard.user_ids.filter_nurses(wizard.user_ids)
        hcas = wizard.user_ids.filter_hcas(wizard.user_ids)

        shift_model = self.pool['nh.clinical.shift']
        shift_model.create(
            cr, uid, {
                'ward': wizard.ward_id.id,
                'nurses': [(6, 0, map(lambda e: e.id, nurses))],
                'hcas': [(6, 0, map(lambda e: e.id, hcas))]
            }
        )


class StaffAllocationWizard(osv.TransientModel):
    _name = 'nh.clinical.staff.allocation'
    _inherit = 'nh.clinical.allocation'
    _rec_name = 'create_uid'

    _stages = [['wards', 'My Ward'], ['review', 'De-allocate'],
               ['users', 'Roll Call'], ['allocation', 'Allocation']]

    _columns = {
        'stage': fields.selection(_stages, string='Stage'),
        'ward_id': fields.many2one('nh.clinical.location',
                                   string='Ward',
                                   domain=[['usage', '=', 'ward']]),
        'location_ids': fields.many2many('nh.clinical.location',
                                         'alloc_loc_rel', 'allocation_id',
                                         'location_id',
                                         string='Locations'),
        'user_ids': fields.many2many('res.users', 'alloc_user_rel',
                                     'allocation_id', 'user_id',
                                     string='Users',
                                     domain=[
                                         ['groups_id.name', 'in',
                                          ['NH Clinical HCA Group',
                                           'NH Clinical Nurse Group']]
                                     ]),
        'allocating_ids': fields.many2many('nh.clinical.allocating',
                                           'alloc_allocating_rel',
                                           'allocation_id',
                                           'allocating_id',
                                           string='Allocating Locations')
    }
    _defaults = {
        'stage': 'wards'
    }

    def submit_ward(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        if not isinstance(ids, int):
            raise ValueError('Invalid ID passed to submit_wards')
        wiz = self.browse(cr, uid, ids, context=context)
        ward_ids = [wiz.ward_id.id]
        location_pool = self.pool['nh.clinical.location']
        location_ids = location_pool.search(
            cr, uid, [['id', 'child_of', ward_ids]], context=context)
        self.write(cr, uid, ids,
                   {'stage': 'review', 'location_ids': [[6, 0, location_ids]]},
                   context=context)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': ids,
            'view_mode': 'form',
            'target': 'new',
        }

    def deallocate(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        if not isinstance(ids, int):
            raise ValueError('Invalid ID passed to deallocate')
        user_pool = self.pool['res.users']
        allocating_pool = self.pool['nh.clinical.allocating']
        wiz = self.browse(cr, uid, ids, context=context)
        location_ids = [location.id for location in wiz.location_ids]
        user_ids = user_pool.search(cr, uid, [
            ['groups_id.name', 'in',
             [
                 'NH Clinical HCA Group',
                 'NH Clinical Nurse Group',
                 'NH Clinical Shift Coordinator Group'
             ]],
            ['location_ids', 'in', location_ids]
        ], context=context)
        for location_id in location_ids:
            user_pool.write(cr, uid, user_ids,
                            {'location_ids': [[3, location_id]]},
                            context=context)
        self.responsibility_allocation_activity(cr, uid, uid, [wiz.ward_id.id],
                                                context=context)
        self.unfollow_patients_in_locations(cr, uid, location_ids,
                                            context=context)
        allocating_ids = []
        for location in wiz.location_ids:
            if location.usage == 'bed':
                allocating_ids.append(
                    allocating_pool.create(cr, uid, {
                        'location_id': location.id}, context=context))
        self.write(cr, uid, ids,
                   {
                       'allocating_ids': [[6, 0, allocating_ids]],
                       'stage': 'users'
                   }, context=context)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': ids,
            'view_mode': 'form',
            'target': 'new',
        }

    def submit_users(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        if not isinstance(ids, int):
            raise ValueError('Invalid ID passed to submit_users')
        self.write(cr, uid, ids, {'stage': 'allocation'}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Shift Change',
            'res_model': 'nh.clinical.staff.allocation',
            'res_id': ids,
            'view_mode': 'form',
            'target': 'new',
        }


class StaffReallocationWizard(osv.TransientModel):
    _name = 'nh.clinical.staff.reallocation'
    _inherit = 'nh.clinical.allocation'
    _rec_name = 'create_uid'

    _nursing_groups = ['NH Clinical Nurse Group', 'NH Clinical HCA Group']
    _stages = [['users', 'Current Roll Call'], ['allocation', 'Allocation']]

    def _get_default_ward(self, cr, uid, context=None):
        location_pool = self.pool['nh.clinical.location']
        ward_ids = location_pool.search(
            cr, uid, [['usage', '=', 'ward'], ['user_ids', 'in', [uid]]],
            context=context)
        if not ward_ids:
            raise osv.except_osv(
                'Shift Management Error!',
                'You must be in charge of a ward to do this task!')
        return ward_ids[0]

    def get_users_for_locations(self, cr, uid, location_ids, context=None):
        user_pool = self.pool['res.users']
        return user_pool.search(
            cr, uid, [['groups_id.name', 'in', self._nursing_groups],
                      ['location_ids', 'in', location_ids]], context=context)

    @api.model
    def _get_default_users(self):
        ward_id = self._get_default_ward()
        shift_model = self.env['nh.clinical.shift']
        latest_shift_for_ward = shift_model.get_latest_shift_for_ward(ward_id)
        if not latest_shift_for_ward:
            return
        users_on_shift = \
            latest_shift_for_ward.nurses + latest_shift_for_ward.hcas
        return users_on_shift

    def _get_default_locations(self, cr, uid, context=None):
        location_pool = self.pool['nh.clinical.location']
        ward_id = self._get_default_ward(cr, uid, context=context)
        location_ids = location_pool.search(cr, uid,
                                            [['id', 'child_of', ward_id]],
                                            context=context)
        return location_ids

    def _get_default_allocatings(self, cr, uid, context=None):
        location_pool = self.pool['nh.clinical.location']
        allocating_pool = self.pool['nh.clinical.allocating']
        location_ids = self._get_default_locations(cr, uid, context=context)
        locations = location_pool.browse(cr, uid, location_ids,
                                         context=context)
        allocating_ids = []
        for l in locations:
            if l.usage != 'bed':
                continue
            nurse_id = False
            hca_ids = []
            for u in l.user_ids:
                groups = [g.name for g in u.groups_id]
                if 'NH Clinical Nurse Group' in groups and \
                        'NH Clinical Shift Coordinator Group' not in groups:
                    nurse_id = u.id
                if 'NH Clinical HCA Group' in groups:
                    hca_ids.append(u.id)
                if 'NH Clinical Shift Coordinator Group' in groups \
                        and not nurse_id:
                            nurse_id = u.id
            allocating_ids.append(allocating_pool.create(cr, uid, {
                'location_id': l.id,
                'nurse_id': nurse_id,
                'hca_ids': [[6, 0, hca_ids]]
            }, context=context))
        return allocating_ids

    _columns = {
        'stage': fields.selection(_stages, string='Stage'),
        'ward_id': fields.many2one('nh.clinical.location',
                                   string='Ward',
                                   domain=[['usage', '=', 'ward']]),
        'location_ids': fields.many2many('nh.clinical.location',
                                         'realloc_loc_rel', 'reallocation_id',
                                         'location_id',
                                         string='Locations'),
        'user_ids': fields.many2many('res.users', 'realloc_user_rel',
                                     'allocation_id', 'user_id',
                                     string='Users',
                                     domain=[
                                         ['groups_id.name', 'in',
                                          ['NH Clinical HCA Group',
                                           'NH Clinical Nurse Group']]
                                     ]),
        'allocating_ids': fields.many2many('nh.clinical.allocating',
                                           'real_allocating_rel',
                                           'reallocation_id',
                                           'allocating_id',
                                           string='Allocating Locations')
    }
    _defaults = {
        'stage': 'users',
        'ward_id': _get_default_ward,
        'user_ids': _get_default_users,
        'location_ids': _get_default_locations,
        'allocating_ids': _get_default_allocatings
    }

    def reallocate(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        if not isinstance(ids, int):
            raise ValueError('reallocate expected integer')
        user_pool = self.pool['res.users']
        wiz = self.read(
            cr, uid, ids, ['location_ids', 'user_ids'], context=context)
        location_ids = wiz.get('location_ids')
        loc_user_ids = self.get_users_for_locations(
            cr, uid, location_ids, context=context)
        user_ids = wiz.get('user_ids')
        recompute = False
        for u_id in loc_user_ids:
            if u_id not in user_ids and u_id != uid:
                recompute = True
                user = user_pool.read(
                    cr, uid, u_id, ['location_ids'], context=context)
                uloc_ids = user.get('location_ids')
                loc_ids = list_diff(uloc_ids, location_ids)
                self.responsibility_allocation_activity(
                    cr, uid, u_id, loc_ids, context=context)
                # Remove patient followers
                loc_ids = list_intersect(uloc_ids, location_ids)
                self.unfollow_patients_in_locations(
                    cr, uid, loc_ids, context=context)
        self.write(cr, uid, ids, {'stage': 'allocation'}, context=context)
        if recompute:
            allocating_ids = self._get_default_allocatings(cr, uid,
                                                           context=context)
            self.write(cr, uid, ids,
                       {'allocating_ids': [[6, 0, allocating_ids]]},
                       context=context)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nursing Re-Allocation',
            'res_model': 'nh.clinical.staff.reallocation',
            'res_id': ids,
            'view_mode': 'form',
            'target': 'new',
        }

    def complete(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        if not isinstance(ids, int):
            raise ValueError('Invalid ID passed to complete')
        allocating_pool = self.pool['nh.clinical.allocating']
        wizard = self.browse(cr, uid, ids, context=context)
        allocation = {
            u.id: [l.id for l in u.location_ids if l.id not
                   in wizard.location_ids.ids] for u in wizard.user_ids}
        for allocating in allocating_pool.browse(
                cr, uid, [a.id for a in wizard.allocating_ids],
                context=context):
            if allocating.nurse_id:
                allocation[allocating.nurse_id.id].append(
                    allocating.location_id.id)
                if allocating.nurse_id.id == uid:
                    allocation[allocating.nurse_id.id].append(
                        wizard.ward_id.id)
            for hca in allocating.hca_ids:
                allocation[hca.id].append(allocating.location_id.id)
            if uid not in allocation:
                allocation[uid] = [wizard.ward_id.id]
            elif wizard.ward_id.id not in allocation.get(uid):
                allocation[uid].append(wizard.ward_id.id)
        for key, value in allocation.iteritems():
            self.responsibility_allocation_activity(cr, uid, key, value,
                                                    context=context)
        return {'type': 'ir.actions.act_window_close'}


class doctor_allocation_wizard(osv.TransientModel):
    _name = 'nh.clinical.doctor.allocation'
    _rec_name = 'create_uid'

    _stages = [['review', 'De-allocate'], ['users', 'Medical Roll Call']]
    _doctor_groups = ['NH Clinical Doctor Group',
                      'NH Clinical Junior Doctor Group',
                      'NH Clinical Consultant Group',
                      'NH Clinical Registrar Group']

    def _get_default_ward(self, cr, uid, context=None):
        location_pool = self.pool['nh.clinical.location']
        ward_ids = location_pool.search(cr, uid, [['usage', '=', 'ward'],
                                                  ['user_ids', 'in', [uid]]],
                                        context=context)
        if not ward_ids:
            raise osv.except_osv(
                'Shift Management Error!',
                'You must be in charge of a ward to do this task!')
        return ward_ids[0]

    def _get_default_locations(self, cr, uid, context=None):
        location_pool = self.pool['nh.clinical.location']
        ward_ids = location_pool.search(
            cr, uid, [['usage', '=', 'ward'], ['user_ids', 'in', [uid]]],
            context=context)
        if not ward_ids:
            raise osv.except_osv(
                'Shift Management Error!',
                'You must be in charge of a ward to do this task!')
        location_ids = location_pool.search(
            cr, uid, [['id', 'child_of', ward_ids[0]]], context=context)
        return location_ids

    def _get_current_doctors(self, cr, uid, context=None):
        location_pool = self.pool['nh.clinical.location']
        user_pool = self.pool['res.users']
        ward_ids = location_pool.search(cr, uid, [['usage', '=', 'ward'],
                                                  ['user_ids', 'in', [uid]]],
                                        context=context)
        if not ward_ids:
            raise osv.except_osv(
                'Shift Management Error!',
                'You must be in charge of a ward to do this task!')
        doctor_ids = user_pool.search(
            cr, uid, [['groups_id.name', 'in', self._doctor_groups],
                      ['location_ids', 'in', ward_ids]], context=context)
        return doctor_ids

    _columns = {
        'create_uid': fields.many2one('res.users',
                                      'User Executing the Wizard'),
        'create_date': fields.datetime('Create Date'),
        'stage': fields.selection(_stages, string='Stage'),
        'ward_id': fields.many2one('nh.clinical.location', string='Ward',
                                   domain=[['usage', '=', 'ward']]),
        'doctor_ids': fields.many2many('res.users', 'docalloc_doc_rel',
                                       'allocation_id', 'user_id',
                                       string='Current Doctors'),
        'location_ids': fields.many2many('nh.clinical.location',
                                         'docalloc_loc_rel', 'allocation_id',
                                         'location_id', string='Locations'),
        'user_ids': fields.many2many(
            'res.users', 'docalloc_user_rel', 'allocation_id', 'user_id',
            string='Users', domain=[['groups_id.name', 'in', _doctor_groups]])
    }
    _defaults = {
        'stage': 'review',
        'ward_id': _get_default_ward,
        'location_ids': _get_default_locations,
        'doctor_ids': _get_current_doctors
    }

    def deallocate(self, cr, uid, ids, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        wiz = self.browse(cr, uid, ids[0], context=context)
        deallocate_location_ids = \
            [location.id for location in wiz.location_ids]

        user_pool = self.pool['res.users']
        all_doctor_ids = user_pool.search(
            cr, uid, [['groups_id.name', 'in', self._doctor_groups]],
            context=context
        )

        for doctor_id in all_doctor_ids:
            doctor_current_location_ids = user_pool.read(
                cr, uid, doctor_id, fields=['location_ids']
            )['location_ids']
            doctor_new_location_ids = \
                set(doctor_current_location_ids) - set(deallocate_location_ids)
            user_pool.write(
                cr, uid, doctor_id,
                {'location_ids': [(6, 0, doctor_new_location_ids)]},
                context=context
            )

        self.write(cr, uid, ids, {'stage': 'users'}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medical Shift Change',
            'res_model': 'nh.clinical.doctor.allocation',
            'res_id': ids[0],
            'view_mode': 'form',
            'target': 'new',
        }

    def submit_users(self, cr, uid, ids, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        wiz = self.browse(cr, uid, ids[0], context=context)
        responsibility_allocation_pool = self.pool[
            'nh.clinical.user.responsibility.allocation'
        ]

        for doctor in wiz.user_ids:
            location_ids = doctor.location_ids
            if not location_ids:
                location_ids = []
            else:
                location_ids = map(lambda i: i.id, location_ids)
            location_ids.append(wiz.ward_id.id)

            activity_id = responsibility_allocation_pool.create_activity(
                cr, uid, {}, {
                    'responsible_user_id': doctor.id,
                    # Have to use '6' in the model relationship syntax used
                    # below to replace whole list rather than '4' to
                    # simply update the list as using '4' caused a failure in
                    # the activity complete method.
                    'location_ids': [[6, 0, location_ids]]
                }, context=context
            )
            activity_pool = self.pool['nh.activity']
            activity_pool.complete(cr, uid, activity_id, context=context)
        return {'type': 'ir.actions.act_window_close'}


class allocating_user(osv.TransientModel):
    _name = 'nh.clinical.allocating'
    _rec_name = 'location_id'

    _columns = {
        'location_id': fields.many2one('nh.clinical.location', 'Location',
                                       required=1),
        'patient_ids': fields.related('location_id', 'patient_ids',
                                      type='many2many',
                                      relation='nh.clinical.patient',
                                      string='Patient'),
        'nurse_id': fields.many2one(
            'res.users', 'Responsible Nurse',
            domain=[['groups_id.name', 'in', ['NH Clinical Nurse Group']]]),
        'hca_ids': fields.many2many(
            'res.users', 'allocating_hca_rel', 'allocating_id', 'hca_id',
            string='Responsible HCAs',
            domain=[['groups_id.name', 'in', ['NH Clinical HCA Group']]]),
        'nurse_name': fields.related('nurse_id', 'name', type='char', size=100,
                                     string='Responsible Nurse')
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(allocating_user, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar, submenu)

        if view_type != 'form':
            return res

        # At this point no staff will be available as options for populating
        # the field. The rest of the method will populate the `ids` domain
        # parameter.
        nurse_ids = []
        hca_ids = []
        res['fields']['nurse_id']['domain'] = [
            ['id', 'in', nurse_ids],
            ['groups_id.name', 'in', ['NH Clinical Nurse Group']]
        ]
        res['fields']['hca_ids']['domain'] = [
            ['id', 'in', hca_ids],
            ['groups_id.name', 'in', ['NH Clinical HCA Group']]
        ]

        parent_view = context['parent_view']
        if parent_view == 'allocation':
            allocation_model = self.pool['nh.clinical.staff.allocation']
            allocation_id = allocation_model.search(
                cr, uid, [('create_uid', '=', uid)], order='id desc', limit=1)
            allocation = allocation_model.browse(
                cr, uid, allocation_id[0], context=context)
            user_ids = [u.id for u in allocation.user_ids]
        elif parent_view == 'reallocation':
            reallocation_model = self.pool[
                'nh.clinical.staff.reallocation']
            ward_id = reallocation_model._get_default_ward(
                cr, uid, context=context)
            shift_model = self.pool['nh.clinical.shift']
            shift = shift_model.get_latest_shift_for_ward(
                cr, uid, ward_id)
            user_ids = shift.nurses._ids + shift.hcas._ids
        else:
            raise ValueError(
                "Unknown view. This method does not support this view yet."
            )

        # Can add all users to both field domains because they are also
        # filtered by user group.
        nurse_ids.extend(user_ids)
        hca_ids.extend(user_ids)
        return res


class user_allocation_wizard(osv.TransientModel):
    _name = 'nh.clinical.user.allocation'

    _stages = [['wards', 'Select Wards'], ['users', 'Select Users'],
               ['allocation', 'Allocation']]

    _columns = {
        'create_uid': fields.many2one('res.users',
                                      'User Executing the Wizard'),
        'stage': fields.selection(_stages, string='Stage'),
        'ward_ids': fields.many2many('nh.clinical.location',
                                     'allocation_ward_rel', 'allocation_id',
                                     'location_id', string='Wards',
                                     domain=[['usage', '=', 'ward']]),
        'user_ids': fields.many2many('res.users', 'allocation_user_rel',
                                     'allocation_id', 'user_id',
                                     string='Users'),
        'allocating_user_ids': fields.many2many(
            'nh.clinical.allocating', 'allocating_allocation_rel',
            'allocation_id', 'allocating_user_id', string='Allocating Users')
    }
    _defaults = {
        'stage': 'users'
    }
