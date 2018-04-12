import copy

from openerp import api
from openerp.addons.nh_eobs import helpers, exceptions
from openerp.addons.nh_eobs_api.routing import ResponseJSON
from openerp.osv import orm, fields


class NHClinicalWardboard(orm.Model):

    _name = 'nh.clinical.wardboard'
    _inherit = 'nh.clinical.wardboard'

    def _get_obs_stop_from_spell(self, cr, uid, ids, field_name, arg,
                                 context=None):
        """
        Function field to return obs_stop flag from spell
        :param cr: Odoo cursor
        :param uid: User ID of user doing operation
        :param ids: Ids to read
        :param field_name: name of field
        :param arg: arguments
        :param context: Odoo context
        :return: obs_stop flag from spell
        """
        spell_model = self.pool['nh.clinical.spell']
        flags = spell_model.read(cr, uid, ids, ['obs_stop'], context=context)
        return dict([(rec.get('id'), rec.get('obs_stop')) for rec in flags])

    def _get_rapid_tranq_from_spell(
            self, cr, uid, ids, field_name, arg, context=None):
        """
        Function field to return rapid_tranq from spell

        :param cr: Odoo cursor
        :param uid: User ID of user doing operation
        :param ids: Ids to read
        :param field_name: name of field
        :param arg: arguments
        :param context: Odoo context
        :return: rapid_tranq flag from spell
        """
        spell_model = self.pool['nh.clinical.spell']
        flags = spell_model.read(
            cr, uid, ids, ['rapid_tranq'], context=context)
        return dict([(rec.get('id'), rec.get('rapid_tranq')) for rec in flags])

    acuity_selection = [
        ('NoScore', 'New Pt / Obs Restart'),
        ('High', 'High Risk'),
        ('Medium', 'Medium Risk'),
        ('Low', 'Low Risk'),
        ('None', 'No Risk'),
        ('ObsStop', 'Obs Stop'),
        ('Refused', 'Refused')
    ]

    _columns = {
        'obs_stop': fields.function(_get_obs_stop_from_spell, type='boolean'),
        'acuity_index': fields.text('Index on Acuity Board'),
        'rapid_tranq': fields.function(
            _get_rapid_tranq_from_spell, type='boolean', store=True)
    }

    _order = 'rapid_tranq desc, location asc'

    @api.multi
    def toggle_obs_stop(self):
        """
        Handle button press on 'Stop Observations'/'Restore Observation' button

        :return: True
        """
        spell = self.spell_activity_id.data_ref
        if not spell.id:
            raise ValueError('No spell found for patient')
        if spell.obs_stop:
            self.end_obs_stop()
        else:
            return self.prompt_user_for_obs_stop_reason()

    @api.multi
    def prompt_user_for_obs_stop_reason(self):
        """
        Returns an action to the front-end that instructs it to open another
        view in which the user can select a reason for observations to be
        stopped.
        :return: An action that opens another view.
        :rtype: dict
        """
        wizard_model = \
            self.env['nh.clinical.patient_monitoring_exception.select_reason']
        patient_name = self.patient_id.given_name + ' ' + \
            self.patient_id.family_name
        wizard = wizard_model.create({
            'spell_has_open_escalation_tasks':
                self.spell_has_open_escalation_tasks(
                    self.spell_activity_id.id),
            'patient_name': patient_name
        })

        view_id = self.env['ir.model.data'].get_object_reference(
            'nh_eobs_mental_health', 'view_select_obs_stop_reason'
        )[1]

        # Very important, data is needed later in
        # nh.clinical.patient_monitoring_exception.select_reason's
        # start_patient_monitoring_exception() method.
        self = self.with_context(
            spell_id=self.spell_activity_id.data_ref.id,
            spell_activity_id=self.spell_activity_id.id
        )
        return {
            'name': "Patient Observation Status Change",
            'type': 'ir.actions.act_window',
            'res_model':
                'nh.clinical.patient_monitoring_exception.select_reason',
            'res_id': wizard.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self.env.context,
            'view_id': view_id
        }

    @api.multi
    def open_set_therapeutic_obs_level_view(self):
        return {
            'name': 'Set Therapeutic Obs Level',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.patient.observation.therapeutic.level',
            'view_mode': 'form',
            'target': 'new',
            'flags': {'form': {'action_buttons': True}}
        }

    @helpers.v8_refresh_materialized_views('ews0', 'ews1', 'ews2')
    @api.multi
    def start_obs_stop(self, reasons, spell_id, spell_activity_id):
        """
        Creates a new patient monitoring exception with the passed reason.

        Creates an activity with a reference to the monitoring exception, save
        the 'spell activity id' on the activity, and start it. It is difficult
        to retrieve the monitoring exception activity later to complete it if
        the spell activity id is not set.

        Toggles the 'obs stop' flag on the spell to True as there is now a
        patient monitoring exception in effect.
        """
        if len(reasons) == 0:
            raise ValueError(
                "No reasons were selected. A patient monitoring exception "
                "cannot be created without a reason."
            )
        elif len(reasons) > 1:
            raise ValueError(
                "More than one reason was selected. "
                "There should only be one reason per patient monitoring "
                "exception."
            )

        obs_stop_model = self.env['nh.clinical.pme.obs_stop']
        selected_reason_id = reasons[0].id
        activity_id = obs_stop_model.create_activity(
            {
                'parent_id': spell_activity_id
            },
            {
                'reason': selected_reason_id,
                'spell': spell_id
            }
        )
        activity_model = self.env['nh.activity']
        activity = activity_model.browse(activity_id)
        # last_finished_obs_stop view returns nothing without this.
        activity.spell_activity_id = spell_activity_id
        obs_stop = activity.data_ref
        obs_stop.start(activity_id)

    @helpers.v8_refresh_materialized_views('ews0', 'ews1', 'ews2')
    @api.multi
    def end_obs_stop(self, cancellation=False):
        """
        Completes the patient monitoring exception activity and toggles the
        'obs stop' flag on the spell to False as there are no longer any
        patient monitoring exceptions in effect.
        """
        obs_stop_model = self.env['nh.clinical.pme.obs_stop']
        spell_activity = self.spell_activity_id
        activities = \
            obs_stop_model.get_activities_by_spell_activity(spell_activity)
        activity = activities[-1]
        obs_stop = activity.data_ref

        if cancellation:
            obs_stop.cancel(activity.id)
        else:
            obs_stop.complete(activity.id)

    @api.multi
    def set_rapid_tranq(self, value):
        """
        Set the `rapid_tranq` field of the patient's spell to the passed value.

        :param value: The new value for the `rapid_tranq` field.
        :rtype: bool or dict
        :return:
        """
        if isinstance(value, dict):
            value = value.get('value')  # Context passed from Odoo view.
        if value is None:
            raise ValueError("No value argument passed to be set on the rapid "
                             "tranq field.")
        if not isinstance(value, bool):
            raise TypeError("Value is not a boolean.")

        rapid_tranq_model = self.env['nh.clinical.pme.rapid_tranq']
        spell_activity = self.spell_activity_id
        spell = spell_activity.data_ref

        check_response = rapid_tranq_model.check_set_rapid_tranq(
            value, spell)

        if check_response['status'] == ResponseJSON.STATUS_SUCCESS:
            # Will create a rapid tranq record.
            rapid_tranq_model.toggle_rapid_tranq(spell_activity)

        elif check_response['status'] == ResponseJSON.STATUS_FAIL:
            raise exceptions.StaleDataException(check_response['description'],
                                                check_response['title'])
        else:
            raise ValueError("Unexpected status returned from set rapid tranq "
                             "check.")

    def spell_has_open_escalation_tasks(self, cr, uid, spell_activity_id,
                                        context=None):
        """
        Check to see if spell has any open escalation tasks.

        :param cr: Odoo cursor
        :param uid: User carrying out operation
        :param spell_activity_id: IDs of the spell
        :param context: Odoo context
        :return: True if open tasks, False if not
        """
        activity_model = self.pool['nh.activity']
        escalation_task_domain = [
            ['data_model', 'like', 'nh.clinical.notification.%'],
            ['state', 'not in', ['completed', 'cancelled']],
            ['spell_activity_id', '=', spell_activity_id]
        ]
        return any(activity_model.search(
            cr, uid, escalation_task_domain, context=context))

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
        Override nh_eobs.wardboard.fields_view_get to change next_diff to
        'Observations Stopped' if obs_stop flag set on patient spell
        :param cr: Odoo Cursor
        :param uid: ID of user performing action
        :param view_id: XML_ID of view
        :param view_type: Type of view (form, kanban etc)
        :param context: Odoo context
        :param toolbar: If has toolbar or not
        :param submenu: Submenu
        :return: ui.ir.view for rendering on frontend
        """
        res = super(NHClinicalWardboard, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        return res

    def read(self, cr, user, ids, fields=None, context=None,
             load='_classic_read'):
        """
        Override of read method of wardboard to override next_diff and
        frequency fields with obs_stop information is flag set
        :param cr: Odoo cursor
        :param user: User doing operation
        :param ids: Record IDs to read
        :param fields: Fields to read from records
        :param context: Odoo context
        :param load: Type of loading to do
        :return: list of dicts or objects
        """
        res = super(NHClinicalWardboard, self).read(
            cr, user, ids, fields, context=context, load=load)
        was_single_record = False
        if not isinstance(res, list):
            was_single_record = True
            res = [res]
        for rec in res:
            spell_model = self.pool['nh.clinical.spell']
            patient_id = rec.get('patient_id')
            if isinstance(patient_id, tuple):
                patient_id = patient_id[0]
            spell_id = spell_model.search(cr, user, [
                ['patient_id', '=', patient_id],
                ['state', 'not in', ['completed', 'cancelled']]
            ], context=context)
            if spell_id:
                spell_id = spell_id[0]
                spell = spell_model.read(
                    cr, user, spell_id, [
                        'obs_stop',
                        'rapid_tranq',
                        'refusing_obs'
                    ],
                    context=context)
                rec['rapid_tranq'] = spell.get('rapid_tranq')
                if spell.get('obs_stop'):
                    obs_stop_model = self.pool['nh.clinical.pme.obs_stop']
                    obs_stops = obs_stop_model.search(cr, user, [
                        ['spell', '=', spell_id]
                    ], context=context)
                    if obs_stops:
                        obs_stop = obs_stops[0]
                        reason = obs_stop_model.read(
                            cr, user, obs_stop, ['reason'], context=context)
                        rec['frequency'] = reason.get('reason', [0, False])[1]
                    rec['next_diff'] = 'Observations Stopped'
                elif spell.get('refusing_obs'):
                    rec['frequency'] = 'Refused - {0}'.format(rec['frequency'])
                    rec['next_diff'] = 'Refused - {0}'.format(rec['next_diff'])
        if was_single_record:
            return res[0]
        return res

    # Acuity Board grouping
    @api.model
    def _get_acuity_groups(self, ids, domain, read_group_order=None,
                           access_rights_uid=None,):
        """
        Override _get_cr_groups to include obs_stop and new patient
        / restarted observations - EOBS-404

        :param ids: record ids
        :param domain: Domain to filter groups with
        :param read_group_order: Order to read the groups in
        :param access_rights_uid: User ID to use for access rights
        :returns: Tuple of groups and folded states
        """
        group_list = copy.deepcopy(self.acuity_selection)
        fold_dict = {group[0]: group[0] not in ids for group in group_list}
        return group_list, fold_dict

    _group_by_full = {
        'acuity_index': _get_acuity_groups
    }

    def init(self, cr):
        """
        Override the init function to add the new get_last_finished_obs_stop
        SQL view.

        :param cr: Odoo Cursor
        """
        settings_pool = self.pool['nh.clinical.settings']
        nh_eobs_sql = self.pool['nh.clinical.sql']
        dt_period = \
            settings_pool.get_setting(cr, 1, 'discharge_transfer_period')
        cr.execute("""
        CREATE OR REPLACE VIEW last_finished_obs_stop AS ({last_obs_stop});
        CREATE OR REPLACE VIEW ews_activities AS ({ews_activities});
        CREATE OR REPLACE VIEW refused_ews_activities AS ({refused_ews});
        """.format(
            last_obs_stop=nh_eobs_sql.get_last_finished_obs_stop(),
            ews_activities=nh_eobs_sql.get_ews_activities(),
            refused_ews=nh_eobs_sql.get_refused_ews_activities()
        ))
        super(NHClinicalWardboard, self).init(cr)
        cr.execute("""
        CREATE OR REPLACE VIEW refused_last_ews AS ({refused_last_ews});
        CREATE OR REPLACE VIEW nh_clinical_wardboard AS ({refused_wardboard});
        """.format(
            refused_last_ews=nh_eobs_sql.get_refused_last_ews(),
            refused_wardboard=nh_eobs_sql.get_refused_wardboard(
                '{0}d'.format(dt_period))
        ))
