from openerp.osv import orm, osv, fields


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

    def prompt_user_for_obs_stop_reason(self, cr, uid, ids, context=None):
        """
        Returns an action to the front-end that instructs it to open another
        view in which the user can select a reason for observations to be
        stopped.
        :return: An action that opens another view.
        :rtype: dict
        """
        # patient_monitoring_exception_model = \
        #     self.pool['nh.clinical.patient_monitoring_exception']
        # res_id = self.pool['ir.model.data'].get_object_reference(
        #     cr, uid, 'nh_eobs', 'acute_hospital_ed'
        # )[1]
        display_model = self.pool[
            'nh.clinical.patient_monitoring_exception_reason_display_model']
        display_model_id = display_model.create(cr, uid, context=context)
        view_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'nh_eobs_mental_health', 'view_select_obs_stop_reason'
        )[1]
        return {
            'name': "Patient Observation Status Change",
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.patient_monitoring_exception_reason',
            'res_id': display_model_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context,
            'view_id': view_id
        }

    def toggle_obs_stop(self, cr, uid, ids, context=None):
        """
        Handle button press on 'Stop Observations'/'Restore Observation' button
        :param cr: Odoo cursor
        :param uid: User doing the action
        :param ids: IDs of wardboard
        :param context: Odoo context
        :return: True
        """
        spell_model = self.pool['nh.clinical.spell']
        if isinstance(ids, list):
            ids = ids[0]
        wardboard_obj = self.read(cr, uid, ids, context=context)
        escalation_tasks_open_warning = 'One or more escalation tasks for ' \
                                        '{0} are not completed.'
        spell_activity_id = wardboard_obj.get('spell_activity_id')[0]
        patient = wardboard_obj.get('patient_id')
        patient_name = patient[1]
        spell_id = spell_model.search(
            cr, uid, [['patient_id', '=', patient[0]]])
        if not spell_id:
            raise ValueError('No spell found for patient')
        obs_stop = \
            self.toggle_obs_stop_flag(cr, uid, spell_id[0], context=context)
        if obs_stop:
            if not self.cancel_open_ews(
                    cr, uid, spell_activity_id, context=context):
                raise osv.except_osv(
                    'Error', 'There was an issue cancelling '
                             'all open NEWS activities'
                )
        # else:
        #     # Restart obs
        if self.spell_has_open_escalation_tasks(cr, uid, spell_activity_id,
                                                context=context):
            raise osv.except_osv(
                'Warning!',
                escalation_tasks_open_warning.format(patient_name))
        else:
            return True

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
        spell_model.write(cr, uid, spell_id, {'obs_stop': not obs_stop})
        return not obs_stop

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

    def cancel_open_ews(self, cr, uid, spell_activity_id, context=None):
        """
        Cancel all open EWS observations
        :param cr: Odoo cursor
        :param uid: User carrying out the operation
        :param spell_activity_id: ID of the spell activity
        :param context: Odoo context
        :return: True is successful, False if not
        """
        # Cancel all open obs
        activity_model = self.pool['nh.activity']
        return activity_model.cancel_open_activities(
            cr, uid, spell_activity_id,
            model='nh.clinical.patient.observation.ews',
            context=context)
