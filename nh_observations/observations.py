# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
"""
``observations.py`` defines a set of activity types to record basic
medical observations. They have in common their simple logic and data as
none of them should require complex policies to be implemented.

The abstract definition of an observation from which all other
observations inherit is also included here.
"""
import copy
import logging
from datetime import datetime as dt, timedelta as td

from openerp import SUPERUSER_ID, api
from openerp.addons.nh_observations import frequencies
from openerp.osv import orm, fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

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
    # numeric fields we want to be able to read as NULL instead of 0
    _num_fields = []
    _partial_reasons = [
        ['patient_away_from_bed', 'Patient away from  bed'],  # TODO 2 spaces?
        ['refused', 'Refused'],
        ['emergency_situation', 'Emergency situation'],
        ['doctors_request', 'Doctor\'s request']
    ]

    def _is_partial(self, cr, uid, ids, field, args, context=None):
        ids = ids if isinstance(ids, (tuple, list)) else [ids]
        if not self._required:
            return {id: False for id in ids}
        res = {}
        for obs in self.read(cr, uid, ids, ['none_values'], context):
            res.update(
                {obs['id']: bool(set(self._required) &
                                 set(eval(obs['none_values'])))})
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
        res = super(nh_clinical_patient_observation, self).complete(
            cr, uid, activity_id, context)
        if activity.data_ref.is_partial and not \
                activity.data_ref.partial_reason:
            raise osv.except_osv("Observation Error!",
                                 "Missing partial observation reason")
        if not activity.date_started:
            self.pool['nh.activity'].write(
                cr, uid, activity_id,
                {'date_started': activity.date_terminated}, context=context)
        return res

    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient',
                                      required=True),
        'is_partial': fields.function(_is_partial, type='boolean',
                                      fnct_search=_is_partial_search,
                                      string='Is Partial?'),
        'none_values': fields.text('Non-updated required fields'),
        'null_values': fields.text('Non-updated numeric fields'),
        'frequency': fields.selection(frequencies.as_list(), 'Frequency'),
        'partial_reason': fields.selection(_partial_reasons,
                                           'Reason if partial observation')
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

        :returns: ``nh_clinical_patient_observation`` id.
        :rtype: int
        """
        none_values = list(set(self._required) - set(vals.keys()))
        null_values = list(set(self._num_fields) - set(vals.keys()))
        vals.update({'none_values': none_values, 'null_values': null_values})
        return super(nh_clinical_patient_observation, self).create(
            cr, uid, vals, context)

    def create_activity(self, cr, uid, activity_vals=None,
                        data_vals=None, context=None):
        if not activity_vals:
            activity_vals = {}
        if not data_vals:
            data_vals = {}
        assert data_vals.get('patient_id'), "patient_id is a required field!"
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(
            cr, SUPERUSER_ID, data_vals['patient_id'], context=context)
        spell = spell_pool.browse(cr, uid, spell_id, context=context)
        if not spell_id:
            raise osv.except_osv(
                "Observation Error!",
                "Current spell is not found for patient_id: %s"
                % data_vals['patient_id'])
        activity_vals.update({'parent_id': spell.activity_id.id})
        return super(nh_clinical_patient_observation, self).create_activity(
            cr, uid, activity_vals, data_vals, context=context)

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
            return super(nh_clinical_patient_observation, self).write(
                cr, uid, ids, vals, context)
        for obs in self.read(
                cr, uid, ids, ['none_values', 'null_values'], context=context):
            none_values = list(
                set(eval(obs['none_values'])) - set(vals.keys()))
            null_values = list(
                set(eval(obs['null_values'])) - set(vals.keys()))
            vals.update(
                {'none_values': none_values, 'null_values': null_values})
            super(nh_clinical_patient_observation, self).write(
                cr, uid, obs['id'], vals, context)
        if 'frequency' in vals:
            activity_pool = self.pool['nh.activity']
            for obs in self.browse(cr, uid, ids, context=context):
                # TODO Is it right that updating the frequency will
                # automatically update the date_scheduled to
                # create_date + frequency?
                scheduled = (dt.strptime(
                    obs.activity_id.create_date, DTF)+td(
                    minutes=vals['frequency'])).strftime(DTF)
                activity_pool.schedule(
                    cr, uid, obs.activity_id.id, date_scheduled=scheduled,
                    context=context)
        return True

    def read(self, cr, uid, ids, fields=None, context=None,
             load='_classic_read'):
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
        res = super(nh_clinical_patient_observation, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)
        if res:
            for d in res:
                for key in d.keys():
                    if key in self._columns \
                            and self._columns[key]._type == 'float':
                        if not self._columns[key].digits:
                            _logger.warn(
                                "You might be reading a wrong float from the "
                                "DB. Define digits attribute for float columns"
                                " to avoid this problem.")
                        else:
                            d[key] = round(
                                d[key], self._columns[key].digits[1])
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
        spell_id = spell_pool.get_by_patient_id(
            cr, uid, patient_id, context=context)
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

    @classmethod
    def get_open_obs_search_domain(cls, spell_activity_id):
        return [
            ('data_model', '=', cls._name),
            ('parent_id', '=', spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled']),
        ]

    def patient_has_spell(self, cr, uid, patient_id):
        spell_pool = self.pool['nh.clinical.spell']
        spell_id = spell_pool.get_by_patient_id(cr, uid, patient_id)
        return spell_id

    # TODO These check the last activity which should always be refused.
    # May be able to pass an activity id and work back from there.
    @api.model
    def patient_monitoring_exception_before_refusals(self, spell_activity_id):
        obs_activity = self.get_open_obs_activity(spell_activity_id)
        # Latest activity may be an open obs.
        if obs_activity.state not in ['completed', 'cancelled']:
            obs_activity = self.get_previous_obs_activity(obs_activity)

        # Keep iterating until we get the first refusal.
        while True:
            if not obs_activity or not obs_activity.creator_id:
                return False

            creator_activity = \
                self.get_previous_obs_activity(obs_activity)

            if creator_activity.data_model \
                    == 'nh.clinical.patient.observation.ews' \
                    and creator_activity.data_ref.partial_reason == 'refused':
                obs_activity = creator_activity
                continue
            # Because the first condition failed we know the creator of the
            # current refused obs activity is not a refused obs activity
            # itself.
            # If it is a patient monitoring exception then it must be one that
            # spawned the current refused obs activity and therefore there was
            # indeed a patient monitoring exception immediately prior to the
            # refusals.
            elif creator_activity.data_model == \
                    'nh.clinical.patient_monitoring_exception':
                return True
            return False

    @api.model
    def placement_before_refusals(self, spell_activity_id):
        obs_activity = self.get_open_obs_activity(spell_activity_id)

        # Keep iterating until we get the first refusal.
        while True:
            if not obs_activity or not obs_activity.creator_id:
                return False

            creator_activity = \
                self.get_previous_obs_activity(obs_activity)

            if creator_activity.data_model \
                    == 'nh.clinical.patient.observation.ews' \
                    and creator_activity.data_ref.partial_reason == 'refused':
                obs_activity = creator_activity
                continue
            # Because the first condition failed we know the creator of the
            # current refused obs activity is not a refused obs activity
            # itself.
            # If it is a patient monitoring exception then it must be one that
            # spawned the current refused obs activity and therefore there was
            # indeed a patient monitoring exception immediately prior to the
            # refusals.
            elif creator_activity.data_model == \
                    'nh.clinical.patient.placement':
                return True
            return False

    @api.model
    def get_previous_obs_activity(self, obs_activity):
        activity_pool = self.pool['nh.activity']
        previous_obs_activity_id = obs_activity.creator_id.id
        return activity_pool.browse(
            self.env.cr, self.env.uid, previous_obs_activity_id
        )

    @api.model
    def get_next_obs_activity(self, obs_activity, data_model):
        """
        When one observation activity is completed it triggers the creation of
        another one, this method returns the observation activity triggered by
        the given one.

        :param obs_activity:
        :type obs_activity: 'nh.activity' record
        :param data_model:
        :type data_model: str
        :return:
        :rtype: 'nh.activity' record
        """
        activity_pool = self.pool['nh.activity']
        cr, uid, context = self.env.cr, self.env.uid, self._context
        domain = [
            ['creator_id', '=', obs_activity.id],
            ['data_model', '=', data_model]
        ]
        next_obs_id = activity_pool.search(cr, uid, domain, context=context)
        if next_obs_id:
            next_obs_id = next_obs_id[0]
        else:
            return False
        return activity_pool.browse(cr, uid, next_obs_id, context=context)

    @api.model
    def get_first_obs_created_after_datetime(
            self, spell_activity_id, date_time):
        """
        Gets the first observation created after the passed datetime.

        :param spell_activity_id:
        :type spell_activity_id: int
        :param date_time:
        :type date_time: str
        :return:
        """
        activity_model = self.env['nh.activity']
        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', spell_activity_id),
            ('create_date', '>=', date_time)
        ]
        return activity_model.search(domain, limit=1, order='create_date asc')

    @api.model
    def get_open_obs_activity(self, spell_activity_id):
        """
        Gets a list of all 'open' activities.
        'Open' is anything that is not 'completed' or 'cancelled'.

        As far as I know there is not yet a situation where there should be
        more than one observation that is open but there may be in the future.
        It is up to the caller to check they are happy with the length of the
        returned list.

        :return: Search results for open EWS observations.
        :rtype: list
        """
        domain = self.get_open_obs_search_domain(spell_activity_id)
        activity_model = self.env['nh.activity']
        return activity_model.search(domain)

    @api.model
    def get_open_obs(self, spell_id):
        return self.get_open_obs_activity(spell_id).data_ref

    def get_last_obs_activity(self, cr, uid, patient_id, context=None):
        """ Get the activity for the last full observation made for the given
        patient_id.

        :param cr:
        :param uid:
        :param patient_id:
        :type patient_id: int
        :param context:
        :return: ``False``
        or :class:`activity<nhclinical.nh_activity.activity.nh_activity>`
        """
        # No ongoing spell to get an obs for so just return straight away.
        if not self.patient_has_spell(cr, uid, patient_id):
            return False
        domain = [['patient_id', '=', patient_id],
                  ['data_model', '=', self._name],
                  ['state', '=', 'completed'],
                  ['parent_id.state', '=', 'started']]

        activity_pool = self.pool['nh.activity']
        ews_ids = activity_pool.search(
            cr, uid, domain, order='date_terminated desc, sequence desc',
            context=context)
        if ews_ids:
            return activity_pool.browse(cr, uid, ews_ids[0], context=context)
        else:
            return False

    def get_last_obs(self, cr, uid, patient_id, context=None):
        """ Get the last observation made for the given patient_id.

        :param cr:
        :param uid:
        :param patient_id:
        :type patient_id: int
        :param context:
        :return: ``False`` or :class:`observation<openeobs.nh_observations.
        observations.nh_clinical_patient_observation>`
        """
        last_obs_activity = self.get_last_obs_activity(cr, uid, patient_id)
        if last_obs_activity:
            return last_obs_activity.data_ref

    @api.model
    def is_last_obs_refused(self, patient_id):
        """
        Check if the last completed observation was a partial with reason
        'refused'.

        :param patient_id:
        :return:
        """
        last_obs = self.get_last_obs(patient_id)
        return True if last_obs.partial_reason == 'refused' else False

    # TODO EOBS-811: Duplication between Python methods and SQL views
    @api.model
    def full_observation_since_refused(self, obs_activity):
        """
        Work forwards chronologically from the passed observation activity to
        see if any full observations are encountered along the way.

        :param obs_activity:
        :type obs_activity: nh_activity
        :return:
        :rtype: bool
        """
        refused = False
        while True:
            if not obs_activity:
                return False

            if not obs_activity.data_ref.partial_reason \
                    and obs_activity.state in ['completed', 'cancelled']:
                return True

            if not refused \
                    and obs_activity.data_ref.partial_reason != 'refused':
                return False

            child_activity = \
                self.get_next_obs_activity(obs_activity, self._name)

            if not child_activity:
                if obs_activity.state not in ['completed', 'cancelled']:
                    return False

            obs_activity = child_activity
            refused = True

    # TODO EOBS-811: Duplication between Python methods and SQL views
    @api.model
    def patient_refusal_in_effect(self, patient_id):
        """
        Uses the passed patient_id to look up their spell and then determine if
        a refusal is in effect. You might also see this phrased as a patient
        having a 'refused' status.

        :param patient_id:
        :return: True if a patient refusal is in effect for patient's spell.
        :rtype: bool
        """
        cr, uid, context = self._cr, self._uid, self._context
        activity_pool = self.pool['nh.activity']
        spell_activity_ids = activity_pool.search(
            cr, uid, [
                ['data_model', '=', 'nh.clinical.spell'],
                ['state', '=', 'started'],
                ['patient_id', '=', patient_id],
            ], context=context)

        # If there's no spell there can't be a refusal in effect.
        if not spell_activity_ids:
            return False

        spell_activity_id = spell_activity_ids[0]
        spell_activity = activity_pool.browse(cr, uid, spell_activity_id)
        spell_id = spell_activity.data_ref.id
        spell_pool = self.pool['nh.clinical.spell']

        # If a patient monitoring exception is in effect there can't be a
        # refusal in effect.
        if spell_pool.patient_monitoring_exception_in_effect(
            cr, uid, spell_id, context=context
        ):
            return False

        refused_obs_domain = [
            ['is_partial', '=', True],
            ['patient_id', '=', patient_id],
            ['partial_reason', '=', 'refused']
        ]
        refused_obs = self.search(refused_obs_domain)

        # If there aren't any refused obs for the spell there can't be a
        # refusal in effect.
        if not refused_obs:
            return False

        refused_obs = ['{0},{1}'.format(self._name, ob.id)
                       for ob in refused_obs]
        refused_obs_activities_domain = [
            ['data_model', '=', self._name],
            ['state', '=', 'completed'],
            ['parent_id', '=', spell_activity_id],
            ['data_ref', 'in', refused_obs]
        ]
        refused_obs_activity_ids = activity_pool.search(
            cr, uid, refused_obs_activities_domain,
            order='date_terminated desc, sequence desc',
            context=context)

        # If there aren't any refused obs activities there can't be a refusal
        # in effect.
        if not refused_obs_activity_ids:
            return False

        last_refused_obs_activity = activity_pool.browse(
            cr, uid, refused_obs_activity_ids[0], context=context)
        open_ob = self.get_open_obs_activity(spell_activity_id)

        # If currently open obs was triggered straight after the last refused
        # obs then refusal must still be in effect.
        if open_ob and open_ob[0] in last_refused_obs_activity.child_ids._ids:
            return True

        # If execution reaches here then there must be some things that have
        # happened in between the last refusal and the currently open obs...

        # If a transfer has happened since the last refusal,
        # then the refusal is no longer in effect.
        transfer_model = self.env['nh.clinical.patient.transfer']
        if transfer_model.patient_was_transferred_after_date(
                patient_id, last_refused_obs_activity.date_terminated):
            return False

        # If there are no full observations since the last refusal and all
        # previous conditions have passed then there can only have been
        # partials which is fine, refusal is still in effect.
        return not self.full_observation_since_refused(
            last_refused_obs_activity
        )

    # TODO EOBS-811: Duplication between Python methods and SQL views
    @api.model
    def current_patient_refusal_was_triggered_by(self,
                                                 refused_obs_activity):
        """
        Checks if the currently active patient refusal was triggered by the
        given observation activity. The observation referenced by the activity
        should therefore be one that was refused.

        :param refused_obs_activity:
        :type refused_obs_activity: 'nh.activity' record
        :return:
        :rtype: bool
        """
        activity_model = self.env['nh.activity']
        ews_gen = self.get_child_activity(
            activity_model, refused_obs_activity, self._name,
            context=self._context
        )
        ews_activities_since_refused_obs = list(ews_gen)

        full_ews_since_refused_obs = \
            [ews_activity for ews_activity in ews_activities_since_refused_obs
             if not ews_activity.data_ref.is_partial]
        if full_ews_since_refused_obs:
            return False

        patient = refused_obs_activity.patient_id
        transfer_model = self.env['nh.clinical.patient.transfer']
        if transfer_model.patient_was_transferred_after_date(
                patient.id, refused_obs_activity.date_terminated):
            return False

        spell_model = self.env['nh.clinical.spell']
        spell_activity = spell_model.get_spell_activity_by_patient(patient)
        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        if pme_model.started_after_date(spell_activity,
                                        refused_obs_activity.date_terminated):
            return False

        return True


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

    def schedule(self, cr, uid, activity_id, date_scheduled=None,
                 context=None):
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
                schedule_times.append(
                    dt.now().replace(hour=s[0], minute=s[1],
                                     second=0, microsecond=0))
            date_schedule = dt.now().replace(
                minute=0, second=0, microsecond=0) + td(hours=2)
            utctimes = [fields.datetime.utc_timestamp(
                cr, uid, t, context=context) for t in schedule_times]
            while all([date_schedule.hour != date_schedule.strptime(
                    ut, DTF).hour for ut in utctimes]):
                date_schedule += hour
            date_scheduled = date_schedule.strftime(DTF)
        return super(nh_clinical_patient_observation_weight, self).schedule(
            cr, uid, activity_id, date_scheduled, context=context)

    def complete(self, cr, uid, activity_id, context=None):
        """
        Calls :meth:`complete<activity.nh_activity.complete>` and then
        creates and schedules a new weight observation if the current
        :mod:`monitoring<parameters.nh_clinical_patient_weight_monitoring>`
        parameter is ``True``.

        :returns: ``True``
        :rtype: bool
        """
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)

        res = super(nh_clinical_patient_observation_weight, self).complete(
            cr, uid, activity_id, context)

        activity_pool.cancel_open_activities(
            cr, uid, activity.parent_id.id, self._name, context=context)

        # create next Weight activity (schedule)
        domain = [
            ['data_model', '=', 'nh.clinical.patient.weight_monitoring'],
            ['state', '=', 'completed'],
            ['patient_id', '=', activity.data_ref.patient_id.id]
        ]
        weight_monitoring_ids = activity_pool.search(
            cr, uid, domain, order="date_terminated desc", context=context)
        monitoring_active = weight_monitoring_ids and activity_pool.browse(
            cr, uid, weight_monitoring_ids[0], context=context).data_ref.status
        if monitoring_active:
            next_activity_id = self.create_activity(
                cr, SUPERUSER_ID,
                {'creator_id': activity_id,
                 'parent_id': activity.parent_id.id},
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
         the
         :mod:`target<parameters.nh_clinical_patient_urine_output_target>`
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
        uotarget = uotarget_pool.current_target(
            cr, uid, patient_id, context=context)

        for field in fd:
            if field['name'] == 'urine_output' and uotarget:
                field['secondary_label'] = 'Target: {0} {1}'.format(
                    uotarget[0], units[uotarget[1]])
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
        'bowels_open': fields.selection([['yes', 'Yes'], ['no', 'No']],
                                        'Bowels Open')
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
