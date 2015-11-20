# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
`nh_clinical_extension.py` extends several NH Clinical classes to add
relevant observations related functionality.
"""
from openerp.osv import orm, fields, osv
from openerp import SUPERUSER_ID
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class nh_clinical_patient(orm.Model):
    """
    Extends :class:`patient<base.nh_clinical_patient>`
    """
    _name = 'nh.clinical.patient'
    _inherit = 'nh.clinical.patient'

    def write(self, cr, uid, ids, vals, context=None):
        """
        Calls :meth:`write<openerp.models.Model.write>` and
        automatically updates the :class:`location<base.nh_clinical_location>`
        of every :mod:`observation<observations.nh_clinical_patient_observation>`
        and :mod:`notification<notifications.nh_clinical_notification>`
        related.

        :returns: ``True``
        :rtype: bool
        """
        res = super(nh_clinical_patient, self).write(cr, uid, ids, vals, context=context)
        if 'current_location_id' in vals:
            activity_pool = self.pool['nh.activity']
            patient_ids = [ids] if not isinstance(ids, list) else ids
            obs_and_not_ids = activity_pool.search(cr, uid, [['patient_id', 'in', patient_ids], ['state', 'not in', ['completed', 'cancelled']], '|', ['data_model', 'ilike', '%observation%'], ['data_model', 'ilike', '%notification%']])
            activity_pool.write(cr, uid, obs_and_not_ids, {'location_id': vals['current_location_id']}, context=context)
        return res


class nh_clinical_api_extension(orm.AbstractModel):
    """
    Extends the NH Clinical :class:`API<api.nh_clinical_api>`
    """
    _name = 'nh.clinical.api'
    _inherit = 'nh.clinical.api'

    def change_activity_frequency(self, cr, uid, patient_id, activity_type, frequency, context=None):
        """
        Creates and completes a new
        :mod:`review frequency<notifications.nh_clinical_notification_frequency>`
        task to update the frequency of the specified activity type.

        :param patient_id: :class:`patient<base.nh_clinical_patient>` id.
        :type patient_id: int
        :param activity_type: activity type ``_name`` attribute
        :type activity_type: str
        :param frequency: new frequency in minutes
        :type frequency: int
        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        spell_pool = self.pool['nh.clinical.spell']
        change_freq_pool = self.pool['nh.clinical.notification.frequency']
        domain = [
            ('patient_id', '=', patient_id),
            ('state', '=', 'completed'),
            ('data_model', '=', activity_type)
        ]
        activity_ids = activity_pool.search(cr, uid, domain, order='create_date desc, id desc', context=context)
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id, context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        if not activity_ids:
            creator_id = False
        else:
            creator_id = activity_ids[0]
        frequency_activity_id = change_freq_pool.create_activity(cr, SUPERUSER_ID, {
            'creator_id': creator_id, 'parent_id': spell.activity_id.id
        }, {
            'patient_id': patient_id,
            'observation': activity_type,
            'frequency': frequency
        })
        return activity_pool.complete(cr, uid, frequency_activity_id, context=context)

    def trigger_notifications(self, cr, uid, values, context=None):
        """
        Creates a new :mod:`notification<notifications.nh_clinical_notification>`
        for every element in the `notifications` list provided in
        ``values``::

            {
                'notifications': [{
                    'model': (str) type of notification,  //required
                    'summary': (str) notification text,  //optional
                    'groups': (list of str) user groups for which the notification is created, //required
                    'assign': (bool)  //assign the notification to the user?
                }, ...],
                'parent_id': spell type activity id,
                'creator_id': activity id triggering,
                'patient_id': patient id,
                'model': self._name,
                'group': group name of the user triggering ('hca','nurse')
            }

        :param values: contains information to create the notifications.
        :type values: dict
        """
        for n in values['notifications']:
            # notifications: [{'summary','model','groups'}]
            if values.get('group') in n['groups']:
                pool = self.pool['nh.clinical.notification.'+n['model']]
                deadline = (dt.now()+td(minutes=n.get('minutes_due'))).strftime(DTF) if n.get('minutes_due') \
                    else (dt.now()+td(minutes=5)).strftime(DTF)
                a_values = {
                    'user_id': uid if n.get('assign') else False,
                    'assign_locked': n.get('assign'),
                    'parent_id': values.get('parent_id'),
                    'date_deadline': deadline,
                    'creator_id': values.get('creator_id'),
                }
                if n.get('summary'):
                    a_values.update({'summary': n['summary']})
                d_values = {
                    'patient_id': values.get('patient_id')
                }
                if n['model'] == 'frequency':
                    activity_pool = self.pool['nh.activity']
                    domain = [
                        ('patient_id', '=', values.get('patient_id')),
                        ('state', 'not in', ['completed', 'cancelled']),
                        ('data_model', '=', 'nh.clinical.notification.frequency')]
                    frequency_activity_ids = activity_pool.search(cr, uid, domain, context=context)
                    for f in activity_pool.browse(cr, uid, frequency_activity_ids, context=context):
                        if f.data_ref.observation == values.get('model'):
                            activity_pool.cancel(cr, uid, f.id, context=context)
                    d_values.update({'observation': values.get('model')})
                pool.create_activity(cr, SUPERUSER_ID, a_values, d_values, context=context)

    def cancel_open_activities(self, cr, uid, parent_id, model, context=None):
        """
        Cancels all not `completed` or `cancelled` activities of the
        provided type and :class:`spell<base.nh_clinical_spell>`.

        :param parent_id: :class:`activity<activity.nh_activity>` id of `nh.clinical.spell` type.
        :type parent_id: int
        :param model: activity type ``_name`` attribute.
        :type model: str
        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        domain = [('parent_id', '=', parent_id),
                  ('data_model', '=', model),
                  ('state', 'not in', ['completed', 'cancelled'])]
        open_activity_ids = activity_pool.search(cr, uid, domain, context=context)
        return all([activity_pool.cancel(cr, uid, a, context=context) for a in open_activity_ids])