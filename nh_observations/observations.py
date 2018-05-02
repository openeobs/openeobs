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
from openerp.addons.nh_observations import fields as obs_fields
from openerp.osv import orm, fields, osv
from openerp.osv.fields import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

_logger = logging.getLogger(__name__)


class NhClinicalPatientObservation(orm.AbstractModel):
    """
    Abstract representation of what a medical observation is. Contains
    common information that all observations will have but does not
    represent any entity itself, so it basically acts as a template
    for every other observation.
    """
    _name = 'nh.clinical.patient.observation'
    _inherit = ['nh.activity.data']

    # Fields required for complete observation.
    # Also decides the order fields are displayed in the mobile view.
    _required = []
    # Numeric fields we want to be able to read as NULL instead of 0.
    _num_fields = []
    _partial_reasons = [
        ['patient_away_from_bed', 'Patient away from  bed'],  # TODO 2 spaces?
        ['refused', 'Refused'],
        ['emergency_situation', 'Emergency situation'],
        ['doctors_request', 'Doctor\'s request']
    ]

    @classmethod
    def get_description(cls, append_observation=True):
        """
        Return a label for the observation suitable for display.

        :param append_observation:
        :return:
        :rtype: str
        """
        description = \
            super(NhClinicalPatientObservation, cls).get_description()
        if append_observation:
            description += ' Observation'
        return description

    def get_obs_field_order(self):
        return self._required

    @api.multi
    def get_obs_fields(self):
        return self.env['nh.clinical.field_utils'].\
            get_obs_fields_from_model(self)

    def get_obs_field_names(self):
        obs_fields = self.get_obs_fields()
        return [field.name for field in obs_fields]

    def get_necessary_fields(self):
        obs_fields = self.get_obs_fields()
        return [field for field in obs_fields if field.necessary is True]

    def get_necessary_fields_dict(self):
        necessary_fields = self.get_necessary_fields()
        necessary_field_values = {}
        for field in necessary_fields:
            field_value = getattr(self, field.name)
            necessary_field_values[field.name] = field_value
        return necessary_field_values

    def get_partial_reason_label(self, reason):
        if not reason:
            return reason
        partial_reasons = \
            [partial_reason[0] for partial_reason in self._partial_reasons]
        reason_index = partial_reasons.index(reason)
        return self._partial_reasons[reason_index][1]

    def get_submission_message(self):
        """
        Provides a message to be displayed when the observation is submitted.

        :return:
        :rtype str
        """
        raise NotImplementedError(
            "Get submission message method not implemented for model: {}"
            .format(self._name)
        )

    def get_submission_response_data(self):
        triggered_tasks = self.get_triggered_tasks()
        response_data = {
            'related_tasks': triggered_tasks, 'status': 1
        }
        return response_data

    def get_triggered_tasks(self):
        activity_model = self.env['nh.activity']
        api_model = self.env['nh.clinical.api']

        triggered_tasks = activity_model.search(
            [('creator_id', '=', self.activity_id.id)]
        )

        def open_accessible_non_obs(activity):
            access = api_model.check_activity_access(activity.id)
            is_not_ob = \
                'nh.clinical.patient.observation' not in activity.data_model
            is_open = activity.state not in ['completed', 'cancelled']
            return access and is_open and is_not_ob

        triggered_tasks = triggered_tasks.filtered(open_accessible_non_obs)
        triggered_tasks_dict_list = triggered_tasks.read()
        return triggered_tasks_dict_list

    def _is_partial(self, cr, uid, ids, field, args, context=None):
        """
        Determine if the observations with the passed IDs are partial or not.

        :param cr:
        :param uid:
        :param ids:
        :param field:
        :param args:
        :param context:
        :return:
        :rtype: bool
        """
        ids = ids if isinstance(ids, (tuple, list)) else [ids]
        # If this type of observation has no 'required' fields (not to be
        # confused with Odoo's definition of required) then partial
        # observations are not possible. Return false for all IDs.
        if not self._required:
            return {id: False for id in ids}
        res = {}
        for obs in self.read(cr, uid, ids, ['none_values'], context):
            res.update(
                # See if any of the none values are for 'required' fields,
                # If so then return True, because any none values for required
                # fields mean a partial observation.
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

    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient',
                                      required=True),
        'is_partial': fields.function(_is_partial, type='boolean',
                                      fnct_search=_is_partial_search,
                                      string='Is Partial?'),
        'none_values': fields.text('Non-updated required fields'),
        'null_values': fields.text('Non-updated numeric fields'),
        'frequency': fields.integer('Frequency'),
        'partial_reason': fields.selection(_partial_reasons,
                                           'Reason if partial observation')
    }
    _defaults = {

    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id)
        res = super(NhClinicalPatientObservation, self).complete(
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

    def create(self, cr, uid, vals, context=None):
        """
        Checks for ``null`` numeric values before writing to the
        database and removes them from the ``vals`` dictionary to avoid
        Odoo writing incorrect ``0`` values and then calls
        :meth:`create<openerp.models.Model.create>`.

        Passing a field key with a falsey value will cause that value to be
        excluded from the partial calculation due to the logic used, so don't
        pass keys at all for fields that have not been submitted, even if they
        are using falsey values.

        :returns: ``nh_clinical_patient_observation`` id.
        :rtype: int
        """
        none_values = list(set(self._required) - set(vals.keys()))
        null_values = list(set(self._num_fields) - set(vals.keys()))
        vals.update({'none_values': none_values, 'null_values': null_values})
        return super(NhClinicalPatientObservation, self).create(
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
        return super(NhClinicalPatientObservation, self).create_activity(
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
            return super(NhClinicalPatientObservation, self).write(
                cr, uid, ids, vals, context)
        for obs in self.read(
                cr, uid, ids, ['none_values', 'null_values'], context=context):
            none_values = list(
                set(eval(obs['none_values'])) - set(vals.keys()))
            null_values = list(
                set(eval(obs['null_values'])) - set(vals.keys()))
            vals.update(
                {'none_values': none_values, 'null_values': null_values})
            super(NhClinicalPatientObservation, self).write(
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

        Rounds all floats to n decimal places, where n is the number specified
        in the digits tuple that is an attribute of the field definition on
        the model.

        :returns: dictionary with the read values
        :rtype: dict
        """
        nolist = False
        if not isinstance(ids, list):
            ids = [ids]
            nolist = True
        if fields and 'null_values' not in fields:
            fields.append('null_values')
        res = super(NhClinicalPatientObservation, self).read(
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

    @api.model
    def read_obs_for_patient(self, patient_id):
        """
        Read all observations for the patient.

        :param patient_id:
        :type patient_id: int
        :return:
        :rtype: dict
        """
        domain = [('patient_id', '=', patient_id)]
        # TODO date_terminated is not a valid field on observation?
        obs = self.search_read(domain, order='date_terminated desc, id desc')
        return obs

    @api.multi
    def read_labels(self, fields=None, load='_classic_read'):
        """
        Return a 'read-like' dictionary with field labels instead of values.

        :param fields:
        :param load:
        :return:
        :rtype: dict
        """
        obs_data = self.read(fields=fields, load=load)
        if obs_data:
            obs = obs_data if isinstance(obs_data, list) else [obs_data]
            self.convert_field_values_to_labels(obs)
        return obs_data

    def convert_field_values_to_labels(self, obs):
        """
        Convert the values in the passed dictionary to their corresponding
        labels.

        :param obs:
        :type obs: list
        """
        field_names = self.get_obs_field_names()
        for ob in obs:
            for field_name in field_names:
                if field_name in ob:
                    field_value = ob[field_name]
                    field_value_label = self.get_field_value_label(field_name,
                                                                   field_value)
                    ob[field_name] = field_value_label

    def get_field_value_label(self, field_name, field_value):
        """
        Lookup the label for the passed field value and return it.

        :param field_name:
        :type field_name: str
        :param field_value:
        :type field_value: str
        :return: Field label.
        :rtype: str
        """
        field = self._fields[field_name]
        if isinstance(field, obs_fields.Selection):
            selection = field.selection
            valid_value_tuple = \
                [valid_value_tuple for valid_value_tuple in selection
                 if valid_value_tuple[0] == field_value][0]
            return valid_value_tuple[1]
        if isinstance(field, obs_fields.Many2Many):
            related_ids = field_value
            related_model = self.env[field.comodel_name]
            return [rec.name for rec in related_model.browse(related_ids)]
        return field_value

    @api.multi
    def get_formatted_obs(self, replace_zeros=False,
                          convert_datetimes_to_client_timezone=False):
        """
        Get a dictionary of observation data formatted for display.

        :return:
        :rtype: dict
        """
        obs_dict_list = self.read_labels()

        if convert_datetimes_to_client_timezone:
            datetime_fields = ['date_terminated', 'create_date',
                               'write_date', 'date_started']
            self._convert_datetime_fields_to_client_timezone(
                obs_dict_list, datetime_fields)

        for obs_dict in obs_dict_list:
            self._replace_falsey_values(obs_dict, replace_zeros=replace_zeros)

        return obs_dict_list

    def _convert_datetime_fields_to_client_timezone(self, obs_dict_list,
                                                    datetime_fields):
        """
        Convert datetime fields in the passed list of dictionary obs data to
        the clients timezone.

        :param obs_dict_list:
        :param datetime_fields:
        :return:
        """
        for obs in obs_dict_list:
            for datetime_field_name in datetime_fields:
                date_time = obs.get(datetime_field_name)
                if date_time:
                    obs[datetime_field_name] = \
                        self._convert_datetime_to_client_timezone(date_time)

    def _convert_datetime_to_client_timezone(self, date_time):
        date_time = dt.strptime(date_time, DTF)
        date_time_new = datetime.context_timestamp(
            self.env.cr, self.env.uid, date_time,
            context=self.env.context)
        date_time_new_str = date_time_new.strftime(DTF)
        return date_time_new_str

    @staticmethod
    def _replace_falsey_values(obs_dict, replace_falses=True,
                               replace_zeros=False):
        """
        Replaces falsey values with `None`, to represent a null value.
        This is necessary because null values in the database are replaced with
        falsey values by Odoo.

        :param obs_dict:
        :param replace_falses:
        :param replace_zeros:
        :return:
        """
        for key, value in obs_dict.items():
            if replace_falses and value is False:
                obs_dict[key] = None
            if replace_zeros and value == 0:
                obs_dict[key] = None

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

    @api.model
    def get_view_description(self, form_desc):
        """
        Transform the form description into view description that can
        be used by the mobile. This will return a list of dicts similar to::

            [
                {
                    'type': 'template',
                    'template': 'nh_observation.custom_template'
                },
                {
                    'type': 'form',
                    'inputs': []
                }
            ]

        :param form_desc: List of dicts representing the inputs for the form
        :type form_desc: list
        :return: list of dicts representing view description
        """
        return [
            {
                'type': 'form',
                'inputs': [i for i in form_desc if i['type'] is not 'meta']
            }
        ]

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
    def obs_stop_before_refusals(self, spell_activity_id):
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
                    'nh.clinical.pme.obs_stop':
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
    def transferred_and_placed_before_refusals(self, refused_obs_activity):
        """
        Determine whether a transfer happened before the last set of refusals.

        :param refused_obs_activity:
        :return:
        """
        # TODO This checks for a second placement, not necessarily transfer.
        # The logic checks for placement frequency and at least 2 placements.
        # No placement is automatically created when the patient is
        # transferred so this is only valid for when they are actually placed.
        ews_model = self.env['nh.clinical.patient.observation.ews']
        frequencies_model = self.env['nh.clinical.frequencies.ews']
        placement_model = self.env['nh.clinical.patient.placement']

        spell_activity_id = refused_obs_activity.spell_activity_id.id
        refused_obs_frequency = refused_obs_activity.data_ref.frequency
        placement_frequency = frequencies_model.get_placement_frequency()

        if refused_obs_frequency == placement_frequency \
                and len(placement_model.get_placement_activities_for_spell(
                spell_activity_id)) > 1 \
                and ews_model.placement_before_refusals(spell_activity_id):
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
        """ Get the activity for the last observation made for the given
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
            observations.NhClinicalPatientObservation>`
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

    @classmethod
    def get_data_visualisation_resource(cls):
        """
        Returns URL of JS file to plot data visualisation so can be loaded on
        mobile and desktop

        :return: URL of JS file to plot graph
        :rtype: str
        """
        return None


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
    _description = "Blood Product"
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
    _description = "Pain Score"
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
    _description = "Urine Output"
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
