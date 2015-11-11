# -*- coding: utf-8 -*-
"""
`parameters.py` defines the blood pressure monitoring parameter which
is directly related to the postural blood pressure observation.
"""
from openerp.osv import orm, fields
import logging
from openerp import SUPERUSER_ID
from datetime import datetime as dt
_logger = logging.getLogger(__name__)


class nh_clinical_patient_pbp_monitoring(orm.Model):
    """
    Represents the action of setting the
    :class:`patient<base.nh_clinical_patient>` blood pressure monitoring
    status to `yes` or `no`. This would mainly depend on hospital policy
    and the medical staff assessment.

    This parameter is directly related to the
    :mod:`postural blood pressure<pbp.nh_clinical_patient_observation_pbp>`
    observation.
    """
    _name = 'nh.clinical.patient.pbp_monitoring'
    _inherit = ['nh.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['pbp_monitoring'], context=context):
            result[r['id']] = 'On' if r['pbp_monitoring'] else 'Off'
        return result

    _columns = {
        'pbp_monitoring': fields.boolean('Postural Blood Presssure Monitoring', required=True),
        'value': fields.function(_get_value, type='char', size=3, string='String Value'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        pbp_pool = self.pool['nh.clinical.patient.observation.pbp']
        if activity.data_ref.pbp_monitoring:
            activity_pool.cancel_open_activities(cr, uid, activity.parent_id.id, pbp_pool._name, context=context)
            pbp_activity_id = pbp_pool.create_activity(cr, SUPERUSER_ID,
                                 {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                                 {'patient_id': activity.data_ref.patient_id.id})
            date_schedule = dt.now().replace(minute=0, second=0, microsecond=0)
            activity_pool.schedule(cr, SUPERUSER_ID, pbp_activity_id, date_schedule, context=context)

        return super(nh_clinical_patient_pbp_monitoring, self).complete(cr, uid, activity_id, context=context)