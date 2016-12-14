import copy
from datetime import datetime, timedelta

from openerp import api
from openerp.addons.nh_eobs import helpers
from openerp.osv import orm, osv, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NHClinicalWardboard(orm.Model):

    _name = 'nh.clinical.wardboard'
    _inherit = 'nh.clinical.wardboard'

    def _get_obs_stop_from_spell(self, cr, uid, ids, field_name, arg,
                                 context=None):
        """
        Function field to return obs_stop flag from spell
        :param cr: Odoo cursor
        :param uid: User ID of user doing operatoin
        :param ids: Ids to read
        :param field_name: name of field
        :param arg: arguments
        :param context: Odoo context
        :return: obs_stop flag from spell
        """
        spell_model = self.pool['nh.clinical.spell']
        flags = spell_model.read(cr, uid, ids, ['obs_stop'], context=context)
        return dict([(rec.get('id'), rec.get('obs_stop')) for rec in flags])

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
        'acuity_index': fields.text('Index on Acuity Board')
    }

    @api.multi
    def toggle_obs_stop(self):
        """
        Handle button press on 'Stop Observations'/'Restore Observation' button
        :param cr: Odoo cursor
        :param uid: User doing the action
        :param ids: IDs of wardboard
        :param context: Odoo context
        :return: True
        """
        spell = self.spell_activity_id.data_ref
        if not spell.id:
            raise ValueError('No spell found for patient')
        if spell.obs_stop:
            self.end_patient_monitoring_exception()
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
        # nh.clinical.patient_monitoring_exception's
        # create_patient_monitoring_exception() method.
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

    @helpers.v8_refresh_materialized_views('ews0', 'ews1', 'ews2')
    @api.multi
    def start_patient_monitoring_exception(self, reasons, spell_id,
                                           spell_activity_id):
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

        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        selected_reason_id = reasons[0].id
        activity_id = pme_model.create_activity(
            {'parent_id': spell_activity_id},
            {'reason': selected_reason_id, 'spell': spell_id}
        )
        activity_model = self.env['nh.activity']
        pme_activity = activity_model.browse(activity_id)
        pme_activity.spell_activity_id = spell_activity_id
        pme_model.start(activity_id)

        cancel_reason_pme = \
            self.env['ir.model.data'].get_object(
                'nh_eobs', 'cancel_reason_patient_monitoring_exception'
            )

        cancel_open_ews = self.cancel_open_ews(spell_activity_id,
                                               cancel_reason_pme.id)

        if not cancel_open_ews:
            raise osv.except_osv(
                'Error', 'There was an issue cancelling '
                         'all open NEWS activities'
            )

        self.set_obs_stop_flag(spell_id, True)

    @helpers.v8_refresh_materialized_views('ews0', 'ews1', 'ews2')
    @api.multi
    def end_patient_monitoring_exception(self, cancellation=False):
        """
        Completes the patient monitoring exception activity and toggles the
        'obs stop' flag on the spell to False as there are no longer any
        patient monitoring exceptions in effect.
        """
        activity_model = self.env['nh.activity']
        activity_pool = self.pool['nh.activity']
        ir_model_data_model = self.env['ir.model.data']

        spell_id = self.spell_activity_id.data_ref.id
        patient_monitoring_exception_activity = activity_model.search([
            ('data_model', '=', 'nh.clinical.patient_monitoring_exception'),
            ('spell_activity_id', '=', self.spell_activity_id.id),
            ('state', 'not in', ['completed', 'cancelled'])
        ])
        if len(patient_monitoring_exception_activity) > 1:
            raise ValueError(
                "Only one monitoring exception per patient is expected, there "
                "is no way to know which monitoring exception the toggle "
                "intends to end."
            )

        patient_monitoring_exception_activity_id = \
            patient_monitoring_exception_activity.id

        if cancellation:
            cancel_reason = ir_model_data_model.get_object(
                'nh_eobs', 'cancel_reason_transfer'
            )
            activity_pool.cancel_with_reason(
                self.env.cr, self.env.uid,
                patient_monitoring_exception_activity.id,
                cancel_reason.id
            )
        else:
            activity_pool.complete(
                self.env.cr, self.env.uid,
                patient_monitoring_exception_activity_id
            )

        self.set_obs_stop_flag(spell_id, False)
        self.create_new_ews(patient_monitoring_exception_activity_id)

    def set_obs_stop_flag(self, cr, uid, spell_id, value, context=None):
        """
        Toggle the obs_stop flag on the spell object
        :param cr: Odoo cursor
        :param uid: User doing the action
        :param spell_id: spell to toggle
        :param context: context
        :return: True
        """
        spell_model = self.pool['nh.clinical.spell']
        return spell_model.write(cr, uid, spell_id, {'obs_stop': value})

    def spell_has_open_escalation_tasks(self, cr, uid, spell_activity_id,
                                        context=None):
        """
        Check to see if spell has any open escalation tasks
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

    @api.multi
    def create_new_ews(self, ended_patient_monitoring_exception_id):
        """
        Create a new EWS task an hour in the future. Used when patient is
        take off obs_stop.

        :return: ID of created EWS
        """
        ews_model = self.env['nh.clinical.patient.observation.ews']
        activity_model = self.env['nh.activity']
        api_model = self.env['nh.clinical.api']

        new_ews_id = ews_model.create_activity(
            {'parent_id': self.spell_activity_id.id,
             'creator_id': ended_patient_monitoring_exception_id},
            {'patient_id': self.patient_id.id}
        )
        one_hour_time = datetime.now() + timedelta(hours=1)
        one_hour_time_str = one_hour_time.strftime(DTF)

        self.force_v7_api(activity_model)

        activity_model.schedule(self.env.cr, self.env.uid, new_ews_id,
                                date_scheduled=one_hour_time_str)
        api_model.change_activity_frequency(
            self.patient_id.id, 'nh.clinical.patient.observation.ews', 60)
        return new_ews_id

    @api.model
    def cancel_open_ews(self, spell_activity_id, cancel_reason_id=None):
        """
        Cancel all open EWS observations
        :param cr: Odoo cursor
        :param uid: User carrying out the operation
        :param spell_activity_id: ID of the spell activity
        :param context: Odoo context
        :return: True is successful, False if not
        """
        # Cancel all open obs
        activity_model = self.env['nh.activity']
        return activity_model.cancel_open_activities(
            spell_activity_id,
            model='nh.clinical.patient.observation.ews',
            cancel_reason_id=cancel_reason_id
        )

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
                spell = spell_model.read(cr, user, spell_id, ['obs_stop'],
                                         context=context)
                if spell.get('obs_stop'):
                    pme_model = self.pool[
                        'nh.clinical.patient_monitoring_exception']
                    obs_stops = pme_model.search(cr, user, [
                        ['spell', '=', spell_id]
                    ], context=context)
                    if obs_stops:
                        obs_stop = obs_stops[0]
                        reason = pme_model.read(
                            cr, user, obs_stop, ['reason'], context=context)
                        rec['frequency'] = reason.get('reason', [0, False])[1]
                    rec['next_diff'] = 'Observations Stopped'
                elif rec.get('acuity_index') == 'Refused':
                    rec['frequency'] = 'Refused - {0}'.format(rec['frequency'])
                    rec['next_diff'] = 'Refused - {0}'.format(rec['next_diff'])
        if was_single_record:
            return res[0]
        return res

    # TODO Refactor the activity method decorator and remove this method.
    @classmethod
    def force_v7_api(cls, obj):
        """
        Trick Odoo into thinking this is a 7.0 ORM API style method before
        the `complete` method is called on the activity. I believe there may
        be a problem in the decorator that is used on all activity data methods
        which specifically looks for all args.
        :param obj:
        :return:
        """
        if '_ids' in obj.__dict__:
            obj.__dict__.pop('_ids')

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
        fold_dict = {group[0]: False for group in group_list}
        return group_list, fold_dict

    _group_by_full = {
        'acuity_index': _get_acuity_groups
    }

    def init(self, cr):
        """
        Override the init function to add the new get_last_finished_pme SQL
        view

        :param cr: Odoo Cursor
        """
        settings_pool = self.pool['nh.clinical.settings']
        nh_eobs_sql = self.pool['nh.clinical.sql']
        dt_period = \
            settings_pool.get_setting(cr, 1, 'discharge_transfer_period')
        cr.execute("""
        CREATE OR REPLACE VIEW last_finished_pme AS ({last_pme});
        CREATE OR REPLACE VIEW ews_activities AS ({ews_activities});
        CREATE OR REPLACE VIEW refused_ews_activities AS ({refused_ews});
        """.format(
            last_pme=nh_eobs_sql.get_last_finished_pme(),
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
