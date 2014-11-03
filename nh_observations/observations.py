# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.nh_activity.activity import except_if
from openerp.addons.nh_observations.parameters import frequencies
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from dateutil.relativedelta import relativedelta as rd
import logging
import bisect
from openerp import SUPERUSER_ID
from math import fabs

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation(orm.AbstractModel):
    _name = 'nh.clinical.patient.observation'
    _inherit = ['nh.activity.data']
    _required = [] # fields required for complete observation
    _num_fields = [] # numeric fields we want to be able to read as NULL instead of 0
    _partial_reasons = [['not_in_bed', 'Patient not in bed'],
                        ['asleep', 'Patient asleep']]
    
    def _is_partial(self, cr, uid, ids, field, args, context=None):
        ids = isinstance(ids, (tuple, list)) and ids or [ids]
        if not self._required:
            return {id: False for id in ids}
        res = {}
        for obs in self.read(cr, uid, ids, ['none_values'], context):
            res.update({obs['id']: bool(set(self._required) & set(eval(obs['none_values'])))})
        return res

    def _partial_observation_has_reason(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            if o.is_partial and not o.partial_reason:
                return False
        return True

    def calculate_score(self, data):
        return False

    def complete(self, cr, uid, activity_id, context=None):
        api = self.pool['nh.clinical.api']
        activity = api.get_activity(cr, uid, activity_id)
        res = super(nh_clinical_patient_observation, self).complete(cr, uid, activity_id, context)
        except_if(activity.data_ref.is_partial and not activity.data_ref.partial_reason,
                  msg="Partial observation didn't have reason")
        if not activity.date_started:
            self.pool['nh.activity'].write(cr, uid, activity_id, {'date_started': activity.date_terminated}, context=context)
        return res
    
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'is_partial': fields.function(_is_partial, type='boolean', string='Is Partial?'),
        'none_values': fields.text('Non-updated required fields'),
        'null_values': fields.text('Non-updated numeric fields'),
        'frequency': fields.selection(frequencies, 'Frequency'),
        'partial_reason': fields.selection(_partial_reasons, 'Reason if partial observation')
    }
    _defaults = {

    }
    _form_description = [
        {
            'name': 'meta',
            'type': 'meta',
            'score': False
        }
    ]
    
    def create(self, cr, uid, vals, context=None):
        none_values = list(set(self._required) - set(vals.keys()))
        null_values = list(set(self._num_fields) - set(vals.keys()))
        vals.update({'none_values': none_values, 'null_values': null_values})
        return super(nh_clinical_patient_observation, self).create(cr, uid, vals, context)
    
    def create_activity(self, cr, uid, activity_vals={}, data_vals={}, context=None):
        assert data_vals.get('patient_id'), "patient_id is a required field!"
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, data_vals['patient_id'], context=context)
        except_if(not spell_activity_id, msg="Current spell is not found for patient_id: %s" %  data_vals['patient_id'])
        activity_vals.update({'parent_id': spell_activity_id})
        return super(nh_clinical_patient_observation, self).create_activity(cr, uid, activity_vals, data_vals, context)      
                
    def write(self, cr, uid, ids, vals, context=None):
        ids = isinstance(ids, (tuple, list)) and ids or [ids]
        if not self._required and not self._num_fields:
            return super(nh_clinical_patient_observation, self).write(cr, uid, ids, vals, context)
        for obs in self.read(cr, uid, ids, ['none_values', 'null_values'], context):
            none_values = list(set(eval(obs['none_values'])) - set(vals.keys()))
            null_values = list(set(eval(obs['null_values'])) - set(vals.keys()))
            vals.update({'none_values': none_values, 'null_values': null_values})
            super(nh_clinical_patient_observation, self).write(cr, uid, obs['id'], vals, context)
        if 'frequency' in vals:
            activity_pool = self.pool['nh.activity']
            for obs in self.browse(cr, uid, ids, context=context):
                scheduled = (dt.strptime(obs.activity_id.create_date, DTF)+td(minutes=vals['frequency'])).strftime(DTF)
                activity_pool.schedule(cr, uid, obs.activity_id.id, date_scheduled=scheduled, context=context)
        return True

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        # if not self._num_fields:
        #     return super(nh_clinical_patient_observation, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        nolist = False
        if not isinstance(ids, list):
            ids = [ids]
            nolist = True
        if fields and 'null_values' not in fields:
            fields.append('null_values')
        res = super(nh_clinical_patient_observation, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        for obs in isinstance(res, (tuple, list)) and res or [res]:
            for nv in eval(obs['null_values'] or '{}'):
                if nv in obs.keys():
                    obs[nv] = False
        for d in res:
            for key in d.keys():
                if key in self._columns and self._columns[key]._type == 'float':
                    if not self._columns[key].digits:
                        _logger.warn("You might be reading a wrong float from the DB. Define digits attribute for float columns to avoid this problem.")
                    else:
                        d[key] = round(d[key], self._columns[key].digits[1])
        res = res[0] if nolist and len(res) > 0 else res
        return res

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        placement_pool = self.pool['nh.clinical.patient.placement']
        # FIXME + placement.id child_of current_spell_activity
        placement = placement_pool.browse_domain(cr, uid, [('patient_id','=',patient_id),('state','=','completed')], limit=1, order="date_terminated desc")
        location_id = placement and placement[0].location_id.id or False
        return location_id

    def get_form_description(self, cr, uid, patient_id, context=None):
        return self._form_description


class nh_clinical_patient_observation_height(orm.Model):
    _name = 'nh.clinical.patient.observation.height'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['height']
    _num_fields = ['height']
    _description = "Height Observation"
    _columns = {
        'height': fields.float('Height', digits=(1, 2)),
    }
    _form_description = [
        {
            'name': 'height',
            'type': 'float',
            'label': 'Height (m)',
            'min': 0.1,
            'max': 3.0,
            'digits': [1, 1],
            'initially_hidden': False
        }
    ]

class nh_clinical_patient_observation_weight(orm.Model):
    _name = 'nh.clinical.patient.observation.weight'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['weight']
    _num_fields = ['weight']
    _description = "Weight Observation"
    _columns = {
        'weight': fields.float('Weight', digits=(3, 1)),
    }
    _POLICY = {
        'schedule': [[6, 0]]
    }
    _form_description = [
        {
            'name': 'weight',
            'type': 'float',
            'label': 'Weight (Kg)',
            'min': 1.0,
            'max': 999.9,
            'digits': [3, 1],
            'initially_hidden': False
        }
    ]

    def schedule(self, cr, uid, activity_id, date_scheduled=None, context=None):
        hour = td(hours=1)
        schedule_times = []
        for s in self._POLICY['schedule']:
            schedule_times.append(dt.now().replace(hour=s[0], minute=s[1], second=0, microsecond=0))
        date_schedule = date_scheduled if date_scheduled else dt.now().replace(minute=0, second=0, microsecond=0)
        utctimes = [fields.datetime.utc_timestamp(cr, uid, t, context=context) for t in schedule_times]
        while all([date_schedule.hour != date_schedule.strptime(ut, DTF).hour for ut in utctimes]):
            date_schedule += hour
        return super(nh_clinical_patient_observation_weight, self).schedule(cr, uid, activity_id, date_schedule.strftime(DTF), context=context)

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)

        res = super(nh_clinical_patient_observation_weight, self).complete(cr, uid, activity_id, context)

        api_pool.cancel_open_activities(cr, uid, activity.parent_id.id, self._name, context=context)

        # create next Weight activity (schedule)
        domain = [
            ['data_model', '=', 'nh.clinical.patient.weight_monitoring'],
            ['state', '=', 'completed'],
            ['patient_id', '=', activity.data_ref.patient_id.id]
        ]
        weight_monitoring_ids = activity_pool.search(cr, uid, domain, order="date_terminated desc", context=context)
        monitoring_active = weight_monitoring_ids and activity_pool.browse(cr, uid, weight_monitoring_ids[0], context=context).data_ref.weight_monitoring
        if monitoring_active:
            next_activity_id = self.create_activity(cr, SUPERUSER_ID,
                                 {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                                 {'patient_id': activity.data_ref.patient_id.id})

            date_schedule = dt.now().replace(minute=0, second=0, microsecond=0) + td(hours=2)

            activity_pool.schedule(cr, uid, next_activity_id, date_schedule, context=context)
        return res


class nh_clinical_patient_observation_blood_product(orm.Model):
    _name = 'nh.clinical.patient.observation.blood_product'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['vol', 'product']
    _num_fields = ['vol']
    _description = "Blood Product Observation"
    _blood_product_values = [
        ['rbc', 'RBC'],
        ['ffp', 'FFP'],
        ['platelets', 'Platelets'],
        ['has', 'Human Albumin Sol'],
        ['dli', 'DLI'],
        ['stem', 'Stem Cells']
    ]
    _columns = {
        'vol': fields.float('Blood Product Vol', digits=(5, 1)),
        'product': fields.selection(_blood_product_values, 'Blood Product'),
    }
    _form_description = [
        {
            'name': 'vol',
            'type': 'float',
            'label': 'Vol (ml)',
            'min': 0.1,
            'max': 10000.0,
            'digits': [5, 1],
            'initially_hidden': False
        },
        {
            'name': 'product',
            'type': 'selection',
            'selection': _blood_product_values,
            'label': 'Blood Product',
            'initially_hidden': False
        }
    ]


class nh_clinical_patient_observation_blood_sugar(orm.Model):
    _name = 'nh.clinical.patient.observation.blood_sugar'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['blood_sugar']
    _num_fields = ['blood_sugar']
    _description = "Blood Sugar Observation"
    _columns = {
        'blood_sugar': fields.float('Blood Sugar', digits=(2, 1)),
    }
    _form_description = [
        {
            'name': 'blood_sugar',
            'type': 'float',
            'label': 'Blood Sugar (mmol/L)',
            'min': 1.0,
            'max': 99.9,
            'digits': [2, 1],
            'initially_hidden': False
        }
    ]