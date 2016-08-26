from openerp.osv import orm, osv


class NHClinicalWardboard(orm.Model):

    _name = 'nh.clinical.wardboard'
    _inherit = 'nh.clinical.wardboard'

    def toggle_obs_stop(self, cr, uid, ids, context=None):
        if isinstance(ids, list):
            ids = ids[0]
        wardboard_obj = self.read(cr, uid, ids, context=context)
        escalation_tasks_open_warning = 'One or more escalation tasks for ' \
                                        '{0} are not completed.'
        spell_activity_id = wardboard_obj.get('spell_activity_id')[0]
        patient_name = wardboard_obj.get('patient_id')[1]
        if self.spell_has_open_escalation_tasks(cr, uid, spell_activity_id,
                                                context=context):
            raise osv.except_osv(
                'Warning!',
                escalation_tasks_open_warning.format(patient_name))
        pass

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
