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
    _form_description = []
    
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
        if not self._num_fields:
            return super(nh_clinical_patient_observation, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        if fields and 'null_values' not in fields:
            fields.append('null_values')
        res = super(nh_clinical_patient_observation, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        for obs in isinstance(res, (tuple, list)) and res or [res]:
            for nv in eval(obs['null_values'] or '{}'):
                if nv in obs.keys():
                    obs[nv] = False
        return res

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        placement_pool = self.pool['nh.clinical.patient.placement']
        # FIXME + placement.id child_of current_spell_activity
        placement = placement_pool.browse_domain(cr, uid, [('patient_id','=',patient_id),('state','=','completed')], limit=1, order="date_terminated desc")
        #import pdb; pdb.set_trace()
        location_id = placement and placement[0].location_id.id or False
        return location_id

    def get_form_description(self, cr, uid, patient_id, context=None):
        return self._form_description


class nh_clinical_patient_observation_height(orm.Model):
    _name = 'nh.clinical.patient.observation.height'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['height']
    _description = "Height Observation"
    _columns = {
        'height': fields.float('Height', digits=(1, 1)),
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


class nh_clinical_patient_observation_stools(orm.Model):
    _name = 'nh.clinical.patient.observation.stools'
    _inherit = ['nh.clinical.patient.observation']
    _required = []
    _description = "Bristol Stools Observation"
    _boolean_selection = [[True, 'Yes'], [False, 'No']]
    _quantity_selection = [['large', 'Large'], ['medium', 'Medium'], ['small', 'Small']]
    _colour_selection = [['brown', 'Brown'], ['yellow', 'Yellow'], ['green', 'Green'], ['black', 'Black/Tarry'],
                         ['red', 'Red (fresh blood)'], ['clay', 'Clay']]
    _bristol_selection = [['1', 'Type 1'], ['2', 'Type 2'], ['3', 'Type 3'], ['4', 'Type 4'], ['5', 'Type 5'],
                          ['6', 'Type 6'], ['7', 'Type 7']]
    _samples_selection = [['none', 'None'], ['micro', 'Micro'], ['virol', 'Virol'], ['m+v', 'M+V']]
    _columns = {
        'bowel_open': fields.boolean('Bowel Open'),
        'nausea': fields.boolean('Nausea'),
        'vomiting': fields.boolean('Vomiting'),
        'quantity': fields.selection(_quantity_selection, 'Quantity'),
        'colour': fields.selection(_colour_selection, 'Colour'),
        'bristol_type': fields.selection(_bristol_selection, 'Bristol Type'),
        'offensive': fields.boolean('Offensive'),
        'strain': fields.boolean('Strain'),
        'laxatives': fields.boolean('Laxatives'),
        'samples': fields.selection(_samples_selection, 'Lab Samples'),
        'rectal_exam': fields.boolean('Rectal Exam'),
    }
    _form_description = [
        {
            'name': 'bowel_open',
            'type': 'selection',
            'label': 'Bowel Open',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'nausea',
            'type': 'selection',
            'label': 'Nausea',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'vomiting',
            'type': 'selection',
            'label': 'Vomiting',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'quantity',
            'type': 'selection',
            'label': 'Quantity',
            'selection': _quantity_selection,
            'initially_hidden': False
        },
        {
            'name': 'colour',
            'type': 'selection',
            'label': 'Colour',
            'selection': _colour_selection,
            'initially_hidden': False
        },
        {
            'name': 'bristol_type',
            'type': 'selection',
            'label': 'Bristol Type',
            'selection': _bristol_selection,
            'initially_hidden': False
        },
        {
            'name': 'offensive',
            'type': 'selection',
            'label': 'Offensive',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'strain',
            'type': 'selection',
            'label': 'Strain',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'laxatives',
            'type': 'selection',
            'label': 'Laxatives',
            'selection': _boolean_selection,
            'initially_hidden': False
        },
        {
            'name': 'samples',
            'type': 'selection',
            'label': 'Lab Samples',
            'selection': _samples_selection,
            'initially_hidden': False
        },
        {
            'name': 'rectal_exam',
            'type': 'selection',
            'label': 'Rectal Exam',
            'selection': _boolean_selection,
            'initially_hidden': False
        }
    ]


class nh_clinical_patient_observation_ews(orm.Model):
    _name = 'nh.clinical.patient.observation.ews'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['respiration_rate', 'indirect_oxymetry_spo2', 'body_temperature', 'blood_pressure_systolic', 'pulse_rate']
    _num_fields = ['respiration_rate', 'indirect_oxymetry_spo2', 'body_temperature', 'blood_pressure_systolic',
                   'blood_pressure_diastolic', 'pulse_rate', 'flow_rate', 'concentration', 'cpap_peep', 'niv_backup',
                   'niv_ipap', 'niv_epap']
    _description = "NEWS Observation"

    _RR_RANGES = {'ranges': [8, 11, 20, 24], 'scores': '31023'}
    _O2_RANGES = {'ranges': [91, 93, 95], 'scores': '3210'}
    _BT_RANGES = {'ranges': [35.0, 36.0, 38.0, 39.0], 'scores': '31012'}
    _BP_RANGES = {'ranges': [90, 100, 110, 219], 'scores': '32103'}
    _PR_RANGES = {'ranges': [40, 50, 90, 110, 130], 'scores': '310123'}
    """
    Default EWS policy has 4 different scenarios:
        case 0: no clinical risk
        case 1: low clinical risk
        case 2: medium clinical risk
        case 3: high clinical risk
    """
    _POLICY = {'ranges': [0, 4, 6], 'case': '0123', 'frequencies': [720, 240, 60, 30],
               'notifications': [
                   [],
                   [{'model': 'assessment', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca']},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}],
                   [{'model': 'medical_team', 'summary': 'Urgently inform medical team', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca']},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}],
                   [{'model': 'medical_team', 'summary': 'Immediately inform medical team', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca']},
                    {'model': 'nurse', 'summary': 'Informed about patient status (NEWS)', 'groups': ['hca']}]
               ],
               'risk': ['None', 'Low', 'Medium', 'High']}

    def calculate_score(self, ews_data):
        score = 0
        three_in_one = False

        aux = int(self._RR_RANGES['scores'][bisect.bisect_left(self._RR_RANGES['ranges'], ews_data['respiration_rate'])])
        three_in_one = three_in_one or aux == 3
        score += aux

        aux = int(self._O2_RANGES['scores'][bisect.bisect_left(self._O2_RANGES['ranges'], ews_data['indirect_oxymetry_spo2'])])
        three_in_one = three_in_one or aux == 3
        score += aux

        aux = int(self._BT_RANGES['scores'][bisect.bisect_left(self._BT_RANGES['ranges'], ews_data['body_temperature'])])
        three_in_one = three_in_one or aux == 3
        score += aux

        aux = int(self._BP_RANGES['scores'][bisect.bisect_left(self._BP_RANGES['ranges'], ews_data['blood_pressure_systolic'])])
        three_in_one = three_in_one or aux == 3
        score += aux

        aux = int(self._PR_RANGES['scores'][bisect.bisect_left(self._PR_RANGES['ranges'], ews_data['pulse_rate'])])
        three_in_one = three_in_one or aux == 3
        score += aux

        if 'oxygen_administration_flag' in ews_data and ews_data['oxygen_administration_flag']:
            score += 2 if ews_data['oxygen_administration_flag'] else 0

        score += 3 if ews_data['avpu_text'] in ['V', 'P', 'U'] else 0
        three_in_one = True if ews_data['avpu_text'] in ['V', 'P', 'U'] else three_in_one

        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], score)])
        case = 2 if three_in_one and case < 3 else case
        clinical_risk = self._POLICY['risk'][case]

        return {'score': score, 'three_in_one': three_in_one, 'clinical_risk': clinical_risk}

    
    def _get_score(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for ews in self.browse(cr, uid, ids, context):
            res[ews.id] = self.calculate_score(ews)
            _logger.debug("Observation EWS activity_id=%s ews_id=%s score: %s" % (ews.activity_id.id, ews.id, res[ews.id]))
        return res

    def _data2ews_ids(self, cr, uid, ids, context=None):
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        ews_ids = ews_pool.search(cr, uid, [('activity_id', 'in', ids)], context=context)
        return ews_ids
    _avpu_values = [['A', 'Alert'], ['V', 'Voice'], ['P', 'Pain'], ['U', 'Unresponsive']]
    _columns = {
        #'duration': fields.integer('Duration'),
        'score': fields.function(_get_score, type='integer', multi='score', string='Score', store={
            'nh.clinical.patient.observation.ews': (lambda self, cr, uid, ids, ctx: ids, [], 10) # all fields of self
        }),
        'three_in_one': fields.function(_get_score, type='boolean', multi='score', string='3 in 1 flag', store={
            'nh.clinical.patient.observation.ews': (lambda self, cr, uid, ids, ctx: ids, [], 10) # all fields of self
        }),
        'clinical_risk': fields.function(_get_score, type='char', multi='score', string='Clinical Risk', store={
            'nh.clinical.patient.observation.ews': (lambda self, cr, uid, ids, ctx: ids, [], 10)
        }),
        'respiration_rate': fields.integer('Respiration Rate'),
        'indirect_oxymetry_spo2': fields.integer('O2 Saturation'),
        'oxygen_administration_flag': fields.boolean('Patient on supplemental O2'),
        'body_temperature': fields.float('Body Temperature', digits=(2, 1)),
        'blood_pressure_systolic': fields.integer('Blood Pressure Systolic'),
        'blood_pressure_diastolic': fields.integer('Blood Pressure Diastolic'),
        'pulse_rate': fields.integer('Pulse Rate'),
        'avpu_text': fields.selection(_avpu_values, 'AVPU'),
        'mews_score': fields.integer('Mews Score'),
        # O2 stuff former 'o2_device_reading_id'
        'flow_rate': fields.float('Flow rate (l/min)', digits=(3, 1)),
        'concentration': fields.integer('Concentration (%)'),
        'cpap_peep': fields.integer('CPAP: PEEP (cmH2O)'),
        'niv_backup': fields.integer('NIV: Back-up rate (br/min)'),
        'niv_ipap': fields.integer('NIV: IPAP (cmH2O)'),
        'niv_epap': fields.integer('NIV: EPAP (cmH2O)'),
        'device_id': fields.many2one('nh.clinical.device', 'Device'),
        'order_by': fields.related('activity_id', 'date_terminated', type='datetime', string='Date Terminated', store={
            'nh.clinical.patient.observation.ews': (lambda self, cr, uid, ids, ctx: ids, ['activity_id'], 10),
            'nh.activity.data': (_data2ews_ids, ['date_terminated'], 20)
        })
    }

    _form_description = [
        {
            'name': 'respiration_rate',
            'type': 'integer',
            'label': 'Respiration Rate',
            'min': 1,
            'max': 59,
            'initially_hidden': False,
        },
        {
            'name': 'indirect_oxymetry_spo2',
            'type': 'integer',
            'label': 'O2 Saturation',
            'min': 51,
            'max': 100,
            'initially_hidden': False,
        },
        {
            'name': 'body_temperature',
            'type': 'float',
            'label': 'Body Temperature',
            'min': 27.1,
            'max': 44.9,
            'digits': [2, 1],
            'initially_hidden': False,
        },
        {
            'name': 'blood_pressure_systolic',
            'type': 'integer',
            'label': 'Blood Pressure Systolic',
            'min': 1,
            'max': 300,
            'validation': [['>', 'blood_pressure_diastolic']],
            'initially_hidden': False,
        },
        {
            'name': 'blood_pressure_diastolic',
            'type': 'integer',
            'label': 'Blood Pressure Diastolic',
            'min': 1,
            'max': 280,
            'validation': [['<', 'blood_pressure_systolic']],
            'initially_hidden': False,
        },
        {
            'name': 'pulse_rate',
            'type': 'integer',
            'label': 'Pulse Rate',
            'min': 1,
            'max': 250,
            'initially_hidden': False,
        },
        {
            'name': 'avpu_text',
            'type': 'selection',
            'selection': _avpu_values,
            'label': 'AVPU',
            'initially_hidden': False,
        },
        {
            'name': 'oxygen_administration_flag',
            'type': 'selection',
            'label': 'Patient on supplemental O2',
            'selection': [[False, 'No'], [True, 'Yes']],
            'initially_hidden': False,
            'on_change': {
                'True': {
                    'show': ['device_id'],
                    'hide': []
                },
                'False': {
                    'show': [],
                    'hide': ['device_id', 'flow_rate', 'concentration', 'cpap_peep', 'niv_backup', 'niv_ipap', 'niv_epap']
                }
            }
        },
        {
            'name': 'device_id',
            'type': 'selection',
            'label': 'O2 Device',
            'initially_hidden': True
        },
        {
            'name': 'flow_rate',
            'type': 'float',
            'label': 'Flow Rate',
            'min': 0,
            'max': 100.0,
            'digits': [3, 1],
            'initially_hidden': True
        },
        {
            'name': 'concentration',
            'type': 'integer',
            'label': 'Concentration',
            'min': 0,
            'max': 100,
            'initially_hidden': True
        },
        {
            'name': 'cpap_peep',
            'type': 'integer',
            'label': 'CPAP: PEEP (cmH2O)',
            'min': 0,
            'max': 1000,
            'initially_hidden': True
        },
        {
            'name': 'niv_backup',
            'type': 'integer',
            'label': 'NIV: Back-up rate (br/min)',
            'min': 0,
            'max': 100,
            'initially_hidden': True
        },
        {
            'name': 'niv_ipap',
            'type': 'integer',
            'label': 'NIV: IPAP (cmH2O)',
            'min': 0,
            'max': 100,
            'initially_hidden': True
        },
        {
            'name': 'niv_epap',
            'type': 'integer',
            'label': 'NIV: EPAP (cmH2O)',
            'min': 0,
            'max': 100,
            'initially_hidden': True
        }
    ]

    _defaults = {
        'frequency': 15
    }

    _order = "order_by desc, id desc"

    def submit(self, cr, uid, activity_id, data_vals={}, context=None):
        vals = data_vals.copy()
        if vals.get('oxygen_administration'):
            vals.update({'oxygen_administration_flag': vals['oxygen_administration'].get('oxygen_administration_flag')})
            del vals['oxygen_administration']


        return super(nh_clinical_patient_observation_ews, self).submit(cr, SUPERUSER_ID, activity_id, data_vals, context)      
    
    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default EWS policy
        """
        activity_pool = self.pool['nh.activity']
        groups_pool = self.pool['res.groups']
        api_pool = self.pool['nh.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        case = 2 if activity.data_ref.three_in_one and case < 3 else case
        hcagroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False
        spell_activity_id = activity.parent_id.id
        except_if(not group, cap="Are you sure you are supposed to complete this activity?", msg="Current user is not found in groups Nurse, HCA")
        # TRIGGER NOTIFICATIONS
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._POLICY['notifications'][case],
            'parent_id': spell_activity_id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': self._name,
            'group': group
        }, context=context)

        res = super(nh_clinical_patient_observation_ews, self).complete(cr, uid, activity_id, context)

        # create next EWS
        next_activity_id = self.create_activity(cr, SUPERUSER_ID, 
                             {'creator_id': activity_id, 'parent_id': spell_activity_id},
                             {'patient_id': activity.data_ref.patient_id.id})
        api_pool.change_activity_frequency(cr, SUPERUSER_ID,
                                           activity.data_ref.patient_id.id,
                                           self._name,
                                           self._POLICY['frequencies'][case], context=context)
        return res
    
    def create_activity(self, cr, uid, vals_activity={}, vals_data={}, context=None):
        activity_pool = self.pool['nh.activity']
        domain = [['patient_id','=',vals_data['patient_id']],['data_model','=',self._name],['state','in',['new','started','scheduled']]]
        ids = activity_pool.search(cr, SUPERUSER_ID, domain)
        #TODO THIS SHOULD NOT BE AN ERROR, CREATING REDUNDANT ACTIVITIES SHOULD BE ALLOWED BY REMOVING THE OLD ONES - ADD WARNING MAYBE
        except_if(len(ids),
                  msg="Having more than one activity of type '%s' is restricted. Terminate activities with ids=%s first"
                  % (self._name, str(ids)))
        res = super(nh_clinical_patient_observation_ews, self).create_activity(cr, uid, vals_activity, vals_data, context)
        return res

    def get_form_description(self, cr, uid, patient_id, context=None):
        activity_pool = self.pool['nh.activity']
        device_pool = self.pool['nh.clinical.device']
        fd = list(self._form_description)
        # Find the O2 target
        o2target_ids = activity_pool.search(cr, uid, [
            ('state', '=', 'completed'),
            ('patient_id', '=', patient_id),
            ('data_model', '=', 'nh.clinical.patient.o2target')], order='date_terminated desc', context=context)
        if not o2target_ids:
            o2target = False
        else:
            o2tactivity = activity_pool.browse(cr, uid, o2target_ids[0], context=context)
            o2target = o2tactivity.data_ref.level_id.name
        # Find O2 devices
        device_ids = device_pool.search(cr, uid, [('type_id.name', '=', 'Supplemental O2')], context=context)
        device_selection = [[d, device_pool.read(cr, uid, d, ['name'], context=context)['name']] for d in device_ids]
        device_on_change = {}
        for ds in device_selection:
            if ds[1] == 'CPAP':
                device_on_change[ds[1]] = {
                    'show': ['flow_rate', 'concentration', 'cpap_peep'],
                    'hide': ['niv_backup', 'niv_ipap', 'niv_epap']
                }
            elif ds[1] == 'NIV BiPAP':
                device_on_change[ds[1]] = {
                    'show': ['flow_rate', 'concentration', 'niv_backup', 'niv_ipap', 'niv_epap'],
                    'hide': ['cpap_peep']
                }
            else:
                device_on_change[ds[1]] = {
                    'show': ['flow_rate', 'concentration'],
                    'hide': ['cpap_peep', 'niv_backup', 'niv_ipap', 'niv_epap']
                }

        for field in fd:
            if field['name'] == 'indirect_oxymetry_spo2' and o2target:
                field['secondary_label'] = o2target
            if field['name'] == 'device_id':
                field['selection'] = device_selection
                field['on_change'] = device_on_change
        return fd


class nh_clinical_patient_observation_gcs(orm.Model):
    _name = 'nh.clinical.patient.observation.gcs'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['eyes', 'verbal', 'motor']
    _description = "GCS Observation"
    _eyes = [('1', '1: Does not open eyes'),
             ('2', '2: Opens eyes in response to painful stimuli'),
             ('3', '3: Opens eyes in response to voice'),
             ('4', '4: Opens eyes spontaneously'),
             ('C', 'C: Closed by swelling')]
    _verbal = [('1', '1: Makes no sounds'),
               ('2', '2: Incomprehensible sounds'),
               ('3', '3: Utters inappropiate words'),
               ('4', '4: Confused, disoriented'),
               ('5', '5: Oriented, converses normally'),
               ('T', 'T: Intubated')]
    _motor = [('1', '1: Makes no movements'),
              ('2', '2: Extension to painful stimuli (decerebrate response)'),
              ('3', '3: Abnormal flexion to painful stimuli (decorticate response)'),
              ('4', '4: Flexion / Withdrawal to painful stimuli'),
              ('5', '5: Localizes painful stimuli'),
              ('6', '6: Obeys commands')]

    """
    Default GCS policy has 5 different scenarios:
        case 0: 30 min frequency
        case 1: 1 hour frequency
        case 2: 2 hour frequency
        case 3: 4 hour frequency
        case 4: 12 hour frequency (no clinical risk)
    """
    _POLICY = {'ranges': [5, 9, 13, 14], 'case': '01234', 'frequencies': [30, 60, 120, 240, 720],
               'notifications': [[], [], [], [], []]}

    def calculate_score(self, gcs_data):
        eyes = 1 if gcs_data['eyes'] == 'C' else int(gcs_data['eyes'])
        verbal = 1 if gcs_data['verbal'] == 'T' else int(gcs_data['verbal'])
        motor = int(gcs_data['motor'])

        return {'score': eyes+verbal+motor}

    def _get_score(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for gcs in self.browse(cr, uid, ids, context):
            res[gcs.id] = self.calculate_score({'eyes': gcs.eyes, 'verbal': gcs.verbal, 'motor': gcs.motor})
            _logger.debug("Observation GCS activity_id=%s gcs_id=%s score: %s" % (gcs.activity_id.id, gcs.id, res[gcs.id]))
        return res

    _columns = {
        'score': fields.function(_get_score, type='integer', multi='score', string='Score', store={
                       'nh.clinical.patient.observation.gcs': (lambda self,cr,uid,ids,ctx: ids, [], 10) # all fields of self
        }),
        'eyes': fields.selection(_eyes, 'Eyes'),
        'verbal': fields.selection(_verbal, 'Verbal'),
        'motor': fields.selection(_motor, 'Motor')
    }

    _defaults = {
        'frequency': 60
    }

    _form_description = [
        {
            'name': 'eyes',
            'type': 'selection',
            'label': 'Eyes',
            'selection': _eyes,
            'initially_hidden': False
        },
        {
            'name': 'verbal',
            'type': 'selection',
            'label': 'Verbal',
            'selection': _verbal,
            'initially_hidden': False
        },
        {
            'name': 'motor',
            'type': 'selection',
            'label': 'Motor',
            'selection': _motor,
            'initially_hidden': False
        }
    ]

    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default GCS policy
        """
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        groups_pool = self.pool['res.groups']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        hcagroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False

        # TRIGGER NOTIFICATIONS
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._POLICY['notifications'][case],
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': self._name,
            'group': group
        }, context=context)

        res = super(nh_clinical_patient_observation_gcs, self).complete(cr, uid, activity_id, context)

        # create next GCS
        next_activity_id = self.create_activity(cr, SUPERUSER_ID, 
                             {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                             {'patient_id': activity.data_ref.patient_id.id})
        api_pool.change_activity_frequency(cr, SUPERUSER_ID,
                                           activity.data_ref.patient_id.id,
                                           self._name,
                                           self._POLICY['frequencies'][case], context=context)
        return res

    def create_activity(self, cr, uid, vals_activity={}, vals_data={}, context=None):
        assert vals_data.get('patient_id'), "patient_id is a required field!"
        activity_pool = self.pool['nh.activity']
        domain = [['patient_id','=',vals_data['patient_id']],['data_model','=',self._name],['state','in',['new','started','scheduled']]]
        ids = activity_pool.search(cr, SUPERUSER_ID, domain)
        except_if(len(ids),
                  msg="Having more than one activity of type '%s' is restricted. Terminate activities with ids=%s first"
                  % (self._name, str(ids)))
        res = super(nh_clinical_patient_observation_gcs, self).create_activity(cr, uid, vals_activity, vals_data, context)
        return res


class nh_clinical_patient_observation_pbp(orm.Model):
    _name = 'nh.clinical.patient.observation.pbp'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['systolic_sitting', 'diastolic_sitting', 'systolic_standing', 'diastolic_standing']
    _description = "Postural Blood Pressure Observation"

    _POLICY = {'schedule': [[6, 0], [18, 0]], 'notifications': [
        [],
        [{'model': 'nurse', 'summary': 'Inform FY2', 'groups': ['nurse', 'hca']},
         {'model': 'hca', 'summary': 'Inform registered nurse', 'groups': ['hca']},
         {'model': 'nurse', 'summary': 'Informed about patient status (Postural Blood Pressure)', 'groups': ['hca']}]
    ]}

    def _get_pbp_result(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pbp in self.browse(cr, uid, ids, context=context):
            if int(pbp.systolic_sitting - pbp.systolic_standing) > 20:
                res[pbp.id] = 'yes'
            else:
                res[pbp.id] = 'no'
        return res

    _columns = {
        'systolic_sitting': fields.integer('Sitting Blood Pressure Systolic'),
        'systolic_standing': fields.integer('Standing Blood Pressure Systolic'),
        'diastolic_sitting': fields.integer('Sitting Blood Pressure Diastolic'),
        'diastolic_standing': fields.integer('Standing Blood Pressure Diastolic'),
        'result': fields.function(_get_pbp_result, type='char', string='>20 mm/Hg', size=5, store=False)
    }

    _form_description = [
        {
            'name': 'systolic_sitting',
            'type': 'integer',
            'label': 'Sitting Blood Pressure Systolic',
            'min': 1,
            'max': 300,
            'validation': [['>', 'diastolic_sitting']],
            'initially_hidden': False
        },
        {
            'name': 'diastolic_sitting',
            'type': 'integer',
            'label': 'Sitting Blood Pressure Diastolic',
            'min': 1,
            'max': 280,
            'validation': [['<', 'systolic_sitting']],
            'initially_hidden': False
        },
        {
            'name': 'systolic_standing',
            'type': 'integer',
            'label': 'Standing Blood Pressure Systolic',
            'min': 1,
            'max': 300,
            'validation': [['>', 'diastolic_standing']],
            'initially_hidden': True
        },
        {
            'name': 'diastolic_standing',
            'type': 'integer',
            'label': 'Standing Blood Pressure Diastolic',
            'min': 1,
            'max': 280,
            'validation': [['<', 'systolic_standing']],
            'initially_hidden': True
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
        return super(nh_clinical_patient_observation_pbp, self).schedule(cr, uid, activity_id, date_schedule.strftime(DTF), context=context)

    def complete(self, cr, uid, activity_id, context=None):
        """
        Implementation of the default PBP policy
        """
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        groups_pool = self.pool['res.groups']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        case = int(activity.data_ref.result == 'yes')
        hcagroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(cr, uid, [('users', 'in', [uid]), ('name', '=', 'NH Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False

        # TRIGGER NOTIFICATIONS
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._POLICY['notifications'][case],
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': self._name,
            'group': group
        }, context=context)

        res = super(nh_clinical_patient_observation_pbp, self).complete(cr, uid, activity_id, context)

        api_pool.cancel_open_activities(cr, uid, activity.parent_id.id, self._name, context=context)

        # create next PBP (schedule)
        domain = [
            ['data_model', '=', 'nh.clinical.patient.pbp_monitoring'],
            ['state', '=', 'completed'],
            ['patient_id', '=', activity.data_ref.patient_id.id]
        ]
        pbp_monitoring_ids = activity_pool.search(cr, uid, domain, order="date_terminated desc", context=context)
        monitoring_active = pbp_monitoring_ids and activity_pool.browse(cr, uid, pbp_monitoring_ids[0], context=context).data_ref.pbp_monitoring
        if monitoring_active:
            next_activity_id = self.create_activity(cr, SUPERUSER_ID,
                                 {'creator_id': activity_id, 'parent_id': activity.parent_id.id},
                                 {'patient_id': activity.data_ref.patient_id.id})

            date_schedule = dt.now().replace(minute=0, second=0, microsecond=0) + td(hours=2)

            activity_pool.schedule(cr, uid, next_activity_id, date_schedule, context=context)
        return res