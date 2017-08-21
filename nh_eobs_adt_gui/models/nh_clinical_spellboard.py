# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
Defines the spellboard model. This model is backed by a view and is not
managed by the ORM (see `_auto = False`). That is why all the model methods
such as `create` and `write` are overridden and do not call `super`, as writes
to the database will fail because views cannot be updated unless you setup
rules in PostgreSQL (google 'updateable views'). You can think of this model
as a proxy that is only used as a means of updating various other underlying
models.
"""
import copy
import logging

import re
from openerp.osv import orm, fields, osv

_logger = logging.getLogger(__name__)


class nh_clinical_spellboard(orm.Model):
    """
    Provides patient spell information and operations for the GUI.
    """
    _name = "nh.clinical.spellboard"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Spell Management View"
    _rec_name = 'registration'
    _auto = False
    _table = "nh_clinical_spellboard"
    _states = [('new', 'New'), ('scheduled', 'Scheduled'),
               ('started', 'Started'), ('completed', 'Completed'),
               ('cancelled', 'Cancelled')]

    def _get_ward_id(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        location_pool = self.pool['nh.clinical.location']
        for spell in self.browse(cr, uid, ids, context=context):
            res[spell.id] = spell.location_id.id \
                if spell.location_id.usage == 'ward' \
                else location_pool.get_closest_parent_id(
                cr, uid, spell.location_id.id, 'ward', context=context)
        return res

    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1,
                                       ondelete='restrict'),
        'registration': fields.many2one(
            'nh.clinical.adt.patient.register', 'Patient', required=True),
        'location_id': fields.many2one('nh.clinical.location',
                                       'Current Location', required=True),
        'ward_id': fields.function(
            _get_ward_id, type='many2one', relation='nh.clinical.location',
            string='Admission Location'),
        'pos_id': fields.many2one('nh.clinical.pos', 'Point of Service'),
        'code': fields.char("Admission Code", size=20),
        'start_date': fields.datetime("Admission Date"),
        'move_date': fields.datetime("Last Movement Date"),
        'ref_doctor_ids': fields.many2many(
            'nh.clinical.doctor', 'ref_doctor_spell_rel', 'spell_id',
            'doctor_id', "Referring Doctors"),
        'con_doctor_ids': fields.many2many(
            'nh.clinical.doctor', 'con_doctor_spell_rel', 'spell_id',
            'doctor_id', "Consulting Doctors"),
        'hospital_number': fields.char('Hospital Number', size=200),
        'nhs_number': fields.char('NHS Number', size=200)
    }

    _defaults = {
        'code': lambda s, cr, uid, c: s.pool['ir.sequence'].next_by_code(
            cr, uid, 'nh.clinical.spell', context=c),
    }

    def init(self, cr):
        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        spell_activity.id as id,
                        spell_activity.id as activity_id,
                        register.id as registration,
                        spell.location_id as location_id,
                        spell.pos_id as pos_id,
                        spell.code as code,
                        spell.start_date as start_date,
                        spell.move_date as move_date,
                        register.other_identifier as hospital_number,
                        register.patient_identifier as nhs_number
                    from nh_activity spell_activity
                    inner join nh_clinical_spell spell
                        on spell.activity_id = spell_activity.id
                    inner join nh_clinical_adt_patient_register register
                        on spell.patient_id = register.patient_id
                    where spell_activity.data_model = 'nh.clinical.spell'
                )
        """ % (self._table, self._table))

    def format_data(self, data):
        """
        Removes any non alphanumeric symbols from hospital number
        and NHS number fields.
        """
        for field in data.keys():
            if field == 'hospital_number' or field == 'nhs_number':
                non_alphanumeric = re.compile(r'[\W_]+')
                data[field] = non_alphanumeric.sub('', data[field])

    def fetch_patient_id(self, cr, uid, data, context=None):
        """
        Fetch the patient_id from the provided Hospital Number or NHS Number.
        """
        if not context:
            context = dict()
        patient_pool = self.pool['nh.clinical.patient']
        if data.get('hospital_number'):
            patient_id = patient_pool.search(
                cr, uid,
                [['other_identifier', '=', data.get('hospital_number')]],
                context=context)
            data['patient_id'] = patient_id[0] if patient_id else False
        elif data.get('nhs_number'):
            patient_id = patient_pool.search(
                cr, uid,
                [['patient_identifier', '=', data.get('nhs_number')]],
                context=context)
            data['patient_id'] = patient_id[0] if patient_id else False

    def patient_id_change(self, cr, uid, ids, registration_id, context=None):
        """Fills hospital_number and nhs_number fields."""
        result = {'hospital_number': False, 'nhs_number': False}

        if registration_id:
            adt_register_pool = self.pool['nh.clinical.adt.patient.register']
            registration = adt_register_pool.browse(
                cr, uid, [registration_id], context=context)
            result = {
                'hospital_number': registration.other_identifier,
                'nhs_number': registration.patient_identifier
            }
        return {'value': result}

    def create(self, cr, uid, vals, context=None):
        """
        Admits a patients or raises an exception.
        A registration must already exist before this is called as the UI flow
        for the user means that they click through on the registration field
        to create one before going back to the spellboard view to create a
        spellboard record (calling this method).

        :param vals: must contain keys ``patient_id``, ``location_id``,
            ``code``, ``start_date``, ``ref_doctor_ids`` and
            ``con_doctor_ids``
        :type vals: dict
        :raises: :class:`osv.except_osv<openerp.osv.osv.except_orm>`
        :returns: id of new record
        :rtype: int
        """
        self.format_data(vals)
        if vals.get('hospital_number') or vals.get('nhs_number'):
            self.fetch_patient_id(cr, uid, vals, context=context)
            if not vals.get('patient_id'):
                raise orm.except_orm('Validation Error!', 'Patient not found!')
        api = self.pool['nh.eobs.api']
        location_pool = self.pool['nh.clinical.location']
        activity_pool = self.pool['nh.activity']
        adt_register_pool = self.pool['nh.clinical.adt.patient.register']

        registration = adt_register_pool.browse(
            cr, uid, vals.get('registration'), context=context)

        # The conditions below are necessary to accommodate both the UI flow
        # (where a register record is created from the view without an
        # activity) and calls from the code where the
        # `create_activity` -> `submit` pattern can be used to create the
        # activity before the registration record.
        if not registration.activity_id:
            data_ref = '{},{}'.format(adt_register_pool._name, registration.id)
            adt_register_pool.create_activity(
                cr, uid,
                {
                    'data_ref': data_ref
                },
                {},
                context=context
            )
        if registration.activity_id.state not in ['completed', 'cancelled']:
            # Creates the patient.
            registration.complete(registration.activity_id.id, context=context)

        patient = registration.patient_id
        location = location_pool.read(
            cr, uid, vals.get('location_id'), ['code'], context=context)

        api.admit(cr, uid, patient.other_identifier, {
            'code': vals.get('code'),
            'patient_identifier': patient.patient_identifier,
            'location': location['code'],
            'date_started': vals.get('start_date'),  # Activity field
            'start_date': vals.get('start_date'),  # ADT admit field
            'ref_doctor_ids': vals.get('ref_doctor_ids'),
            'con_doctor_ids': vals.get('con_doctor_ids')
        }, context=context)

        api.admit_update(cr, uid, patient.other_identifier, {
            'date_started': vals.get('start_date'),  # Activity field
            'start_date': vals.get('start_date'),  # ADT spell update field
            'patient_identifier': patient.patient_identifier,
            'location': location['code'],
        })
        spell_activity_id = activity_pool.search(
            cr, uid, [['patient_id', '=', patient.id],
                      ['state', 'not in', ['completed', 'cancelled']],
                      ['data_model', '=', 'nh.clinical.spell']],
            context=context)
        if not spell_activity_id:
            osv.except_osv('Error!', 'Spell does not exist after admission!')
        activity_pool.write(
            cr, uid, spell_activity_id,
            {'date_started': vals.get('start_date')}
        )
        return spell_activity_id

    def read(self, cr, uid, ids, fields=None, context=None,
             load='_classic_read'):
        """
        Extends :meth:`read()<openerp.models.Model.read>` to fetch
        fields ``con_doctor_ids`` and ``ref_doctor_ids``.
        """

        res = super(nh_clinical_spellboard, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)
        if not fields or 'ref_doctor_ids' in fields \
                or 'con_doctor_ids' in fields:
            activity_pool = self.pool['nh.activity']
            for r in res:
                spell_activity = activity_pool.browse(
                    cr, uid, r['id'], context=context)
                r['con_doctor_ids'] = [
                    cd.id for cd in spell_activity.data_ref.con_doctor_ids]
                r['ref_doctor_ids'] = [
                    rd.id for rd in spell_activity.data_ref.ref_doctor_ids]
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """
        Extends :meth:`write()<openerp.models.Model.read>` to fetch
        fields ``con_doctor_ids`` and ``ref_doctor_ids``.

        :raises: :class:`osv.except_osv<openerp.osv.osv.except_orm>`
        :returns: ``True`` if successful. Otherwise ``False``
        :rtype: bool
        """
        api_pool = self.pool['nh.eobs.api']
        location_pool = self.pool['nh.clinical.location']

        if vals.get('patient_id'):
            osv.except_osv(
                'Error!',
                'Cannot change patient from an existing spell, edit patient '
                'information instead!'
            )

        res = {}
        for spell in self.browse(cr, uid, ids, context=context):
            if vals.get('location_id'):
                location = location_pool.read(cr, uid, vals.get(
                    'location_id'), ['code'], context=context)
                res[spell.id] = api_pool.transfer(
                    cr, uid, spell.patient_id.other_identifier,
                    {'location': location['code']}, context=context)
            else:
                res[spell.id] = api_pool.admit_update(
                    cr, uid, spell.patient_id.other_identifier,
                    {
                        'location': spell.location_id.code,
                        'code': spell.code,
                        'start_date': vals.get('start_date'),
                        'ref_doctor_ids': vals.get('ref_doctor_ids'),
                        'con_doctor_ids': vals.get('con_doctor_ids')
                    },
                    context=context
                )
        return all(res.iteritems())

    def cancel_discharge(self, cr, uid, ids, context=None):
        """
        Cancels the discharge of one or more patients.

        :param ids: spell ids
        :type ids: list
        :returns: ``True`` if successful. Otherwise ``False``
        :rtype: bool
        """

        api = self.pool['nh.eobs.api']
        res = {}
        for spell in self.browse(cr, uid, ids, context=context):
            res[spell.id] = api.cancel_discharge(
                cr, uid, spell.patient_id.other_identifier, context=context)
        return all([res[r] for r in res.keys()])

    def cancel_admit_button(self, cr, uid, ids, context=None):
        """
        Button called by view_spellboard_form view to call form to
        cancel the admission of a patient.
        """
        context = self._update_context(cr, uid, ids, context=context)
        action = {
            "type": "ir.actions.act_window",
            "name": "Cancel Visit",
            "res_model": "nh.clinical.cancel_admit.wizard",
            "view_mode": "form",
            "view_type": "form",
            "views": [(False, "form")],
            "target": "new",
            "view_id": "view_cancel_admit_wizard",
            "context": context,
        }
        return action

    def transfer_button(self, cr, uid, ids, context=None):
        """
        Button called by view_spellboard_form view to call form to
        transfer patient.
        """
        context = self._update_context(cr, uid, ids, context=context)
        action = {
            "type": "ir.actions.act_window",
            "name": "Transfer Patient",
            "res_model": "nh.clinical.transfer.wizard",
            "view_mode": "form",
            "view_type": "form",
            "views": [(False, "form")],
            "target": "new",
            "view_id": "view_transfer_wizard",
            "context": context,
        }
        return action

    def discharge_button(self, cr, uid, ids, context=None):
        """
        Button called by view_spellboard_form view to call form to
        discharge patient.
        """
        context = self._update_context(cr, uid, ids, context=context)
        action = {
            "type": "ir.actions.act_window",
            "name": "Confirm Discharge",
            "res_model": "nh.clinical.discharge.wizard",
            "view_mode": "form",
            "view_type": "form",
            "views": [(False, "form")],
            "target": "new",
            "view_id": "view_discharge_wizard",
            "context": context,
        }
        return action

    def _update_context(self, cr, uid, ids, context=None):
        """Updates context with patient_id and location_id."""
        record = self.browse(cr, uid, ids, context=context)
        new_context = copy.deepcopy(context)
        if new_context:
            new_context.update({'default_patient_id': record.patient_id.id})
            new_context.update({'default_nhs_number': record.nhs_number})
            new_context.update({'default_ward_id': record.ward_id.id})
        return new_context
