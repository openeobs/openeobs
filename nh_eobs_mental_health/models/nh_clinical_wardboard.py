from openerp.osv import orm, osv


class NHClinicalWardboard(orm.Model):

    _name = 'nh.clinical.wardboard'
    _inherit = 'nh.clinical.wardboard'

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
        self.toggle_obs_stop_flag(cr, uid, spell_id[0], context=context)
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
