# -*- coding: utf-8 -*-
"""
``observations.py`` defines a set of activity types to record basic
medical observations. They have in common their simple logic and data as
none of them should require complex policies to be implemented.

The abstract definition of an observation from which all other
observations inherit is also included here.
"""

from openerp.osv import orm, fields, osv
from openerp.addons.nh_observations.parameters import frequencies
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import SUPERUSER_ID
import copy

import logging
_logger = logging.getLogger(__name__)


class nh_clinical_patient_observation(orm.AbstractModel):
    """
    Abstract representation of what a medical observation is. Contains
    common information that all observations will have but does not
    represent any entity itself, so it basically acts as a template
    for every other observation.
    """
    _name = 'nh.clinical.patient.observation'
    _inherit = ['nh.activity.data']
    _required = []  # fields required for complete observation
    _num_fields = []  # numeric fields we want to be able to read as NULL instead of 0
    _partial_reasons = [
        ['patient_away_from_bed', 'Patient away from  bed'],
        ['patient_refused', 'Patient refused'],
        ['emergency_situation', 'Emergency situation'],
        ['doctors_request', 'Doctor\'s request']
    ]
    
    def _is_partial(self, cr, uid, ids, field, args, context=None):
        ids = ids if isinstance(ids, (tuple, list)) else [ids]
        if not self._required:
            return {id: False for id in ids}
        res = {}
        for obs in self.read(cr, uid, ids, ['none_values'], context):
            res.update({obs['id']: bool(set(self._required) & set(eval(obs['none_values'])))})
        return res

    def _is_partial_search(self, cr, uid, obj, name, args, domain=None, context=None):
        arg1, op, arg2 = args[0]
        arg2 = bool(arg2)
        all_ids = self.search(cr, uid, [])
        is_partial_map = self._is_partial(cr, uid, all_ids, 'is_partial', None, context=context)
        partial_ews_ids = [key for key, value in is_partial_map.items() if value]
        if arg2:
            return [('id', 'in', [ews_id for ews_id in all_ids if ews_id in partial_ews_ids])]
        else:
            return [('id', 'in', [ews_id for ews_id in all_ids if ews_id not in partial_ews_ids])]

    def _partial_observation_has_reason(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            if o.is_partial and not o.partial_reason:
                return False
        return True

    def calculate_score(self, data):
        return False

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id)
        res = super(nh_clinical_patient_observation, self).complete(cr, uid, activity_id, context)
        if activity.data_ref.is_partial and not activity.data_ref.partial_reason:
            raise osv.except_osv("Observation Error!", "Missing partial observation reason")
        if not activity.date_started:
            self.pool['nh.activity'].write(cr, uid, activity_id, {'date_started': activity.date_terminated}, context=context)
        return res
    
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'is_partial': fields.function(_is_partial, type='boolean', fnct_search=_is_partial_search,
                                      string='Is Partial?'),
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
        """
        Checks for ``null`` numeric values before writing to the
        database and removes them from the ``vals`` dictionary to avoid
        Odoo writing incorrect ``0`` values and then calls
        :meth:`create<openerp.models.Model.create>`.

        :returns: :mod:`observation<observations.nh_clinical_patient_observation>` id.
        :rtype: int
        """
        none_values = list(set(self._required) - set(vals.keys()))
        null_values = list(set(self._num_fields) - set(vals.keys()))
        vals.update({'none_values': none_values, 'null_values': null_values})
        return super(nh_clinical_patient_observation, self).create(cr, uid, vals, context)
    
    def create_activity(self, cr, uid, activity_vals={}, data_vals={}, context=None):
        assert data_vals.get('patient_id'), "patient_id is a required field!"
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(cr, SUPERUSER_ID, data_vals['patient_id'], context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        if not spell_id:
            raise osv.except_osv("Observation Error!", "Current spell is not found for patient_id: %s" %  data_vals['patient_id'])
        activity_vals.update({'parent_id': spell.activity_id.id})
        return super(nh_clinical_patient_observation, self).create_activity(cr, uid, activity_vals, data_vals, context)      
                
    def write(self, cr, uid, ids, vals, context=None):
        """
        Checks for ``null`` numeric values before writing to the
        database and removes them from the ``vals`` dictionary to avoid
        Odoo writing incorrect ``0`` values and then calls
        :meth:`write<openerp.models.Model.write>`.

        If the ``frequency`` is updated, the observation will be
        rescheduled accordingly.

        :returns: ``True``
        :rtype: bool
        """
        ids = ids if isinstance(ids, (tuple, list)) else [ids]
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
        """
        Calls :meth:`read<openerp.models.Model.read>` and then looks for
        potential numeric values that might be actually ``null`` instead
        of ``0`` (as Odoo interprets every numeric value as ``0`` when
        it finds ``null`` in the database) and fixes the return value
        accordingly.

        :returns: dictionary with the read values
        :rtype: dict
        """
        nolist = False
        if not isinstance(ids, list):
            ids = [ids]
            nolist = True
        if fields and 'null_values' not in fields:
            fields.append('null_values')
        res = super(nh_clinical_patient_observation, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        if res:
            for d in res:
                for key in d.keys():
                    if key in self._columns and self._columns[key]._type == 'float':
                        if not self._columns[key].digits:
                            _logger.warn("You might be reading a wrong float from the DB. Define digits attribute for float columns to avoid this problem.")
                        else:
                            d[key] = round(d[key], self._columns[key].digits[1])
            for obs in isinstance(res, (tuple, list)) and res or [res]:
                for nv in eval(obs['null_values'] or '{}'):
                    if nv in obs.keys():
                        obs[nv] = False
            res = res[0] if nolist and len(res) > 0 else res
        return res

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        """
        Looks for the related :class:`spell<base.nh_clinical_spell>` and
        gets its current location.

        :param activity_id: :class:`activity<activity.nh_activity>` id
        :type activity_id: int
        :returns: :class:`location<base.nh_clinical_location>` id
        :rtype: int
        """
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id, context=context)
        if spell_id:
            spell = spell_pool.browse(cr, uid, spell_id, context=context)
            return spell.activity_id.location_id.id
        else:
            return False

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
        return self._form_description


class nh_clinical_patient_observation_height(orm.Model):
    """
    Represents the action of measuring a
    :class:`patient<base.nh_clinical_patient>` height.
    """
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
    """
    Represents the action of measuring a
    :class:`patient<base.nh_clinical_patient>` weight.
    """
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
            'min': 35.0,
            'max': 330.0,
            'digits': [3, 1],
            'initially_hidden': False
        }
    ]

    def schedule(self, cr, uid, activity_id, date_scheduled=None, context=None):
        """
        If a specific ``date_scheduled`` parameter is not specified.
        The `_POLICY['schedule']` dictionary value will be used to find
        the closest time to the current time from the ones specified
        (0 to 23 hours)

        Then it will call :meth:`schedule<activity.nh_activity.schedule>`

        :returns: ``True``
        :rtype: bool
        """
        if not date_scheduled:
            hour = td(hours=1)
            schedule_times = []
            for s in self._POLICY['schedule']:
                schedule_times.append(dt.now().replace(hour=s[0], minute=s[1], second=0, microsecond=0))
            date_schedule = dt.now().replace(minute=0, second=0, microsecond=0) + td(hours=2)
            utctimes = [fields.datetime.utc_timestamp(cr, uid, t, context=context) for t in schedule_times]
            while all([date_schedule.hour != date_schedule.strptime(ut, DTF).hour for ut in utctimes]):
                date_schedule += hour
            date_scheduled = date_schedule.strftime(DTF)
        return super(nh_clinical_patient_observation_weight, self).schedule(cr, uid, activity_id, date_scheduled, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        """
        Calls :meth:`complete<activity.nh_activity.complete>` and then
        creates and schedules a new weight observation if the current
        :mod:`weight monitoring<parameters.nh_clinical_patient_weight_monitoring>`
        parameter is ``True``.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)

        res = super(nh_clinical_patient_observation_weight, self).complete(cr, uid, activity_id, context)

        activity_pool.cancel_open_activities(cr, uid, activity.parent_id.id, self._name, context=context)

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

            activity_pool.schedule(cr, uid, next_activity_id, context=context)
        return res


class nh_clinical_patient_observation_blood_product(orm.Model):
    """
    Represents the action of measuring any of the
    :class:`patient<base.nh_clinical_patient>` blood components.
    Usually related to blood transfusions.
    """
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
    """
    Represents the action of measuring a
    :class:`patient<base.nh_clinical_patient>` blood sugar concentration.
    """
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


class nh_clinical_patient_observation_pain(orm.Model):
    """
    Represents the action of subjectively measuring a
    :class:`patient<base.nh_clinical_patient>` pain on a scale from
    1 to 10.
    """
    _name = 'nh.clinical.patient.observation.pain'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['rest_score', 'movement_score']
    _num_fields = ['rest_score', 'movement_score']
    _description = "Pain Score Observation"
    _columns = {
        'rest_score': fields.integer('Pain Score at rest'),
        'movement_score': fields.integer('Pain Score on movement')
    }
    _form_description = [
        {
            'name': 'rest_score',
            'type': 'integer',
            'label': 'Pain Score at rest (0 to 10)',
            'min': 0,
            'max': 10,
            'initially_hidden': False
        },
        {
            'name': 'movement_score',
            'type': 'integer',
            'label': 'Pain Score on movement (0 to 10)',
            'min': 0,
            'max': 10,
            'initially_hidden': False
        }
    ]


class nh_clinical_patient_observation_urine_output(orm.Model):
    """
    Represents the action of measuring a
    :class:`patient<base.nh_clinical_patient>` urine output per hour.
    """
    _name = 'nh.clinical.patient.observation.urine_output'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['urine_output']
    _description = "Urine Output Observation"
    _columns = {
        'urine_output': fields.integer('Urine Output')
    }
    _form_description = [
        {
            'name': 'urine_output',
            'type': 'integer',
            'label': 'Urine Output (ml/hour)',
            'min': 0,
            'max': 1000,
            'initially_hidden': False
        }
    ]

    def get_form_description(self, cr, uid, patient_id, context=None):
        """
         Returns a description in dictionary format of the input fields
         that would be required in the user gui to submit this
         observation.

         Adds an additional label to the ``urine_output`` field with
         the :mod:`urine output target<parameters.nh_clinical_patient_urine_output_target>`
         if the :class:`patient<base.nh_clinical_patient>` has one.

        :param patient_id: :class:`patient<base.nh_clinical_patient>` id
        :type patient_id: int
        :returns: a list of dictionaries
        :rtype: list
        """
        uotarget_pool = self.pool['nh.clinical.patient.uotarget']
        units = {1: 'ml/hour', 2: 'L/day'}
        fd = copy.deepcopy(self._form_description)
        # Find the Urine Output target
        uotarget = uotarget_pool.current_target(cr, uid, patient_id, context=context)

        for field in fd:
            if field['name'] == 'urine_output' and uotarget:
                field['secondary_label'] = 'Target: {0} {1}'.format(uotarget[0], units[uotarget[1]])
        return fd

class nh_clinical_patient_observation_bowels_open(orm.Model):
    """
    Represents the action of observing if a
    :class:`patient<base.nh_clinical_patient>` has the bowels open or
    not.
    """
    _name = 'nh.clinical.patient.observation.bowels_open'
    _inherit = ['nh.clinical.patient.observation']
    _required = ['bowels_open']
    _description = "Bowels Open Flag"
    _columns = {
        'bowels_open': fields.selection([['yes', 'Yes'], ['no', 'No']], 'Bowels Open')
    }
    _form_description = [
        {
            'name': 'bowels_open',
            'type': 'selection',
            'label': 'Bowels Open',
            'selection': [['yes', 'Yes'], ['no', 'No']],
            'initially_hidden': False
        }
    ]
