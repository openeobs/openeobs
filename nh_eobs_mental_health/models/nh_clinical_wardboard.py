from openerp.osv import orm, fields
from openerp import api


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

    _columns = {
        'obs_stop': fields.function(_get_obs_stop_from_spell, type='boolean')
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
        if len(reasons) > 1:
            raise ValueError(
                "More than one reason was selected. "
                "There should only be one reason per patient monitoring "
                "exception."
            )

        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        selected_reason_id = reasons[0].id
        activity_id = pme_model.create_activity(
            {},
            {'reason': selected_reason_id, 'spell': spell_id}
        )
        activity_model = self.env['nh.activity']
        pme_activity = activity_model.browse(activity_id)
        pme_activity.spell_activity_id = spell_activity_id
        pme_model.start(activity_id)

        wardboard_model = self.env['nh.clinical.wardboard']
        wardboard_model.toggle_obs_stop_flag(spell_id)

    @api.multi
    def end_patient_monitoring_exception(self):
        """
        Completes the patient monitoring exception activity and toggles the
        'obs stop' flag on the spell to False as there are no longer any
        patient monitoring exceptions in effect.
        """
        activity_model = self.env['nh.activity']

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

        # The 2 lines below are necessary to trick Odoo into thinking this is a
        # 7.0 ORM API style method before the `complete` method is called on
        # the activity. I believe there may be a problem in the decorator that
        # is used on all activity data methods which specifically looks for all
        # args.
        # TODO Refactor the activity method decorator.
        patient_monitoring_exception_activity_id = \
            patient_monitoring_exception_activity.id
        patient_monitoring_exception_activity.__dict__.pop('_ids')

        patient_monitoring_exception_activity.complete(
            self.env.cr, self.env.uid,
            patient_monitoring_exception_activity_id
        )

        self.toggle_obs_stop_flag(spell_id)

    def toggle_obs_stop_flag(self, cr, uid, spell_id, context=None):
        """
        Toggle the obs_stop flag on the spell object
        :param cr: Odoo cursor
        :param uid: User doing the action
        :param spell_id: spell to toggle
        :param context: context
        :return: True
        """
        spell_model = self.pool['nh.clinical.spell']
        spell = spell_model.read(cr, uid, spell_id, ['obs_stop'])
        obs_stop = spell.get('obs_stop')
        return spell_model.write(cr, uid, spell_id, {'obs_stop': not obs_stop})

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

# class PatientMonitoringException(orm.TransientModel):
#
#     _name = 'nh.clinical.wardboard.exception'
#
#     def fields_view_get(self, cr, uid, view_id=None, view_type='form',
#                         context=None, toolbar=False, submenu=False):
#         result = super(PatientMonitoringException, self)\
#             .fields_view_get(
#             cr, uid, view_id, view_type, context, toolbar, submenu)
#         active_id = context.get('active_id')
#         if active_id:
#             patient_model = self.pool['nh.clinical.patient']
#             patient_name = patient_model.read(
#                 cr, uid, active_id, ['display_name']).get('display_name')
#         else:
#             patient_name = ''
#         result['arch'] = result['arch'].replace('_patient_name_',
#                                                 patient_name)
#         return result
