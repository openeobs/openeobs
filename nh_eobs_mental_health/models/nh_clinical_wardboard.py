from openerp.osv import orm


class NHClinicalWardboard(orm.Model):

    _name = 'nh.clinical.wardboard'
    _inherit = 'nh.clinical.wardboard'

    def toggle_obs_stop(self, cr, uid, ids, context=None):
        escalation_tasks_open_warning = 'Warning! One or more escalation ' \
                                        'tasks for <patient_name> are not ' \
                                        'completed.'
        pass

    def spell_has_open_escalation_tasks(self, cr, uid, spell_id, context=None):
        """
        Check to see if spell has any open escalation tasks
        :param cr: Odoo cursor
        :param uid: User carrying out operation
        :param spell_id: IDs of the spell
        :return: True if open tasks, False if not
        """
        if isinstance(spell_id, list):
            spell_id = spell_id[0]
        activity_model = self.pool['nh.activity']
        spell_model = self.pool['nh.clinical.spell']
        spell = spell_model.read(
            cr, uid, spell_id, ['activity_id'], context=context)
        if spell:
            spell_activity_id = spell.get('activity_id')
            escalation_task_domain = [
                ['data_model', 'like', 'nh.clinical.notification.%'],
                ['state', 'not in', ['completed', 'cancelled']],
                ['spell_activity_id', '=', spell_activity_id]
            ]
            return any(activity_model.search(
                cr, uid, escalation_task_domain, context=context))
        else:
            raise ValueError('Could not locate patient spell')

