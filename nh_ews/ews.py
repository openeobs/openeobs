# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from openerp.addons.nh_activity.activity import except_if
import logging
import bisect
from openerp import SUPERUSER_ID
import copy

_logger = logging.getLogger(__name__)


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
            if ews.is_partial:
                res[ews.id] = {'score': False, 'three_in_one': False, 'clinical_risk': 'None'}
            else:
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
        'device_id': fields.many2one('nh.clinical.device.type', 'Device'),
        'order_by': fields.related('activity_id', 'date_terminated', type='datetime', string='Date Terminated', store={
            'nh.clinical.patient.observation.ews': (lambda self, cr, uid, ids, ctx: ids, ['activity_id'], 10),
            'nh.activity.data': (_data2ews_ids, ['date_terminated'], 20)
        })
    }

    _form_description = [
        {
            'name': 'meta',
            'type': 'meta',
            'score': True
        },
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
            'validation': [
                {
                    'condition': {
                        'target': 'blood_pressure_systolic',
                        'operator': '>',
                        'value': 'blood_pressure_diastolic'
                    },
                    'message': {
                        'target': 'Systolic BP must be more than Diastolic BP',
                        'value': 'Diastolic BP must be less than Systolic BP'
                    }
                }
            ],
            'initially_hidden': False,
        },
        {
            'name': 'blood_pressure_diastolic',
            'type': 'integer',
            'label': 'Blood Pressure Diastolic',
            'min': 1,
            'max': 280,
            'validation': [
                {
                    'condition':{
                        'target': 'blood_pressure_diastolic',
                        'operator': '<',
                        'value': 'blood_pressure_systolic'
                    },
                    'message': {
                        'target': 'Diastolic BP must be less than Systolic BP',
                        'value': 'Systolic BP must be more than Diastolic BP'
                    }
                }
            ],
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
            'selection_type': 'text',
            'label': 'AVPU',
            'initially_hidden': False,
        },
        {
            'name': 'oxygen_administration_flag',
            'type': 'selection',
            'label': 'Patient on supplemental O2',
            'selection': [[False, 'No'], [True, 'Yes']],
            'selection_type': 'boolean',
            'initially_hidden': False,
            'on_change': [
                {
                    'fields': ['device_id'],
                    'condition': [['oxygen_administration_flag', '==', 'True']],
                    'action': 'show'
                },
                {
                    'fields': ['device_id', 'flow_rate', 'concentration', 'cpap_peep', 'niv_backup', 'niv_ipap', 'niv_epap'],
                    'condition': [['oxygen_administration_flag', '!=', 'True']],
                    'action': 'hide'
                }
            ],
        },
        {
            'name': 'device_id',
            'type': 'selection',
            'selection_type': 'number',
            'label': 'O2 Device',
            'on_change': [
                {
                    'fields': ['flow_rate', 'concentration'],
                    'condition': [['device_id', '!=', '']],
                    'action': 'show'
                },
                {
                    'fields': ['flow_rate', 'concentration'],
                    'condition': [['device_id', '==', '']],
                    'action': 'hide'
                },
                {
                    'fields': ['cpap_peep'],
                    'condition': [['device_id', '==', 44]],
                    'action': 'show'
                },
                {
                    'fields': ['cpap_peep'],
                    'condition': [['device_id', '!=', 44]],
                    'action': 'hide'
                },
                {
                    'fields': ['niv_backup', 'niv_ipap', 'niv_epap'],
                    'condition': [['device_id', '==', 45]],
                    'action': 'show'
                },
                {
                    'fields': ['niv_backup', 'niv_ipap', 'niv_epap'],
                    'condition': [['device_id', '!=', 45]],
                    'action': 'hide'
                }
            ],
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

    def handle_o2_devices(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        device_activity_ids = activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.device.session'],
            ['state', 'not in', ['completed', 'cancelled']]], context=context)
        da_browse = activity_pool.browse(cr, uid, device_activity_ids, context=context)
        device_activity_ids = [da.id for da in da_browse if da.data_ref.device_type_id.category_id.name == 'Supplemental O2']
        if not activity.data_ref.oxygen_administration_flag:
            [activity_pool.complete(cr, uid, dai, context=context) for dai in device_activity_ids]
        elif activity.data_ref.device_id:
            add_device = False
            if not device_activity_ids:
                add_device = True
            else:
                device_activity_ids = [da.id for da in da_browse if da.data_ref.device_type_id.category_id.name != activity.data_ref.device_id.name]
                if not any([da.id for da in da_browse if da.data_ref.device_type_id.name == activity.data_ref.device_id.name]):
                    add_device = True
                [activity_pool.complete(cr, uid, dai, context=context) for dai in device_activity_ids]
            if add_device:
                device_activity_id = self.pool['nh.clinical.device.session'].create_activity(cr, SUPERUSER_ID, {
                    'parent_id': activity.parent_id.id}, {
                    'patient_id': activity.patient_id.id,
                    'device_type_id': activity.data_ref.device_id.id,
                    'device_id': False})
                activity_pool.start(cr, uid, device_activity_id, context=context)

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
        self.handle_o2_devices(cr, uid, activity_id, context=context)

        # TRIGGER NOTIFICATIONS
        if not activity.data_ref.is_partial:
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
        if activity.data_ref.is_partial:
            activity_pool.schedule(cr, uid, next_activity_id, date_scheduled=activity.date_scheduled, context=context)
        else:
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
        device_pool = self.pool['nh.clinical.device.type']
        o2target_pool = self.pool['nh.clinical.patient.o2target']
        o2level_pool = self.pool['nh.clinical.o2level']
        fd = copy.deepcopy(self._form_description)
        # Find the O2 target
        o2level_id = o2target_pool.get_last(cr, uid, patient_id, context=context)
        if not o2level_id:
            o2target = False
        else:
            o2level = o2level_pool.browse(cr, uid, o2level_id, context=context)
            o2target = o2level.name
        # Find O2 devices
        device_ids = device_pool.search(cr, uid, [('category_id.name', '=', 'Supplemental O2')], context=context)
        device_selection = [[d, device_pool.read(cr, uid, d, ['name'], context=context)['name']] for d in device_ids]

        for field in fd:
            if field['name'] == 'indirect_oxymetry_spo2' and o2target:
                field['secondary_label'] = 'Target: {0}'.format(o2target)
            if field['name'] == 'device_id':
                field['selection'] = device_selection
        return fd

    def get_last_case(self, cr, uid, patient_id, context=None):
        """
        Checks for the last completed NEWS observation for the provided patient and returns the case.
        :return: False if there is no NEWS observation completed.
                0 to 3 integer. Number representing each case.
                0 - No Risk
                1 - Low Risk
                2 - Medium Risk
                3 - High Risk
        """
        domain = [['patient_id', '=', patient_id], ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                  ['state', '=', 'completed'], ['parent_id.state', '=', 'started']]
        activity_pool = self.pool['nh.activity']
        ews_ids = activity_pool.search(cr, uid, domain, order='date_terminated desc, sequence desc', context=context)
        if not ews_ids:
            return False
        activity = activity_pool.browse(cr, uid, ews_ids[0], context=context)
        case = int(self._POLICY['case'][bisect.bisect_left(self._POLICY['ranges'], activity.data_ref.score)])
        case = 2 if activity.data_ref.three_in_one and case < 3 else case
        return case