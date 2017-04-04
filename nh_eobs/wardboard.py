# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
Defines models for the `Wardboard` view.
"""
import logging

from openerp import SUPERUSER_ID, api
from openerp.osv import orm, fields, osv

_logger = logging.getLogger(__name__)


class wardboard_swap_beds(orm.TransientModel):
    """
    Allows a :class:`patient<base.nh_clinical_patient>` to swap beds
    with another patient on the same ward.
    """

    _name = 'wardboard.swap_beds'

    _columns = {
        'patient1_id': fields.many2one('nh.clinical.patient',
                                       'Current Patient'),
        'patient2_id': fields.many2one('nh.clinical.patient',
                                       'Patient To Swap With'),
        'ward_location_id':  fields.many2one('nh.clinical.location', "Ward"),
        'location1_id':  fields.many2one('nh.clinical.location',
                                         "Current Patient's Location"),
        'location2_id':  fields.many2one('nh.clinical.location',
                                         "Location To Swap With"),
    }

    def do_swap(self, cr, uid, ids, context=None):
        """
        Swaps the bed :class:`locations<base.nh_clinical_location>` of
        two :class:`patients<base.nh_clinical_patient>`.

        :param ids: list of ids for records
        :type ids: list
        :returns: ``True``
        :rtype: bool
        """
        data = self.browse(cr, uid, ids[0])
        values = {
            'location1_id': data.location1_id.id,
            'location2_id': data.location2_id.id
        }
        activity_pool = self.pool['nh.activity']
        swap_pool = self.pool['nh.clinical.patient.swap_beds']
        swap_id = swap_pool.create_activity(
            cr, uid, {}, values, context=context)
        activity_pool.complete(cr, uid, swap_id, context=context)

    def onchange_location2(self, cr, uid, ids, location2_id, context=None):
        """
        Returns dictionary containing the
        :class:`patient<base.nh_clinical_patient>` id of patient in the
        :class:`location<base.nh_clinical_location>` of the
        ``location2_id`` parameter.

        :param location2_id: location id
        :type location2_id: int
        :returns: dictionary containing patient id
        :rtype: dict
        """
        if not location2_id:
            return {'value': {'patient2_id': False}}
        patient_pool = self.pool['nh.clinical.patient']
        patient_id = patient_pool.search(
            cr, uid, [['current_location_id', '=', location2_id]],
            context=context)
        if not patient_id:
            return {'value': {'patient2_id': False, 'location2_id': False}}
        return {'value': {'patient2_id': patient_id[0]}}


class wardboard_patient_placement(orm.TransientModel):
    """
    Moves :class:`patient<base.nh_clinical_patient>` from a bed
    :class:`location<base.nh_clinical_location>` to another vacant bed
    location.
    """

    _name = "wardboard.patient.placement"
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'ward_location_id':  fields.many2one('nh.clinical.location', "Ward"),
        'bed_src_location_id':  fields.many2one('nh.clinical.location',
                                                "Source Bed"),
        'bed_dst_location_id':  fields.many2one('nh.clinical.location',
                                                "Destination Bed")
    }

    def do_move(self, cr, uid, ids, context=None):
        """
        Moves the :class:`patient<base.nh_clinical_patient>` from their
        current bed location to a destination bed location.

        :param ids: record ids
        :type ids: list
        :returns: ``True``
        :rtype: bool
        """
        wiz = self.browse(cr, uid, ids[0], context=context)
        spell_pool = self.pool['nh.clinical.spell']
        move_pool = self.pool['nh.clinical.patient.move']
        activity_pool = self.pool['nh.activity']
        spell_id = spell_pool.get_by_patient_id(
            cr, uid, wiz.patient_id.id, context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        # move to location
        move_activity_id = move_pool.create_activity(
            cr, SUPERUSER_ID, {'parent_id': spell.activity_id.id},
            {'patient_id': wiz.patient_id.id,
             'location_id': wiz.bed_dst_location_id.id}, context=context)
        activity_pool.complete(cr, uid, move_activity_id, context=context)
        activity_pool.submit(
            cr, uid, spell.activity_id.id,
            {'location_id': wiz.bed_dst_location_id.id}, context=context)


class wardboard_device_session_start(orm.TransientModel):
    """
    Starts a :class:`device<devices.nh_clinical_device>` session.
    """

    _name = "wardboard.device.session.start"
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'device_category_id': fields.many2one('nh.clinical.device.category',
                                              'Device Category'),
        'device_type_id':  fields.many2one('nh.clinical.device.type',
                                           "Device Type"),
        'device_id':  fields.many2one('nh.clinical.device', "Device"),
        'location': fields.char('Location', size=50)
    }

    def onchange_device_category_id(self, cr, uid, ids, device_category_id,
                                    context=None):
        """
        Returns domain dictionary containing the
        :class:`type<devices.nh_clinical_device_type>` id of the
        :class:`device<devices.nh_clinical_device>`.

        :param device_category_id:
            :class:`category<devices.nh_clinical_device_category>` id of
            the device
        :type device_category_id: int
        :returns: domain dictionary containing ``device_type_id``
        :rtype: dict
        """
        response = False
        if device_category_id:
            response = {'value': {'device_id': False, 'device_type_id': False}}
            ids = self.pool['nh.clinical.device.type'].search(
                cr, uid, [('category_id', '=', device_category_id)])
            response.update(
                {'domain': {'device_type_id': [('id', 'in', ids)]}})
        return response

    def onchange_device_type_id(self, cr, uid, ids, device_type_id,
                                context=None):
        """
        Given a device :class:`type<devices.nh_clinical_device_type>`
        id, it returns a domain dictionary containing the
        :class:`device<devices.nh_clinical_device>` id.

        :param device_type_id: type id of the device
        :type device_type_id: int
        :returns: domain dictionary containing ``device_id``
        :rtype: dict
        """

        response = False
        if device_type_id:
            response = {'value': {'device_id': False}}
            ids = self.pool['nh.clinical.device'].search(
                cr, uid, [('type_id', '=', device_type_id)])
            response.update(
                {'domain': {'device_id': [('id', 'in', ids),
                                          ('is_available', '=', True)]}})
        return response

    def onchange_device_id(self, cr, uid, ids, device_id, context=None):
        """
        Given a device :class:`device<devices.nh_clinical_device>` id,
        it returns a domain dictionary containing the
        :class:`type<devices.nh_clinical_device_type>` id.

        :param device_id: id of the device
        :type device_id: int
        :returns: domain dictionary containing ``device_id``
        :rtype: dict
        """

        device_pool = self.pool['nh.clinical.device']
        if not device_id:
            return {}
        device = device_pool.browse(cr, uid, device_id, context=context)
        return {'value': {'device_type_id': device.type_id.id}}

    def do_start(self, cr, uid, ids, context=None):
        """
        Starts a :class:`session<devices.nh_clinical_device_session>`
        for a device.

        :param ids: record ids
        :type ids: list
        :returns: ``True``
        :rtype: bool
        """
        session_pool = self.pool['nh.clinical.device.session']
        activity_pool = self.pool['nh.activity']
        wiz = self.browse(cr, uid, ids[0], context=context)
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(
            cr, uid, wiz.patient_id.id, context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        device_activity_id = session_pool.create_activity(
            cr, uid, {'parent_id': spell.activity_id.id},
            {'patient_id': wiz.patient_id.id,
             'device_type_id': wiz.device_type_id.id,
             'device_id': wiz.device_id.id if wiz.device_id else False})
        activity_pool.start(cr, uid, device_activity_id, context=context)
        activity_pool.submit(
            cr, uid, device_activity_id, {'location': wiz.location},
            context=context)


class wardboard_device_session_complete(orm.TransientModel):
    """
    Completes a :class:`session<devices.nh_clinical_device_session>` for
    a device.
    """

    _name = "wardboard.device.session.complete"

    _columns = {
        'session_id': fields.many2one('nh.clinical.device.session', 'Session'),
        'removal_reason': fields.char('Removal reason', size=100),
        'planned': fields.selection((('planned', 'Planned'),
                                     ('unplanned', 'Unplanned')), 'Planned?')
    }

    def do_complete(self, cr, uid, ids, context=None):
        """
        Completed a :class:`session<devices.nh_clinical_device_session>`
        for a device.

        :param ids: record ids
        :type ids: list
        :returns: Odoo `action` definition
        :rtype: dict
        """

        activity_pool = self.pool['nh.activity']
        wiz = self.browse(cr, uid, ids[0])
        activity_pool.submit(
            cr, uid, wiz.session_id.activity_id.id,
            {'removal_reason': wiz.removal_reason, 'planned': wiz.planned},
            context=context)
        activity_pool.complete(
            cr, uid, wiz.session_id.activity_id.id, context=context)
        spell_activity_id = wiz.session_id.activity_id.parent_id.id
        wardboard_pool = self.pool['nh.clinical.wardboard']
        wardboard_id = wardboard_pool.search(
            cr, uid, [['spell_activity_id', '=', spell_activity_id]])[0]
        view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs', 'view_wardboard_form')[1]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': wardboard_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': context,
            'view_id': view_id
        }


class nh_clinical_device_session(orm.Model):
    """
    Extends :class:`session<devices.nh_clinical_device_session>`.
    """

    _inherit = "nh.clinical.device.session"

    def device_session_complete(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`device session complete<wardboard_device_session_complete>`
        for the view ``view_wardboard_device_session_complete_form``.

        :param ids: record ids
        :type ids: list
        :returns: Odoo `action` definition
        :rtype: dict
        """

        device_session = self.browse(cr, uid, ids[0], context=context)
        res_id = self.pool['wardboard.device.session.complete'].create(
            cr, uid, {'session_id': device_session.id})
        view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs',
            'view_wardboard_device_session_complete_form')[1]

        return {
            'name': "Complete Device Session: %s"
                    % device_session.patient_id.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.device.session.complete',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': view_id
        }


