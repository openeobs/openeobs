# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
import logging
from openerp import SUPERUSER_ID
from datetime import datetime as dt, timedelta as td
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


class t4_clinical_o2level(orm.Model):
    _name = 't4.clinical.o2level'

    def _get_name(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['max', 'min'], context=context):
            result[r['id']] = str(r['min']) + '-' + str(r['max'])
        return result

    _columns = {
        'name': fields.function(_get_name, 'O2 Target', type='char', size=10),
        'min': fields.integer("Min"),
        'max': fields.integer("Max"),               
    }


class t4_clinical_patient_o2target(orm.Model):
    _name = 't4.clinical.patient.o2target'
    _inherit = ['t4.activity.data']       
    _rec_name = 'level_id'
    _columns = {
        'level_id': fields.many2one('t4.clinical.o2level', 'O2 Level', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }


class t4_clinical_patient_mrsa(orm.Model):
    _name = 't4.clinical.patient.mrsa'
    _inherit = ['t4.activity.data'] 
    _columns = {
        'mrsa': fields.boolean('MRSA', required=True),                
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }


class t4_clinical_patient_diabetes(orm.Model):
    _name = 't4.clinical.patient.diabetes'
    _inherit = ['t4.activity.data'] 
    _columns = {
        'diabetes': fields.boolean('Diabetes', required=True),                
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }


class t4_clinical_patient_pbp_monitoring(orm.Model):
    _name = 't4.clinical.patient.pbp_monitoring'
    _inherit = ['t4.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['pbp_monitoring'], context=context):
            result[r['id']] = 'On' if r['pbp_monitoring'] else 'Off'
        return result

    _columns = {
        'pbp_monitoring': fields.boolean('Postural Blood Presssure Monitoring', required=True),
        'value': fields.function(_get_value, type='char', size=3, string='String Value'),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['t4.clinical.api']
        pbp_pool = self.pool['t4.clinical.patient.observation.pbp']
        if activity.data_ref.pbp_monitoring:
            api_pool.cancel_open_activities(cr, uid, activity.parent_id.id, pbp_pool._name, context=context)
            pbp_activity_id = pbp_pool.create_activity(cr, SUPERUSER_ID,
                                 {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                                 {'patient_id': activity.data_ref.patient_id.id})
            date_schedule = dt.now().replace(minute=0, second=0, microsecond=0)
            activity_pool.schedule(cr, uid, pbp_activity_id, date_schedule, context=context)

        return super(t4_clinical_patient_pbp_monitoring, self).complete(cr, uid, activity_id, context=context)


class t4_clinical_patient_weight_monitoring(orm.Model):
    _name = 't4.clinical.patient.weight_monitoring'
    _inherit = ['t4.activity.data']

    def _get_value(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['weight_monitoring'], context=context):
            result[r['id']] = 'On' if r['weight_monitoring'] else 'Off'
        return result

    _columns = {
        'weight_monitoring': fields.boolean('Postural Blood Presssure Monitoring', required=True),
        'value': fields.function(_get_value, type='char', size=3, string='String Value'),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['t4.clinical.api']
        weight_pool = self.pool['t4.clinical.patient.observation.weight']
        if activity.data_ref.weight_monitoring:
            api_pool.cancel_open_activities(cr, uid, activity.parent_id.id, weight_pool._name, context=context)
            weight_activity_id = weight_pool.create_activity(cr, SUPERUSER_ID,
                                 {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                                 {'patient_id': activity.data_ref.patient_id.id})
            date_schedule = dt.now().replace(minute=0, second=0, microsecond=0)
            activity_pool.schedule(cr, uid, weight_activity_id, date_schedule, context=context)

        return super(t4_clinical_patient_weight_monitoring, self).complete(cr, uid, activity_id, context=context)