# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
Defines the Early Warning Score observation class and its standard behaviour
and policy triggers based on the UK NEWS standard.
"""
import bisect
import copy
import logging
from datetime import datetime as dt
from datetime import timedelta

from openerp import SUPERUSER_ID, api
from openerp.addons.nh_observations import frequencies
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation_ews(orm.Model):
    """
    Represents an Early Warning Score
    :class:`observation<observations.nh_clinical_patient_observation>`
    which stores a group of physiological parameters measured from the
    :class:`patient<base.nh_clinical_patient>` that together determine
    a score that serves as an indicator of the illness current acuity.

    The basis of the scoring system are the following six parameters:
    respiratory rate, oxygen saturations, temperature, systolic blood
    pressure, pulse rate and level of consciousness.
    """
    _name = 'nh.clinical.patient.observation.ews'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['respiration_rate', 'indirect_oxymetry_spo2',
                 'body_temperature', 'blood_pressure_systolic', 'pulse_rate',
                 'avpu_text', 'blood_pressure_diastolic',
                 'oxygen_administration_flag']
    _num_fields = ['respiration_rate', 'indirect_oxymetry_spo2',
                   'body_temperature', 'blood_pressure_systolic',
                   'blood_pressure_diastolic', 'pulse_rate', 'flow_rate',
                   'concentration', 'cpap_peep', 'niv_backup', 'niv_ipap',
                   'niv_epap']
    _description = "NEWS Observation"

    _RR_RANGES = {'ranges': [8, 11, 20, 24], 'scores': '31023'}
    _O2_RANGES = {'ranges': [91, 93, 95], 'scores': '3210'}
    _BT_RANGES = {'ranges': [35.0, 36.0, 38.0, 39.0], 'scores': '31012'}
    _BP_RANGES = {'ranges': [90, 100, 110, 219], 'scores': '32103'}
    _PR_RANGES = {'ranges': [40, 50, 90, 110, 130], 'scores': '310123'}
    """
    Default EWS (Early Warning Score) policy has 4 different scenarios:
        case 0: no clinical risk
        case 1: low clinical risk
        case 2: medium clinical risk
        case 3: high clinical risk
    """
    _POLICY = {'ranges': [0, 4, 6], 'case': '0123',
               'frequencies': [720, 240, 60, 30],
               'notifications': [
                   [],
                   [{'model': 'assessment', 'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse',
                     'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse',
                     'summary': 'Informed about patient status (NEWS)',
                     'groups': ['hca']}],
                   [{'model': 'medical_team',
                     'summary': 'Urgently inform medical team',
                     'groups': ['nurse', 'hca']},
                    {'model': 'hca',
                     'summary': 'Inform registered nurse',
                     'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse',
                     'summary': 'Informed about patient status (NEWS)',
                     'groups': ['hca']}],
                   [{'model': 'medical_team',
                     'summary': 'Immediately inform medical team',
                     'groups': ['nurse', 'hca']},
                    {'model': 'hca', 'summary': 'Inform registered nurse',
                     'groups': ['hca'], 'assign': 1},
                    {'model': 'nurse',
                     'summary': 'Informed about patient status (NEWS)',
                     'groups': ['hca']}]],
               'risk': ['None', 'Low', 'Medium', 'High']}

    def convert_case_to_risk(self, case):
        return self._POLICY['risk'][case]

    def _is_partial(self, cr, uid, ids, field, args, context=None):
        ids = ids if isinstance(ids, (tuple, list)) else [ids]
        if not self._required:
            return {id: False for id in ids}
        res = {}
        for obs in self.read(cr, uid, ids, ['none_values',
                                            'oxygen_administration_flag',
                                            'device_id',
                                            'flow_rate',
                                            'cpap_peep',
                                            'niv_epap',
                                            'niv_backup',
                                            'niv_ipap',
                                            'concentration'], context):
            partial = bool(set(self._required) & set(eval(obs['none_values'])))
            suppl_oxygen = obs.get('oxygen_administration_flag')
            if not partial and suppl_oxygen:
                device_id = obs.get('device_id', None)
                if device_id:
                    flow = obs.get('flow_rate', None)
                    concentration = obs.get('concentration', None)
                    if not flow and not concentration:
                        partial = True
                    if device_id[1] == 'CPAP' and not obs.get('cpap_peep'):
                        partial = True
                    if device_id[1] == 'NIV BiPAP':
                        ipap = obs.get('niv_ipap')
                        epap = obs.get('niv_epap')
                        backup = obs.get('niv_backup')
                        if not ipap or not epap or not backup:
                            partial = True
                else:
                    partial = True
            res.update(
                {
                    obs['id']: partial
                })
        return res

    def _is_partial_search(self, cr, uid, obj, name, args, domain=None,
                           context=None):
            arg1, op, arg2 = args[0]
            arg2 = bool(arg2)
            all_ids = self.search(cr, uid, [])
            is_partial_map = self._is_partial(
                cr, uid, all_ids, 'is_partial', None, context=context)
            partial_ews_ids = [key for key, value in is_partial_map.items()
                               if value]
            if arg2:
                return [('id', 'in', [ews_id for ews_id in all_ids
                                      if ews_id in partial_ews_ids])]
            else:
                return [('id', 'in', [ews_id for ews_id in all_ids
                                      if ews_id not in partial_ews_ids])]

    def calculate_score(self, ews_data):
        """
        Computes the score and clinical risk values based on the NEWS
        parameters provided.

        It will return as extra information the presence of any Red
        Score parameter within the data. (any parameter that scores 3)

        :param ews_data: The NEWS parameters: ``respiration_rate``,
                         ``indirect_oxymetry_spo2``, ``body_temperature``,
                         ``blood_pressure_systolic``, ``pulse_rate``,
                         ``oxygen_administration_flag`` and ``avpu_text``
        :type ews_data: dict
        :returns: ``score``, ``clinical_risk`` and ``three_in_one``
        :rtype: dict
        """
        score = 0
        three_in_one = False
        if isinstance(ews_data, dict):
            resp_rate = ews_data.get('respiration_rate')
            oxy_sat = ews_data.get('indirect_oxymetry_spo2')
            temp = ews_data.get('body_temperature')
            bp_sys = ews_data.get('blood_pressure_systolic')
            pulse = ews_data.get('pulse_rate')
            suppl_oxy = ews_data.get('oxygen_administration_flag')
            avpu = ews_data.get('avpu_text', '')
        else:
            resp_rate = ews_data.respiration_rate
            oxy_sat = ews_data.indirect_oxymetry_spo2
            temp = ews_data.body_temperature
            bp_sys = ews_data.blood_pressure_systolic
            pulse = ews_data.pulse_rate
            suppl_oxy = ews_data.oxygen_administration_flag
            avpu = ews_data.avpu_text

        # If empty observation being evaluated then return None for all values
        if not any([resp_rate, oxy_sat, temp, bp_sys, pulse, suppl_oxy, avpu]):
            return {'score': None, 'three_in_one': None, 'clinical_risk': None}

        if resp_rate:
            aux = int(self._RR_RANGES['scores'][bisect.bisect_left(
                self._RR_RANGES['ranges'], resp_rate)])
            three_in_one = three_in_one or aux == 3
            score += aux

        if oxy_sat:
            aux = int(self._O2_RANGES['scores'][bisect.bisect_left(
                self._O2_RANGES['ranges'], oxy_sat)])
            three_in_one = three_in_one or aux == 3
            score += aux

        if temp:
            aux = int(self._BT_RANGES['scores'][bisect.bisect_left(
                self._BT_RANGES['ranges'], temp)])
            three_in_one = three_in_one or aux == 3
            score += aux

        if bp_sys:
            aux = int(self._BP_RANGES['scores'][bisect.bisect_left(
                self._BP_RANGES['ranges'], bp_sys)])
            three_in_one = three_in_one or aux == 3
            score += aux

        if pulse:
            aux = int(self._PR_RANGES['scores'][bisect.bisect_left(
                self._PR_RANGES['ranges'], pulse)])
            three_in_one = three_in_one or aux == 3
            score += aux

        if suppl_oxy:
            score += 2

        if avpu in ['V', 'P', 'U']:
            score += 3
            three_in_one = True

        case = int(self._POLICY['case'][bisect.bisect_left(
            self._POLICY['ranges'], score)])
        case = 2 if three_in_one and case < 3 else case
        clinical_risk = self._POLICY['risk'][case]

        return {'score': score, 'three_in_one': three_in_one,
                'clinical_risk': clinical_risk}

    def _get_score(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for ews in self.browse(cr, uid, ids, context):
            partial = \
                self._is_partial(cr, uid, ews.id, None, None).get(ews.id)
            if partial:
                res[ews.id] = {'score': False, 'three_in_one': False,
                               'clinical_risk': 'Unknown'}
            else:
                res[ews.id] = self.calculate_score(ews)
            _logger.debug(
                "Observation EWS activity_id=%s ews_id=%s score: %s"
                % (ews.activity_id.id, ews.id, res[ews.id]))
        return res

    def _get_score_display(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for ews in self.browse(cr, uid, ids, context=context):
            if ews.is_partial:
                display = ''
            else:
                display = str(ews.score)
            res[ews.id] = display
        return res

    def _get_o2_display(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for ews in self.browse(cr, uid, ids, context=context):
            if not ews.oxygen_administration_flag:
                res[ews.id] = 'No'
            else:
                display = ''
                if ews.flow_rate:
                    display += str(ews.flow_rate) + ' l/m '
                elif ews.concentration:
                    display += str(ews.concentration) + '% '
                if ews.device_id:
                    display += ews.device_id.name
                res[ews.id] = display
        return res

    def _get_bp_display(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for ews in self.browse(cr, uid, ids, context=context):
            if not ews.blood_pressure_systolic:
                res[ews.id] = '- / -'
            else:
                res[ews.id] = str(
                    ews.blood_pressure_systolic
                ) + ' / ' + str(ews.blood_pressure_diastolic)
        return res

    def _data2ews_ids(self, cr, uid, ids, context=None):
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        ews_ids = ews_pool.search(
            cr, uid, [('activity_id', 'in', ids)], context=context)
        return ews_ids

    _avpu_values = [['A', 'Alert'], ['V', 'Voice'], ['P', 'Pain'],
                    ['U', 'Unresponsive']]
    _columns = {
        'score': fields.function(
            _get_score, type='integer', multi='score', string='Score', store={
                'nh.clinical.patient.observation.ews': (
                    lambda self, cr, uid, ids, ctx: ids, [], 10)
            }),
        'three_in_one': fields.function(
            _get_score, type='boolean', multi='score', string='3 in 1 flag',
            store={
                'nh.clinical.patient.observation.ews': (
                    lambda self, cr, uid, ids, ctx: ids, [], 10)
            }),
        'clinical_risk': fields.function(
            _get_score, type='char', multi='score', string='Clinical Risk',
            store={
                'nh.clinical.patient.observation.ews': (
                    lambda self, cr, uid, ids, ctx: ids, [], 10)
            }),
        'is_partial': fields.function(_is_partial, type='boolean',
                                      fnct_search=_is_partial_search,
                                      string='Is Partial?'),
        'respiration_rate': fields.integer('Respiration Rate'),
        'indirect_oxymetry_spo2': fields.integer('O2 Saturation'),
        'oxygen_administration_flag': fields.boolean(
            'Patient on supplemental O2'),
        'body_temperature': fields.float('Body Temperature', digits=(2, 1)),
        'blood_pressure_systolic': fields.integer('Blood Pressure Systolic'),
        'blood_pressure_diastolic': fields.integer('Blood Pressure Diastolic'),
        'pulse_rate': fields.integer('Pulse Rate'),
        'avpu_text': fields.selection(_avpu_values, 'AVPU'),
        'mews_score': fields.integer('Mews Score'),
        'flow_rate': fields.float('Flow rate (l/min)', digits=(3, 1)),
        'concentration': fields.integer('Concentration (%)'),
        'cpap_peep': fields.integer('CPAP: PEEP (cmH2O)'),
        'niv_backup': fields.integer('NIV: Back-up rate (br/min)'),
        'niv_ipap': fields.integer('NIV: IPAP (cmH2O)'),
        'niv_epap': fields.integer('NIV: EPAP (cmH2O)'),
        'device_id': fields.many2one('nh.clinical.device.type', 'Device'),
        'order_by': fields.related(
            'activity_id', 'date_terminated', type='datetime',
            string='Date Terminated', store={
                'nh.clinical.patient.observation.ews': (
                    lambda self, cr, uid, ids, ctx: ids, ['activity_id'], 10),
                'nh.activity.data': (_data2ews_ids, ['date_terminated'], 20)
            }),
        'o2_display': fields.function(
            _get_o2_display, type='char', size=300, string='Supplemental O2'),
        'bp_display': fields.function(
            _get_bp_display, type='char', size=10, string='Blood Pressure'),
        'score_display': fields.function(
            _get_score_display, type='char', size=2, string='Score')
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
                    'condition': {
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
                    'condition': [
                        ['oxygen_administration_flag', '==', 'True']],
                    'action': 'show'
                },
                {
                    'fields': ['device_id', 'flow_rate', 'concentration',
                               'cpap_peep', 'niv_backup', 'niv_ipap',
                               'niv_epap'],
                    'condition': [
                        ['oxygen_administration_flag', '!=', 'True']],
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
            'label': 'Flow Rate (l/min)',
            'min': 0,
            'max': 100.0,
            'digits': [3, 1],
            'initially_hidden': True,
            'on_change': [
                {
                    'fields': ['concentration'],
                    'condition': [['flow_rate', '!=', '']],
                    'action': 'disable'
                },
                {
                    'fields': ['concentration'],
                    'condition': [['flow_rate', '==', '']],
                    'action': 'enable'
                }
            ]
        },
        {
            'name': 'concentration',
            'type': 'integer',
            'label': 'Concentration (%)',
            'min': 0,
            'max': 100,
            'initially_hidden': True,
            'on_change': [
                {
                    'fields': ['flow_rate'],
                    'condition': [['concentration', '!=', '']],
                    'action': 'disable'
                },
                {
                    'fields': ['flow_rate'],
                    'condition': [['concentration', '==', '']],
                    'action': 'enable'
                }
            ]
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
        """
        Checks the current state of supplemental oxygen
        :class:`device sessions<devices.nh_clinical_device_session>` on
        the related :class:`spell<base.nh_clinical_spell>`.

        It :meth:`completes<devices.nh_clinical_device_session.complete>`
        the sessions if the current NEWS does not have the oxygen
        administration flag up.

        It :meth:`completes<devices.nh_clinical_device_session.complete>`
        any session with an oxygen administration
        :class:`device type<devices.nh_clinical_device_type>` that does
        not match the NEWS device.

        It :meth:`starts<devices.nh_clinical_device_session.start>` a
        new session if the NEWS device provided does not have already
        an open one related to the spell.

        :param activity_id: :class:`activity<activity.nh_activity>` id.
        :type activity_id: int
        """
        activity_pool = self.pool['nh.activity']
        session_pool = self.pool['nh.clinical.device.session']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        device_activity_ids = activity_pool.search(cr, uid, [
            ['parent_id', '=', activity.parent_id.id],
            ['data_model', '=', 'nh.clinical.device.session'],
            ['state', 'not in', ['completed', 'cancelled']]], context=context)
        da_browse = activity_pool.browse(
            cr, uid, device_activity_ids, context=context)
        device_activity_ids = [
            da.id for da in da_browse if
            da.data_ref.device_type_id.category_id.name == 'Supplemental O2']
        if not activity.data_ref.oxygen_administration_flag:
            [activity_pool.complete(
                cr, uid, dai, context=context) for dai in device_activity_ids]
        elif activity.data_ref.device_id:
            add_device = False
            if not device_activity_ids:
                add_device = True
            else:
                device_activity_ids = [
                    da.id for da in da_browse
                    if da.data_ref.device_type_id.category_id.name !=
                    activity.data_ref.device_id.name]
                if not any([da.id
                            for da in da_browse
                            if da.data_ref.device_type_id.name ==
                            activity.data_ref.device_id.name]):
                    add_device = True
                [activity_pool.complete(
                    cr, uid, dai, context=context)
                 for dai in device_activity_ids]
            if add_device:
                device_activity_id = session_pool.create_activity(
                    cr, SUPERUSER_ID,
                    {
                        'parent_id': activity.parent_id.id
                    }, {
                        'patient_id': activity.patient_id.id,
                        'device_type_id': activity.data_ref.device_id.id,
                        'device_id': False})
                activity_pool.start(
                    cr, uid, device_activity_id, context=context)

    def submit(self, cr, uid, activity_id, data_vals=None, context=None):
        if not data_vals:
            data_vals = {}
        vals = data_vals.copy()
        if vals.get('oxygen_administration'):
            vals.update(
                {'oxygen_administration_flag':
                 vals['oxygen_administration'].get(
                     'oxygen_administration_flag')})
            del vals['oxygen_administration']
        return super(nh_clinical_patient_observation_ews, self).submit(
            cr, SUPERUSER_ID, activity_id, data_vals, context)

    def complete(self, cr, uid, activity_id, context=None):
        """
        It determines which acuity case the current observation is in
        with the stored data and responds to the different policy
        triggers accordingly defined on the ``_POLICY`` dictionary::

            {'ranges': [0, 4, 6], 'case': '0123', --> Used with bisect to
            determine the acuity case based on the score.
            'frequencies': [720, 240, 60, 30], --> frequency of recurrency
            of the NEWS observation, based on the case.
            'notifications': [...],
               Information sent to the trigger_notifications method,
               based on case.
            'risk': ['None', 'Low', 'Medium', 'High']} --> Clinical risk
            of the patient, based on case.

        All the case based lists work in a simple way:
        list[case] --> value used

        After the policy triggers take place the activity is `completed`
        and a new NEWS activity is created. Then the case based
        `frequency` is applied, effectively scheduling it.

        In the case of having a `partial` observation we won't have a new
        frequency so the new activity is scheduled to the same time the
        one just `completed` was, as the need for a complete observation
        is still there.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        groups_pool = self.pool['res.groups']
        api_pool = self.pool['nh.clinical.api']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)

        hcagroup_ids = groups_pool.search(
            cr, uid, [('users', 'in', [uid]),
                      ('name', '=', 'NH Clinical HCA Group')])
        nursegroup_ids = groups_pool.search(
            cr, uid, [('users', 'in', [uid]),
                      ('name', '=', 'NH Clinical Nurse Group')])
        group = nursegroup_ids and 'nurse' or hcagroup_ids and 'hca' or False
        spell_activity_id = activity.parent_id.id
        self.handle_o2_devices(cr, uid, activity.id, context=context)

        # trigger notifications
        if not activity.data_ref.is_partial:
            notifications = self.get_notifications(cr, uid, activity)
            if len(notifications) > 0:
                api_pool.trigger_notifications(cr, uid, {
                    'notifications': notifications,
                    'parent_id': spell_activity_id,
                    'creator_id': activity.id,
                    'patient_id': activity.data_ref.patient_id.id,
                    'model': self._name,
                    'group': group
                }, context=context)

        res = super(nh_clinical_patient_observation_ews, self).complete(
            cr, uid, activity_id, context)
        self.create_next_obs(cr, uid, activity, context)
        return res

    @api.model
    def create_next_obs(self, previous_obs_activity):
        """
        Creates a new observation and activity based on a given closed
        observation activity.

        If the previous observation is partial, the new observation is
        scheduled for the same time as the old one, in other words, there is a
        good chance it will be due right away. If the previous observation is
        not a partial then it will be scheduled based on the frequency implied
        by the clinical risk of the previous observation.

        It only makes sense to create the next observation activity based on
        an activity for an observation of the same type as this one. An
        exception will be raised if the same type of activity is not passed.

        If the observation is neither completed or cancelled then it is still
        open and a new observation activity should not be created, thus an
        exception will be raised.

        :param previous_obs_activity:
        :return:
        """
        if previous_obs_activity.data_model != self._name:
            raise TypeError(
                "Trying to create a new observation and activity but the given"
                " previous activity is not for the same type of observation."
            )
        if previous_obs_activity.state not in ['completed', 'cancelled']:
            raise ValueError(
                "Trying to create a new observation and activity but the given"
                " previous activity is not closed. Only one open "
                "observation should exist at a time."
            )

        spell_activity_id = previous_obs_activity.parent_id.id
        next_obs_activity_id = self.create_activity(
            {'creator_id': previous_obs_activity.id,
             'parent_id': spell_activity_id},
            {'patient_id': previous_obs_activity.data_ref.patient_id.id}
        )

        if previous_obs_activity.data_ref.is_partial:
            activity_pool = self.pool['nh.activity']
            next_obs_activity = \
                activity_pool.browse(self.env.cr, self.env.uid,
                                     next_obs_activity_id)
            self.create_next_obs_after_partial(
                previous_obs_activity, next_obs_activity
            )
        else:
            case = self.get_case(previous_obs_activity.data_ref)
            self.change_activity_frequency(
                previous_obs_activity.data_ref.patient_id.id,
                self._name, case
            )

    @api.model
    def create_next_obs_after_partial(self, partial_obs_activity,
                                      next_obs_activity):
        activity_pool = self.pool['nh.activity']
        patient_id = partial_obs_activity.data_ref.patient_id.id

        patient_refusal_in_effect = \
            self.is_patient_refusal_in_effect(patient_id)
        if patient_refusal_in_effect:
            date_scheduled = self.get_date_scheduled_for_refusal(
                partial_obs_activity, next_obs_activity
            )

        else:
            date_scheduled = partial_obs_activity.date_scheduled

        activity_pool.schedule(
            self.env.cr, self.env.uid, next_obs_activity.id,
            date_scheduled=date_scheduled, context=self.env.context
        )

    @api.model
    def get_date_scheduled_for_refusal(self, previous_obs_activity,
                                       next_obs_activity):
        placement_model = self.env['nh.clinical.patient.placement']

        frequency = previous_obs_activity.data_ref.frequency
        date_completed = previous_obs_activity.date_terminated
        spell_activity_id = next_obs_activity.spell_activity_id.id

        if self.patient_monitoring_exception_before_refusals(
                spell_activity_id):
            case = 'Obs Restart'
        elif frequency == 15 \
                and len(placement_model.get_placement_activities_for_spell(
                    spell_activity_id
                )) > 1 \
                and self.placement_before_refusals(spell_activity_id):
            case = 'Transfer'
        else:
            last_full_obs_activity = self.get_last_full_obs_activity(
                next_obs_activity.parent_id.id
            )
            if last_full_obs_activity:
                case = self.get_case(last_full_obs_activity.data_ref)
            else:
                case = 'Unknown'

        refusal_adjusted_frequency = \
            next_obs_activity.data_ref.adjust_frequency_for_patient_refusal(
                case, frequency
            )

        date_scheduled = dt.strptime(date_completed, dtf) \
            + timedelta(minutes=refusal_adjusted_frequency)
        return date_scheduled

    def can_decrease_obs_frequency(self, cr, uid, patient_id,
                                   threshold_value,
                                   context=None):
        spell_pool = self.pool['nh.clinical.spell']
        spell_start_date = spell_pool.get_spell_start_date(cr, uid, patient_id,
                                                           context=context)
        last_obs = self.get_last_obs(cr, uid, patient_id)

        present = dt.strptime(last_obs['date_terminated'], dtf) \
            if last_obs else dt.now()
        spell_start_delta = present - spell_start_date
        return spell_start_delta.days >= threshold_value

    def get_notifications(self, cr, uid, activity):
        """
        Get notifications that should be triggered upon completion of the
        passed activity for an EWS observation.

        :param activity: activity referencing an EWS observation
        :return: a list of dictionaries representing notifications
        :rtype: list
        """
        case = self.get_case(activity.data_ref)
        return self._POLICY['notifications'][case]

    def get_case(self, observation):
        """
        Return an integer based on the clinical risk of the observation
        to be used as an index when accessing elements of :py:attr:`_POLICY`.

        :param observation: EWS observation
        :return: case
        :rtype: int
        """
        case = int(self._POLICY['case'][bisect.bisect_left(
            self._POLICY['ranges'], observation.score)])
        return 2 if observation.three_in_one and case < 3 else case

    def change_activity_frequency(self, cr, uid, patient_id, name, case,
                                  context=None):
        """
        Convenience that allows you to pass a 'case' instead of a 'frequency'
        and the method will do the lookup for you.

        See :method:`nh_observations.nh_clinical_extension
        .nh_clinical_api_extension.change_activity_frequency`.

        :param cr:
        :param uid:
        :param patient_id:
        :param name:
        :param case:
        :param context:
        :return:
        """
        api_pool = self.pool['nh.clinical.api']
        frequency = self._POLICY['frequencies'][case]
        return api_pool.change_activity_frequency(
            cr, uid, patient_id, name, frequency, context=context
        )

    # Ideally this method would be in `nh_observations` as it could apply
    # to many different types of observation, but it is difficult to test
    # there because `nh.clinical.patient.observation` is an abstract
    # model and so you cannot create records of it to use in tests.
    @api.model
    def get_last_full_obs_activity(self, spell_activity_id):
        """
        Gets the most recent full observation.

        :param spell_activity_id:
        :type spell_activity_id: int
        :return: observation activity
        :rtype: nh.activity
        """
        domain = [
            ('spell_activity_id', '=', spell_activity_id),
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('state', '=', 'completed')
        ]
        activity_model = self.env['nh.activity']
        obs_activities = activity_model.search(
            domain, order='create_date desc, id desc'
        )
        for obs_activity in obs_activities:
            if obs_activity.data_ref.is_partial is False:
                return obs_activity
        return None

    @api.multi
    def adjust_frequency_for_patient_refusal(self, case, frequency=None):
        refusal_adjusted_frequency = \
            self.get_adjusted_frequency_for_patient_refusal(case, frequency)
        if refusal_adjusted_frequency != self.frequency:
            self.frequency = refusal_adjusted_frequency
        return refusal_adjusted_frequency

    def get_adjusted_frequency_for_patient_refusal(self, case, frequency=None):
        if type(case) is str:
            return frequencies.PATIENT_REFUSAL_ADJUSTMENTS[case][0]
        else:
            risk = self.convert_case_to_risk(case)
            return frequencies.PATIENT_REFUSAL_ADJUSTMENTS[risk][frequency][0]

    def create_activity(self, cr, uid, vals_activity=None, vals_data=None,
                        context=None):
        """
        When creating a new activity of this type every other not
        `completed` or `cancelled` instance related to the same patient
        will be automatically cancelled.

        :returns: :class:`activity<activity.nh_activity>` id.
        :rtype: int
        """
        if not vals_activity:
            vals_activity = {}
        if not vals_data:
            vals_data = {}
        activity_pool = self.pool['nh.activity']
        domain = [['patient_id', '=', vals_data['patient_id']],
                  ['data_model', '=', self._name],
                  ['state', 'in', ['new', 'started', 'scheduled']]]
        ids = activity_pool.search(cr, SUPERUSER_ID, domain, context=context)
        for aid in ids:
            activity_pool.cancel(cr, SUPERUSER_ID, aid, context=context)
        return super(
            nh_clinical_patient_observation_ews, self).create_activity(
            cr, uid, vals_activity, vals_data, context=context)

    # TODO EOBS-704: Make 'get_form_description' generic and move from ews.py
    # to observations.py
    def get_form_description(self, cr, uid, patient_id, context=None):
        """
        Returns a description in dictionary format of the input fields
        that would be required in the user gui to submit the
        observation.

        :param patient_id: :class:`patient<base.nh_clinical_patient>` id
        :type patient_id: int
        :returns: a list of dictionaries
        :rtype: list
        """
        device_pool = self.pool['nh.clinical.device.type']
        o2target_pool = self.pool['nh.clinical.patient.o2target']
        o2level_pool = self.pool['nh.clinical.o2level']
        fd = copy.deepcopy(self._form_description)
        # Find the O2 target
        o2level_id = o2target_pool.get_last(
            cr, uid, patient_id, context=context)
        if not o2level_id:
            o2target = False
        else:
            o2level = o2level_pool.browse(cr, uid, o2level_id, context=context)
            o2target = o2level.name
        # Find O2 devices
        device_ids = device_pool.search(
            cr, uid, [('category_id.name', '=', 'Supplemental O2')],
            context=context)
        device_selection = [[d, device_pool.read(
            cr, uid, d, ['name'],
            context=context)['name']] for d in device_ids]

        for field in fd:
            if field['name'] == 'indirect_oxymetry_spo2' and o2target:
                field['secondary_label'] = 'Target: {0}'.format(o2target)
            if field['name'] == 'device_id':
                field['selection'] = device_selection
        return fd

    def get_last_case(self, cr, uid, patient_id, context=None):
        """
        Checks for the last completed NEWS for the provided
        :class:`patient<base.nh_clinical_patient>` and returns the
        acuity case::

            0 - No Risk
            1 - Low Risk
            2 - Medium Risk
            3 - High Risk

        :returns: ``False`` or the acuity case
        :rtype: int
        """
        last_obs_activity = self.get_last_obs_activity(cr, uid, patient_id)
        if not last_obs_activity:
            return False
        case = int(self._POLICY['case'][bisect.bisect_left(
            self._POLICY['ranges'], last_obs_activity.data_ref.score)])
        case = 2 if last_obs_activity.data_ref.three_in_one and case < 3 \
            else case
        return case

    def patient_has_spell(self, cr, uid, patient_id):
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id)
        return bool(spell_id)
