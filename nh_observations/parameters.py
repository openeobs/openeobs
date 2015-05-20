# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
import logging
from openerp import SUPERUSER_ID
from datetime import datetime as dt
_logger = logging.getLogger(__name__)

frequencies = [
    (15, 'Every 15 Minutes'),
    (30, 'Every 30 Minutes'),
    (60, 'Every Hour'),
    (120, 'Every 2 Hours'),
    (240, 'Every 4 Hours'),
    (360, 'Every 6 Hours'),
    (720, 'Every 12 Hours'),
    (1440, 'Every Day')
]


class nh_clinical_patient_mrsa(orm.Model):
    _name = 'nh.clinical.patient.mrsa'
    _inherit = ['nh.activity.data'] 
    _columns = {
        'mrsa': fields.boolean('MRSA', required=True),                
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }


class nh_clinical_patient_diabetes(orm.Model):
    _name = 'nh.clinical.patient.diabetes'
    _inherit = ['nh.activity.data'] 
    _columns = {
        'diabetes': fields.boolean('Diabetes', required=True),                
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }


class nh_clinical_patient_palliative_care(orm.Model):
    _name = 'nh.clinical.patient.palliative_care'
    _inherit = ['nh.activity.data']
    _columns = {
        'status': fields.boolean('On Palliative Care?', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        if activity.data_ref.status:
            activity_ids = activity_pool.search(cr, uid, [['patient_id', '=', activity.data_ref.patient_id.id],
                                                          ['state', 'not in', ['completed', 'cancelled']],
                                                          '|', ['data_model', 'ilike', '%observation%'],
                                                          ['data_model', 'ilike', '%notification%']], context=context)
            [activity_pool.cancel(cr, uid, aid, context=context) for aid in activity_ids]
        return super(nh_clinical_patient_palliative_care, self).complete(cr, uid, activity_id, context=context)


class nh_clinical_patient_weight_monitoring(orm.Model):
    _name = 'nh.clinical.patient.weight_monitoring'
    _inherit = ['nh.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['weight_monitoring'], context=context):
            result[r['id']] = 'On' if r['weight_monitoring'] else 'Off'
        return result

    _columns = {
        'weight_monitoring': fields.boolean('Postural Blood Presssure Monitoring', required=True),
        'value': fields.function(_get_value, type='char', size=3, string='String Value'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']
        weight_pool = self.pool['nh.clinical.patient.observation.weight']
        if activity.data_ref.weight_monitoring:
            api_pool.cancel_open_activities(cr, uid, activity.parent_id.id, weight_pool._name, context=context)
            weight_activity_id = weight_pool.create_activity(cr, SUPERUSER_ID,
                                 {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                                 {'patient_id': activity.data_ref.patient_id.id})
            date_schedule = dt.now().replace(minute=0, second=0, microsecond=0)
            activity_pool.schedule(cr, SUPERUSER_ID, weight_activity_id, date_schedule, context=context)

        return super(nh_clinical_patient_weight_monitoring, self).complete(cr, uid, activity_id, context=context)