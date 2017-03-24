# -*- coding: utf-8 -*-
from openerp.osv import orm, fields
from openerp import SUPERUSER_ID

class nh_clinical_patient_weight_monitoring(orm.Model):
    """
    Represents the action of setting the
    :class:`patient<base.nh_clinical_patient>` weight monitoring status
    to `yes` or `no`. This would mainly depend on hospital policy and
    the medical staff assessment.

    This parameter is directly related to the
    :mod:`weight<observations.nh_clinical_patient_observation_weight>`
    observation.
    """
    _name = 'nh.clinical.patient.weight_monitoring'
    _inherit = ['nh.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['status'], context=context):
            result[r['id']] = 'Yes' if r['status'] else 'No'
        return result

    _columns = {
        'status': fields.boolean('Weight Monitoring'),
        'value': fields.function(_get_value, type='char', size=3,
                                 string='String Value'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient',
                                      required=True),
    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        weight_pool = self.pool['nh.clinical.patient.observation.weight']
        if activity.data_ref.status:
            activity_pool.cancel_open_activities(
                cr, uid, activity.parent_id.id, weight_pool._name,
                context=context)
            weight_activity_id = weight_pool.create_activity(
                cr, SUPERUSER_ID,
                {'creator_id': activity_id,
                 'parent_id': activity.parent_id.id},
                {'patient_id': activity.data_ref.patient_id.id})
            activity_pool.schedule(
                cr, SUPERUSER_ID, weight_activity_id, context=context)
        return super(nh_clinical_patient_weight_monitoring, self).complete(
            cr, uid, activity_id, context=context)