class nh_clinical_wardboard(orm.Model):
    """
    Represents a :class:`patient<base.nh_clinical_patient>` with basic
    patient information (`admission`, `spell`, `location`, etc.).

    Also includes
    :class:`observation<observations.nh_clinical_patient_observation>`
    data such as
    :class:`EWS<ews.nh_clinical_patient_observation_ews>`
    etc.

    Wardboard overrides the init method and others to provide an implementation
    that is backed by database views. When accessing fields on a wardboard,
    rather than allowing Odoo's ORM to retrieve them from database tables, we
    are using function fields that call methods that execute hand-written SQL
    queries on database views. We ensure that the database views these methods
    use are created when the model is first loaded and it's `init` method is
    called.

    Calling create on wardboard fails. Instead you should just browse for them
    as if they already exist, using the spell id as the id
    (or multiple spell ids). The id(s) used are passed to the function fields
    to retrieve the data, so a wardboard record with the correct id simply has
    the means to get the data you'd expect, it does not need to be formally
    created.
    """

    _name = "nh.clinical.wardboard"
    _description = "Wardboard"
    _auto = False
    _table = "nh_clinical_wardboard"
    _trend_strings = [('up', 'up'), ('down', 'down'), ('same', 'same'),
                      ('none', 'none'), ('one', 'one')]
    _rec_name = 'full_name'

    def _get_logo(self, cr, uid, ids, fields_name, arg, context=None):
        res = {}
        for board in self.browse(cr, uid, ids, context=context):
            res[board.id] = board.patient_id.partner_id.company_id.logo
        return res

    _clinical_risk_selection = [['NoScore', 'No Score Yet'],
                                ['High', 'High Risk'],
                                ['Medium', 'Medium Risk'],
                                ['Low', 'Low Risk'],
                                ['None', 'No Risk']]
    _boolean_selection = [('yes', 'Yes'),
                          ('no', 'No')]

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(nh_clinical_wardboard, self).fields_view_get(
            cr, user, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and res['fields'].get('o2target'):
            user_pool = self.pool['res.users']
            user_ids = user_pool.search(
                cr, user,
                [['groups_id.name',
                  'in',
                  ['NH Clinical Doctor Group',
                   'NH Clinical Shift Coordinator Group']]],
                context=context
            )
            res['fields']['o2target']['readonly'] = not (user in user_ids)
        return res

    def _get_started_device_session_ids(self, cr, uid, ids, field_name, arg,
                                        context=None):
        res = {}.fromkeys(ids, False)
        sql = """select spell_id, ids
                    from wb_activity_data
                    where data_model='nh.clinical.device.session'
                        and state in ('started') and spell_id in (%s)""" \
              % ", ".join([str(spell_id) for spell_id in ids])
        cr.execute(sql)
        res.update({r['spell_id']: r['ids'] for r in cr.dictfetchall()})
        return res

    def _get_terminated_device_session_ids(self, cr, uid, ids, field_name, arg,
                                           context=None):
        res = {}.fromkeys(ids, False)
        sql = """select spell_id, ids
                    from wb_activity_data
                    where data_model='nh.clinical.device.session'
                        and state in ('completed', 'cancelled') and spell_id
                        in (%s)""" % ", ".join(
            [str(spell_id) for spell_id in ids])
        cr.execute(sql)
        res.update({r['spell_id']: r['ids'] for r in cr.dictfetchall()})
        return res

    def _get_recently_discharged_uids(self, cr, uid, ids, field_name, arg,
                                      context=None):
        res = {}.fromkeys(ids, False)
        if ids:
            sql = """select spell_id, user_ids, ward_user_ids
                        from last_discharge_users
                        where spell_id in (%s)""" % ", ".join(
                [str(spell_id) for spell_id in ids])
            cr.execute(sql)
            res.update(
                {r['spell_id']: list(set(r['user_ids'] + r['ward_user_ids']))
                 for r in cr.dictfetchall()})
        return res

    def _get_data_ids_multi(self, cr, uid, ids, field_names, arg,
                            context=None):
        res = {i: {field_name: [] for field_name in field_names} for i in ids}
        for field_name in field_names:
            model_name = self._columns[field_name]._obj
            sql = """select spell_id, ids
                     from wb_activity_data
                     where data_model='%s'
                     and spell_id in (%s) and state='completed'""" \
                  % (model_name, ", ".join(
                [str(spell_id) for spell_id in ids]))
            cr.execute(sql)
            rows = cr.dictfetchall()
            for row in rows:
                res[row['spell_id']][field_name] = row['ids']
        return res

    def _get_transferred_user_ids(self, cr, uid, ids, field_names, arg,
                                  context=None):
        res = {}.fromkeys(ids, False)
        if ids:
            sql = """select spell_id, user_ids, ward_user_ids
                        from last_transfer_users
                        where spell_id in (%s)""" % ", ".join(
                [str(spell_id) for spell_id in ids])
            cr.execute(sql)
            res.update(
                {r['spell_id']: list(
                    set(r['user_ids'] + r['ward_user_ids']))
                 for r in cr.dictfetchall()})
        return res

    def _transferred_user_ids_search(self, cr, uid, obj, name, args,
                                     domain=None, context=None):
        arg1, op, arg2 = args[0]
        arg2 = arg2 if isinstance(arg2, (list, tuple)) else [arg2]
        all_ids = self.search(cr, uid, [])
        wb_user_map = self._get_transferred_user_ids(
            cr, uid, all_ids, 'transferred_user_ids', None, context=context)
        wb_ids = [k for k, v in wb_user_map.items() if set(
            v or []) & set(arg2 or [])]
        return [('id', 'in', wb_ids)]

    def _recently_discharged_uids_search(self, cr, uid, obj, name, args,
                                         domain=None, context=None):
        arg1, op, arg2 = args[0]
        arg2 = arg2 if isinstance(arg2, (list, tuple)) else [arg2]
        all_ids = self.search(cr, uid, [])
        user_ids = self._get_recently_discharged_uids(
            cr, uid, all_ids, 'recently_discharged_uids', None,
            context=context)
        wb_ids = [k for k, v in user_ids.items() if set(
            v or []) & set(arg2 or [])]
        return [('id', 'in', wb_ids)]

    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient',
                                      required=1, ondelete='restrict'),
        'company_logo': fields.function(_get_logo, type='binary',
                                        string='Logo'),
        'spell_activity_id': fields.many2one('nh.activity', 'Spell Activity'),
        'spell_date_started': fields.datetime('Spell Start Date'),
        'time_since_admission': fields.text('Time since Admission'),
        'move_date': fields.datetime('Time since Last Movement'),
        'spell_date_terminated': fields.datetime('Spell Discharge Date'),
        'recently_discharged': fields.boolean('Recently Discharged'),
        'spell_state': fields.char('Spell State', size=50),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS'),
        'spell_code': fields.text('Spell Code'),
        'full_name': fields.text("Family Name"),
        'given_name': fields.text("Given Name"),
        'middle_names': fields.text("Middle Names"),
        'family_name': fields.text("Family Name"),
        'location': fields.text("Location"),
        'initial': fields.text("Patient Name Initial"),
        'clinical_risk': fields.selection(_clinical_risk_selection,
                                          "Clinical Risk"),
        'ward_id': fields.many2one('nh.clinical.location', 'Ward'),
        'location_id': fields.many2one('nh.clinical.location', "Location"),
        'location_full_name': fields.related(
            'location_id', 'full_name', type='char', size=150,
            string='Location Name'),
        'sex': fields.text("Sex"),
        'dob': fields.datetime("DOB"),
        'hospital_number': fields.text('Hospital Number'),
        'nhs_number': fields.text('NHS Number'),
        'age': fields.integer("Age"),
        'date_scheduled': fields.datetime("Date Scheduled"),
        'next_diff': fields.text("Time to Next Obs"),
        'frequency': fields.text("Frequency"),
        'ews_score_string': fields.text("Latest Score"),
        'ews_score': fields.integer("Latest Score"),
        'ews_trend_string': fields.selection(_trend_strings,
                                             "Score Trend String"),
        'ews_trend': fields.integer("Score Trend"),
        'mrsa': fields.selection(_boolean_selection, "MRSA"),
        'diabetes': fields.selection(_boolean_selection, "Diabetes"),
        'palliative_care': fields.selection(_boolean_selection,
                                            "Palliative Care"),
        'post_surgery': fields.selection(_boolean_selection, "Post Surgery"),
        'critical_care': fields.selection(_boolean_selection, "Critical Care"),
        'pbp_monitoring': fields.selection(
            _boolean_selection, "Postural Blood Pressure Monitoring"),
        'height': fields.float("Height"),
        'o2target': fields.many2one('nh.clinical.o2level', 'O2 Target'),
        'uotarget_vol': fields.integer('Target Volume'),
        'uotarget_unit': fields.selection(
            [[1, 'ml/hour'], [2, 'L/day']], 'Unit'),
        'consultant_names': fields.text("Consulting Doctors"),
        'terminated_device_session_ids': fields.function(
            _get_terminated_device_session_ids, type='many2many',
            relation='nh.clinical.device.session',
            string='Device Session History'),
        'started_device_session_ids': fields.function(
            _get_started_device_session_ids, type='many2many',
            relation='nh.clinical.device.session',
            string='Started Device Sessions'),
        'spell_ids': fields.function(
            _get_data_ids_multi, multi='spell_ids', type='many2many',
            relation='nh.clinical.spell', string='Spells'),
        'move_ids': fields.function(
            _get_data_ids_multi, multi='move_ids', type='many2many',
            relation='nh.clinical.patient.move', string='Patient Moves'),
        'o2target_ids': fields.function(
            _get_data_ids_multi, multi='o2target_ids', type='many2many',
            relation='nh.clinical.patient.o2target', string='O2 Targets'),
        'uotarget_ids': fields.function(
            _get_data_ids_multi, multi='uotarget_ids', type='many2many',
            relation='nh.clinical.patient.uotarget',
            string='Urine Output Targets'),
        'blood_sugar_ids': fields.function(
            _get_data_ids_multi, multi='blood_sugar_ids', type='many2many',
            relation='nh.clinical.patient.observation.blood_sugar',
            string='Blood Sugar Obs'),
        'mrsa_ids': fields.function(
            _get_data_ids_multi, multi='mrsa_ids', type='many2many',
            relation='nh.clinical.patient.mrsa', string='MRSA'),
        'diabetes_ids': fields.function(
            _get_data_ids_multi, multi='diabetes_ids', type='many2many',
            relation='nh.clinical.patient.diabetes', string='Diabetes'),
        'pbp_monitoring_ids': fields.function(
            _get_data_ids_multi, multi='pbp_monitoring_ids', type='many2many',
            relation='nh.clinical.patient.pbp_monitoring',
            string='PBP Monitoring'),
        'palliative_care_ids': fields.function(
            _get_data_ids_multi, multi='palliative_care_ids', type='many2many',
            relation='nh.clinical.patient.palliative_care',
            string='Palliative Care'),
        'post_surgery_ids': fields.function(
            _get_data_ids_multi, multi='post_surgery_ids', type='many2many',
            relation='nh.clinical.patient.post_surgery',
            string='Post Surgery'),
        'critical_care_ids': fields.function(
            _get_data_ids_multi, multi='critical_care_ids', type='many2many',
            relation='nh.clinical.patient.critical_care',
            string='Critical Care'),
        'pbp_ids': fields.function(
            _get_data_ids_multi, multi='pbp_ids', type='many2many',
            relation='nh.clinical.patient.observation.pbp', string='PBP Obs'),
        'ews_ids': fields.function(
            _get_data_ids_multi, multi='ews_ids', type='many2many',
            relation='nh.clinical.patient.observation.ews', string='EWS Obs'),
        'gcs_ids': fields.function(
            _get_data_ids_multi, multi='gcs_ids', type='many2many',
            relation='nh.clinical.patient.observation.gcs', string='GCS Obs'),
        'pain_ids': fields.function(
            _get_data_ids_multi, multi='pain_ids', type='many2many',
            relation='nh.clinical.patient.observation.pain',
            string='Pain Obs'),
        'urine_output_ids': fields.function(
            _get_data_ids_multi, multi='urine_output_ids', type='many2many',
            relation='nh.clinical.patient.observation.urine_output',
            string='Urine Output Flag'),
        'ews_list_ids': fields.function(
            _get_data_ids_multi, multi='ews_list_ids', type='many2many',
            relation='nh.clinical.patient.observation.ews',
            string='EWS Obs List'),
        'transferred_user_ids': fields.function(
            _get_transferred_user_ids, type='many2many', relation='res.users',
            fnct_search=_transferred_user_ids_search,
            string='Recently Transferred Access'),
        'recently_discharged_uids': fields.function(
            _get_recently_discharged_uids, type='many2many',
            relation='res.users', fnct_search=_recently_discharged_uids_search,
            string='Recently Discharged Access'),
    }

    _order = 'location asc'

    def _get_cr_groups(self, cr, uid, ids, domain, read_group_order=None,
                       access_rights_uid=None, context=None):
        res = [['NoScore', 'No Score Yet'], ['High', 'High Risk'],
               ['Medium', 'Medium Risk'], ['Low', 'Low Risk'],
               ['None', 'No Risk']]
        fold = {r[0]: False for r in res}
        return res, fold

    _group_by_full = {
        'clinical_risk': _get_cr_groups,
    }

    def onchange_palliative_care(self, cr, uid, ids, pc, ps, cc, context=None):
        """
        Checks if any of the other special circumstances parameters
        are ``True`` and returns a warning if that is the case.

        :param pc: palliative care value
        :type pc: str
        :param ps: post surgery value
        :type ps: str
        :param cc: critical care value
        :type cc: str
        :returns: dictionary containing warning and/or values
        :rtype: dict
        """
        res = {}
        if pc == 'no':
            return res
        # wb = self.browse(cr, uid, ids[0], context=context)
        if ps == 'yes':
            res['warning'] = {
                'title': 'Warning',
                'message': 'You must deactivate Post Surgery status first'
            }
            res['value'] = {
                'palliative_care': 'no'
            }
            return res
        if cc == 'yes':
            res['warning'] = {
                'title': 'Warning',
                'message': 'You must deactivate Critical Care status first'
            }
            res['value'] = {
                'palliative_care': 'no'
            }
            return res
        return res

    def onchange_critical_care(self, cr, uid, ids, pc, ps, cc, context=None):
        """
        Checks if any of the other special circumstances parameters
        are ``True`` and returns a warning if that is the case.

        :param pc: palliative care value
        :type pc: str
        :param ps: post surgery value
        :type ps: str
        :param cc: critical care value
        :type cc: str
        :returns: dictionary containing warning and/or values
        :rtype: dict
        """
        res = {}
        if cc == 'no':
            return res
        # wb = self.browse(cr, uid, ids[0], context=context)
        if ps == 'yes':
            res['warning'] = {
                'title': 'Warning',
                'message': 'You must deactivate Post Surgery status first'
            }
            res['value'] = {
                'critical_care': 'no'
            }
            return res
        if pc == 'yes':
            res['warning'] = {
                'title': 'Warning',
                'message': 'You must deactivate Palliative Care status first'
            }
            res['value'] = {
                'critical_care': 'no'
            }
            return res
        return res

    def onchange_post_surgery(self, cr, uid, ids, pc, ps, cc, context=None):
        """
        Checks if any of the other special circumstances parameters
        are ``True`` and returns a warning if that is the case.

        :param pc: palliative care value
        :type pc: str
        :param ps: post surgery value
        :type ps: str
        :param cc: critical care value
        :type cc: str
        :returns: dictionary containing warning and/or values
        :rtype: dict
        """
        res = {}
        if ps == 'no':
            return res
        if pc == 'yes':
            res['warning'] = {
                'title': 'Warning',
                'message': 'You must deactivate Palliative Care status first'
            }
            res['value'] = {
                'post_surgery': 'no'
            }
            return res
        if cc == 'yes':
            res['warning'] = {
                'title': 'Warning',
                'message': 'You must deactivate Critical Care status first'
            }
            res['value'] = {
                'post_surgery': 'no'
            }
            return res
        return res

    def device_session_start(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`device session start<wardboard_device_session_start>`
        for the view ``view_wardboard_device_session_start_form``.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        wardboard = self.browse(cr, uid, ids[0], context=context)
        res_id = self.pool['wardboard.device.session.start'].create(
            cr, uid, {'patient_id': wardboard.patient_id.id,
                      'device_id': None})
        view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs', 'view_wardboard_device_session_start_form')[1]
        return {
            'name': "Start Device Session: %s" % wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.device.session.start',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': view_id
        }

    def open_previous_spell(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`wardboard<nh_clinical_wardboard>` for the view
        ``view_wardboard_form_discharged`` to open a previous
        :class:`spell<spell.nh_clinical_spell>`.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        activity_pool = self.pool['nh.activity']
        wb = self.browse(cr, uid, ids[0], context=context)
        activity_ids = activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.spell'],
            ['patient_id', '=', wb.patient_id.id],
            ['sequence', '<', wb.spell_activity_id.sequence],
            ['state', '=', 'completed']
        ], order='sequence desc', context=context)
        if not activity_ids:
            raise osv.except_osv(
                'No previous spell!',
                'This is the oldest spell available for this patient.')
        spell_id = activity_pool.browse(
            cr, uid, activity_ids[0], context=context).data_ref.id
        view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs', 'view_wardboard_form_discharged')[1]
        return {
            'name': 'Previous Spell',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': spell_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': context,
            'view_id': view_id
        }

    def wardboard_swap_beds(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`swap beds<wardboard_swap_beds>` for the view
        ``view_wardboard_swap_beds_form``.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        swap_beds_pool = self.pool['wardboard.swap_beds']
        wb = self.browse(cr, uid, ids[0])
        res_id = swap_beds_pool.create(cr, uid, {
            'patient1_id':  wb.patient_id.id,
            'location1_id': wb.location_id.id,
            'ward_location_id': wb.location_id.parent_id.id}, context=context)
        view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs', 'view_wardboard_swap_beds_form')[1]
        return {
            'name': "Swap Beds",
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.swap_beds',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': view_id
        }

    def wardboard_patient_placement(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`patient placement<wardboard_patient_placement>` for the
        view ``view_wardboard_patient_placement_form``. Raises an
        exception if :class:`patient<base.nh_clinical_patient>` isn't
        placed in a bed.

        :param ids: records ids
        :type ids: list
        :raises: :class:`osv.except_osv<openerp.osv.osv.except_orm>`
        :returns: Odoo form window action
        :rtype: dict
        """

        wardboard = self.browse(cr, uid, ids[0], context=context)
        if wardboard.location_id.usage != 'bed':
            raise osv.except_osv(
                "Patient Board Error!",
                "Patient must be placed to bed before moving!")
        sql = """
        with
            recursive route(level, path, parent_id, id) as (
                    select 0, id::text, parent_id, id
                    from nh_clinical_location
                    where parent_id is null
                union
                    select level + 1, path||','||location.id,
                        location.parent_id, location.id
                    from nh_clinical_location location
                    join route on location.parent_id = route.id
            )
            select
                route.id as location_id,
                ('{'||path||'}')::int[] as parent_ids
            from route
            where id = %s
            order by path
        """ % wardboard.location_id.id
        cr.execute(sql)
        parent_ids = (cr.dictfetchone() or {}).get('parent_ids')
        ward_location_ids = self.pool['nh.clinical.location'].search(
            cr, uid, [['id', 'in', parent_ids], ['usage', '=', 'ward']])
        ward_location_id = ward_location_ids and ward_location_ids[0] or False
        res_id = self.pool['wardboard.patient.placement'].create(
            cr, uid,
            {'patient_id': wardboard.patient_id.id,
             'ward_location_id': ward_location_id if ward_location_id
             else wardboard.location_id.parent_id.id,
             'bed_src_location_id': wardboard.location_id.id,
             'bed_dst_location_id': None
             }, context=context)
        view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs', 'view_wardboard_patient_placement_form')[1]
        return {
            'name': "Move Patient: %s" % wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.patient.placement',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': view_id
        }

    def wardboard_prescribe(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`wardboard<nh_clinical_wardboard>` for the view
        ``view_wardboard_prescribe_form``.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(
            cr, uid, [('name', '=', 'view_wardboard_prescribe_form')],
            context=context)
        view_id = model_data_pool.read(
            cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': context,
            'view_id': int(view_id)
        }

    def wardboard_chart(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`wardboard<nh_clinical_wardboard>` for the view
        ``view_wardboard_chart_form``.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(
            cr, uid, [('name', '=', 'view_wardboard_chart_form')],
            context=context)
        view_id = model_data_pool.read(
            cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': int(view_id)
        }

    def wardboard_bs_chart(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`wardboard<nh_clinical_wardboard>` for the view
        ``view_wardboard_bs_chart_form``.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        wardboard = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(
            cr, uid, [('name', '=', 'view_wardboard_bs_chart_form')],
            context=context)
        view_id = model_data_pool.read(
            cr, uid, model_data_ids, ['res_id'], context=context)[0]['res_id']
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': int(view_id)
        }

    def wardboard_ews(self, cr, uid, ids, context=None):
        """
        Returns an Odoo tree window action for `completed`
        :class:`ews<ews.nh_clinical_patient_observation_ews>`.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        wardboard = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.patient.observation.ews',
            'view_mode': 'tree',
            'view_type': 'tree',
            'domain': [('patient_id', '=', wardboard.patient_id.id),
                       ('state', '=', 'completed')],
            'target': 'new',
            'context': context
        }

    def wardboard_place(self, cr, uid, ids, context=None):
        """
        Returns an Odoo form window action for
        :class:`patient placement<operations.nh_clinical_patient_placement>`
        for the view ``view_patient_placement_complete``.

        :param ids: records ids
        :type ids: list
        :returns: Odoo form window action
        :rtype: dict
        """

        wardboard = self.browse(cr, uid, ids[0], context=context)
        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(
            cr, uid, [('name', '=', 'view_patient_placement_complete')],
            context=context)
        view_id = model_data_pool.read(
            cr, uid, model_data_ids, ['res_id'], context)[0]['res_id']
        res_activity_id = self.pool['nh.activity'].search(cr, uid, [
            ['parent_id', '=', wardboard.spell_activity_id.id],
            ['data_model', '=', 'nh.clinical.patient.placement'],
            ['state', 'not in', ['completed', 'cancelled']]], context=context)
        res_id = self.pool['nh.clinical.patient.placement'].search(
            cr, uid, [['activity_id', 'in', res_activity_id]], context=context)
        context.update({'active_id': res_activity_id[0]})
        return {
            'name': wardboard.full_name + ' Placement',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.patient.placement',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': res_id[0],
            'target': 'new',
            'view_id': int(view_id),
            'context': context
        }

    def write(self, cr, uid, ids, vals, context=None):
        """
        Extends Odoo's :meth:`write()<openerp.models.Model.write>`.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        for wb in self.browse(cr, uid, ids, context=context):
            if 'mrsa' in vals:
                mrsa_pool = self.pool['nh.clinical.patient.mrsa']
                mrsa_id = mrsa_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'status': vals['mrsa'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, mrsa_id, context=context)
            if 'diabetes' in vals:
                diabetes_pool = self.pool['nh.clinical.patient.diabetes']
                diabetes_id = diabetes_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'status': vals['diabetes'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, diabetes_id, context=context)
            if 'pbp_monitoring' in vals:
                pbpm_pool = self.pool['nh.clinical.patient.pbp_monitoring']
                pbpm_id = pbpm_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'status': vals['pbp_monitoring'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, pbpm_id, context=context)
            if 'o2target' in vals:
                o2target_pool = self.pool['nh.clinical.patient.o2target']
                o2target_id = o2target_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'level_id': vals['o2target']
                }, context=context)
                activity_pool.complete(cr, uid, o2target_id, context=context)
            if 'palliative_care' in vals:
                pc_pool = self.pool['nh.clinical.patient.palliative_care']
                pc_id = pc_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': wb.spell_activity_id.id,
                }, {
                    'patient_id': wb.spell_activity_id.patient_id.id,
                    'status': vals['palliative_care'] == 'yes'
                }, context=context)
                activity_pool.complete(cr, uid, pc_id, context=context)
        return True

    @api.model
    def get_by_spell_activity_id(self, spell_activity_id):
        wardboard = \
            self.search([('spell_activity_id', '=', spell_activity_id)])
        wardboard.ensure_one()
        return wardboard

    def init(self, cr):
        settings_pool = self.pool['nh.clinical.settings']
        nh_eobs_sql = self.pool['nh.clinical.sql']
        dt_period = \
            settings_pool.get_setting(cr, 1, 'discharge_transfer_period')
        last_discharge_users = \
            nh_eobs_sql.get_last_discharge_users('{0}d'.format(dt_period))
        last_transfer_users = \
            nh_eobs_sql.get_last_transfer_users('{0}d'.format(dt_period))
        wardboard = nh_eobs_sql.get_wardboard('{0}d'.format(dt_period))
        wb_transfer_ranked = nh_eobs_sql.get_wb_transfer_ranked_sql()
        cr.execute("""

-- materialized views
drop materialized view if exists ews0 cascade;
drop materialized view if exists ews1 cascade;
drop materialized view if exists ews2 cascade;
drop materialized view if exists ward_locations cascade;
drop materialized view if exists param cascade;
drop materialized view if exists pbp cascade;

create or replace view
-- activity per spell, data_model, state
wb_activity_ranked as(
        select
            spell.id as spell_id,
            activity.*,
            split_part(activity.data_ref, ',', 2)::int as data_id,
            rank() over (partition by spell.id, activity.data_model,
                activity.state order by activity.sequence desc)
        from nh_clinical_spell spell
        inner join nh_activity activity
            on activity.spell_activity_id = spell.activity_id
);

create or replace view
-- ews per spell, data_model, state
wb_ews_ranked as(
    select *
    from (
        select
            spell.id as spell_id,
            activity.*,
            split_part(activity.data_ref, ',', 2)::int as data_id,
            rank() over (partition by spell.id, activity.data_model,
                activity.state order by activity.sequence desc)
    from nh_clinical_spell spell
    inner join nh_activity activity
        on activity.spell_activity_id = spell.activity_id
        and activity.data_model = 'nh.clinical.patient.observation.ews'
    left join nh_clinical_patient_observation_ews ews
        on ews.activity_id = activity.id
    where activity.state = 'scheduled'
    or (activity.state != 'scheduled'
        and ews.clinical_risk != 'Unknown')) sub_query
    where rank < 3
);

create or replace view
wb_spell_ranked as(
    select *
    from (
        select
            spell.id as spell_id,
            activity.*,
            split_part(activity.data_ref, ',', 2)::int as data_id,
            rank() over (partition by spell.id, activity.data_model,
                activity.state order by activity.sequence desc)
    from nh_clinical_spell spell
    inner join nh_activity activity
        on activity.id = spell.activity_id) sub_query
    where rank = 1
);

create or replace view
-- transfer per spell, data_model, state
wb_transfer_ranked as({wb_transfer_ranked});

create or replace view
-- discharge per spell, data_model, state
wb_discharge_ranked as(
    select *
    from (
        select
            spell.id as spell_id,
            activity.*,
            split_part(activity.data_ref, ',', 2)::int as data_id,
            rank() over (partition by spell.id, activity.data_model,
                activity.state order by activity.sequence desc)
    from nh_clinical_spell spell
    inner join nh_activity activity
        on activity.spell_activity_id = spell.activity_id
        and activity.data_model = 'nh.clinical.patient.discharge') sub_query
    where rank = 1
);

create materialized view
ward_locations as(
    with recursive ward_loc(id, parent_id, path, ward_id) as (
        select lc.id, lc.parent_id, ARRAY[lc.id] as path, lc.id as ward_id
        from nh_clinical_location as lc
        where lc.usage = 'ward'
        union all
        select l.id, l.parent_id, w.path || ARRAY[l.id] as path, w.path[1]
            as ward_id
        from ward_loc as w, nh_clinical_location as l
        where l.parent_id = w.id)
    select * from ward_loc
);

create or replace view
wb_activity_latest as(
    with
    max_sequence as(
        select
            spell.id as spell_id,
            activity.data_model,
            activity.state,
            max(activity.sequence) as sequence
        from nh_clinical_spell spell
        inner join nh_activity activity
            on activity.patient_id = spell.patient_id
        group by spell_id, activity.data_model, activity.state
    )
    select
        max_sequence.spell_id,
        activity.state,
        array_agg(activity.id) as ids
    from nh_activity activity
    inner join max_sequence on max_sequence.data_model = activity.data_model
         and max_sequence.state = activity.state
         and max_sequence.sequence = activity.sequence
    group by max_sequence.spell_id, activity.state
);

create or replace view
-- activity data ids per spell/patient_id, data_model, state
wb_activity_data as(
        select
            spell.id as spell_id,
            spell.patient_id,
            activity.data_model,
            activity.state,
            array_agg(split_part(activity.data_ref, ',', 2)::int
                order by split_part(activity.data_ref, ',', 2)::int desc)
                as ids
        from nh_clinical_spell spell
        inner join nh_activity spell_activity
            on spell_activity.id = spell.activity_id
        inner join nh_activity activity
            on activity.parent_id = spell_activity.id
        group by spell_id, spell.patient_id, activity.data_model,
            activity.state
);

create materialized view
ews0 as(
            select
                activity.parent_id as spell_activity_id,
                activity.patient_id,
                activity.spell_id,
                activity.state,
                activity.date_scheduled,
                ews.id,
                ews.score,
                ews.frequency,
                ews.clinical_risk,
                case when activity.date_scheduled < now() at time zone 'UTC'
                    then 'overdue: ' else '' end as next_diff_polarity,
                case activity.date_scheduled is null
                    when false then justify_hours(greatest(now() at time zone
                    'UTC',activity.date_scheduled) - least(now() at time zone
                    'UTC', activity.date_scheduled))
                    else interval '0s'
                end as next_diff_interval,
                activity.rank
            from wb_ews_ranked activity
            left join nh_clinical_patient_observation_ews ews
                on activity.data_id = ews.id
            where activity.rank = 1 and activity.state = 'scheduled'
);

create materialized view
ews1 as(
            select
                activity.parent_id as spell_activity_id,
                activity.patient_id,
                activity.spell_id,
                activity.state,
                activity.date_scheduled,
                activity.date_terminated,
                ews.id,
                ews.score,
                ews.frequency,
                ews.clinical_risk,
                case when activity.date_scheduled < now() at time zone 'UTC'
                    then 'overdue: ' else '' end as next_diff_polarity,
                case activity.date_scheduled is null
                    when false then justify_hours(greatest(now() at time zone
                    'UTC',activity.date_scheduled) - least(now() at time zone
                    'UTC', activity.date_scheduled))
                    else interval '0s'
                end as next_diff_interval,
                activity.rank
            from wb_ews_ranked activity
            inner join nh_clinical_patient_observation_ews ews
                on activity.data_id = ews.id
            where activity.rank = 1 and activity.state = 'completed'
);

create materialized view
ews2 as(
            select
                activity.parent_id as spell_activity_id,
                activity.patient_id,
                activity.spell_id,
                activity.state,
                activity.date_scheduled,
                ews.id,
                ews.score,
                ews.frequency,
                ews.clinical_risk,
                case when activity.date_scheduled < now() at time zone 'UTC'
                then 'overdue: ' else '' end as next_diff_polarity,
                case activity.date_scheduled is null
                    when false then justify_hours(greatest(now() at time zone
                    'UTC',activity.date_scheduled) - least(now() at time zone
                    'UTC', activity.date_scheduled))
                    else interval '0s'
                end as next_diff_interval,
                activity.rank
            from wb_ews_ranked activity
            inner join nh_clinical_patient_observation_ews ews
            on activity.data_id = ews.id
            where activity.rank = 2 and activity.state = 'completed'
);

create or replace view
consulting_doctors as(
            select
                spell.id as spell_id,
                array_to_string(array_agg(doctor.name), ' / ') as names
            from nh_clinical_spell spell
            inner join con_doctor_spell_rel
                on con_doctor_spell_rel.spell_id = spell.id
            inner join res_partner doctor
                on con_doctor_spell_rel.doctor_id = doctor.id
            group by spell.id
);

create materialized view
param as(
        select
            activity.spell_id,
            height.height,
            diabetes.status as diabetes,
            mrsa.status as mrsa,
            pc.status,
            o2target_level.id as o2target_level_id,
            ps.status as post_surgery,
            psactivity.date_terminated as post_surgery_date,
            cc.status as critical_care,
            ccactivity.date_terminated as critical_care_date,
            uotarget.volume as uotarget_vol,
            uotarget.unit as uotarget_unit
        from wb_activity_latest activity
        left join nh_clinical_patient_observation_height height
            on activity.ids && array[height.activity_id]
        left join nh_clinical_patient_diabetes diabetes
            on activity.ids && array[diabetes.activity_id]
        left join nh_clinical_patient_o2target o2target
            on activity.ids && array[o2target.activity_id]
        left join nh_clinical_o2level o2target_level
            on o2target_level.id = o2target.level_id
        left join nh_clinical_patient_mrsa mrsa
            on activity.ids && array[mrsa.activity_id]
        left join nh_clinical_patient_palliative_care pc
            on activity.ids && array[pc.activity_id]
        left join nh_clinical_patient_post_surgery ps
            on activity.ids && array[ps.activity_id]
        left join nh_clinical_patient_uotarget uotarget
            on activity.ids && array[uotarget.activity_id]
        left join nh_activity psactivity on psactivity.id = ps.activity_id
        left join nh_clinical_patient_critical_care cc
            on activity.ids && array[cc.activity_id]
        left join nh_activity ccactivity on ccactivity.id = cc.activity_id
        where activity.state = 'completed'
);

create materialized view
pbp as(
    select
        activity.spell_id,
        pbp.status
    from wb_activity_latest activity
    left join nh_clinical_patient_pbp_monitoring pbp
        on activity.ids && array[pbp.activity_id]
    where activity.state = 'completed'
);

create or replace view last_movement_users as(
    select
        spell.id as spell_id,
        array_agg(distinct users.id) as user_ids,
        array_agg(distinct users2.id) as ward_user_ids
    from nh_clinical_spell spell
    inner join wb_activity_ranked activity
        on activity.id = spell.activity_id and activity.rank = 1
    inner join wb_activity_ranked move
        on move.parent_id = activity.id and move.rank = 1
        and move.state = 'completed'
        and move.data_model = 'nh.clinical.patient.move'
    inner join nh_clinical_patient_move move_data
        on move_data.activity_id = move.id
    inner join nh_clinical_location location
        on location.id = move_data.from_location_id
    inner join ward_locations wl on wl.id = location.id
    left join user_location_rel ulrel on ulrel.location_id = location.id
    left join res_users users on users.id = ulrel.user_id
    left join user_location_rel ulrel2 on ulrel2.location_id = wl.ward_id
    left join res_users users2 on users2.id = ulrel2.user_id
    where now() at time zone 'UTC' - move.date_terminated < interval '1d'
    group by spell.id
);

create or replace view last_discharge_users as({last_discharge_users});

create or replace view last_transfer_users as({last_transfer_users});

create or replace view
nh_clinical_wardboard as({wardboard});
""".format(last_discharge_users=last_discharge_users,
           last_transfer_users=last_transfer_users,
           wardboard=wardboard,
           wb_transfer_ranked=wb_transfer_ranked))
