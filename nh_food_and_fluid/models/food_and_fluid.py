# -*- coding: utf-8 -*-
import copy
from datetime import datetime, timedelta

from openerp import models, api
from openerp.addons.nh_observations import fields as obs_fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NHClinicalFoodAndFluid(models.Model):

    _name = 'nh.clinical.patient.observation.food_fluid'
    _inherit = 'nh.clinical.patient.observation'

    _required = ['passed_urine', 'bowels_open']
    _description = 'Food and Fluid'

    _passed_urine_options = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('unknown', 'Unknown')
    ]

    _bowels_open_options = [
        ('no', 'No'),
        ('unknown', 'Unknown'),
        ('type_1', 'Type 1'),
        ('type_2', 'Type 2'),
        ('type_3', 'Type 3'),
        ('type_4', 'Type 4'),
        ('type_5', 'Type 5'),
        ('type_6', 'Type 6'),
        ('type_7', 'Type 7')
    ]

    recorded_concerns = obs_fields.Many2Many(
        comodel_name='nh.clinical.recorded_concern',
        relation="recorded_concern_rel",
        string='Recorded Concern', necessary=False
    )
    dietary_needs = obs_fields.Many2Many(
        comodel_name='nh.clinical.dietary_need',
        relation="dietary_need_rel",
        string='Consider Special Dietary Needs', necessary=False
    )
    fluid_taken = obs_fields.Integer('Fluid Taken (ml) - Include IV / NG',
                                     necessary=False)
    fluid_description = obs_fields.Text('Fluid Description')
    food_taken = obs_fields.Text('Food Taken')
    food_fluid_rejected = obs_fields.Text(
        'Food and Fluid Offered but Rejected', necessary=False
    )
    passed_urine = obs_fields.Selection(_passed_urine_options, 'Passed Urine',
                                        required=True)
    bowels_open = obs_fields.Selection(_bowels_open_options, 'Bowels Open',
                                       required=True)

    @classmethod
    def get_description(cls, append_observation=True):
        description = super(NHClinicalFoodAndFluid, cls).get_description(
            append_observation=append_observation
        )
        if not append_observation:
            description = "Daily {}".format(description)
        return description

    @classmethod
    def get_data_visualisation_resource(cls):
        """
        Returns URL of JS file to plot data visualisation so can be loaded on
        mobile and desktop

        :return: URL of JS file to plot graph
        :rtype: str
        """
        return '/nh_food_and_fluid/static/src/js/chart.js'

    @api.model
    def get_form_description(self, patient_id):
        """
        Returns a description in dictionary format of the input fields
        that would be required in the user gui to submit this
        observation.

        Adds the lists of recorded concerns and dietary needs to the
        form description as these are stored in separate models to allow
        for multi select

        :param patient_id: :class:`patient<base.nh_clinical_patient>` id
        :type patient_id: int
        :returns: a list of dictionaries
        :rtype: list
        """
        form_desc = copy.deepcopy(self._form_description)
        recorded_concern_model = self.env['nh.clinical.recorded_concern']
        dietary_need_model = self.env['nh.clinical.dietary_need']
        recorded_concerns = recorded_concern_model.search([])
        dietary_needs = dietary_need_model.search([])
        form_desc[0]['selection'] = \
            [(rec.id, rec.name) for rec in recorded_concerns]
        form_desc[1]['selection'] = \
            [(rec.id, rec.name) for rec in dietary_needs]
        return form_desc

    _form_description = [
        {
            'name': 'recorded_concerns',
            'type': 'multiselect',
            'label': 'Recorded Concern',
            'selection': [],
            'initially_hidden': False,
            'necessary': 'false'
        },
        {
            'name': 'dietary_needs',
            'type': 'multiselect',
            'label': 'Consider Special Dietary Needs',
            'selection': [],
            'initially_hidden': False,
            'necessary': 'false'
        },
        {
            'name': 'fluid_taken',
            'type': 'integer',
            'min': 0,
            'max': 5000,
            'label': 'Fluid Taken (ml) - Include IV / NG',
            'initially_hidden': False,
            'reference': {
                'type': 'iframe',
                'url': '/nh_food_and_fluid/static/src/html/fluid_taken.html',
                'title': 'Fluid Taken Guidance',
                'label': 'Fluid Taken Guidance'
            },
            'necessary': 'false'
        },
        {
            'name': 'fluid_description',
            'type': 'text',
            'label': 'Fluid Description',
            'initially_hidden': False,
            'necessary': 'false'
        },
        {
            'name': 'food_taken',
            'type': 'text',
            'label': 'Food Taken',
            'initially_hidden': False,
            'necessary': 'false'
        },
        {
            'name': 'food_fluid_rejected',
            'type': 'text',
            'label': 'Food and Fluid Offered but Rejected',
            'initially_hidden': False,
            'necessary': 'false'
        },
        {
            'name': 'passed_urine',
            'type': 'selection',
            'label': 'Passed Urine',
            'selection': _passed_urine_options,
            'initially_hidden': False,
            'required': True,
            'necessary': 'true'
        },
        {
            'name': 'bowels_open',
            'type': 'selection',
            'label': 'Bowels Open',
            'selection': _bowels_open_options,
            'initially_hidden': False,
            'reference': {
                'type': 'image',
                'url': '/nh_stools/static/src/img/bristol_stools.png',
                'title': 'Bristol Stools Type Chart',
                'label': 'Bristol Stools Type Chart'
            },
            'required': True,
            'necessary': 'true'
        }
    ]

    def calculate_total_fluid_intake(self, spell_activity_id, date_time):
        """
        Returns the sum of all the `fluid_taken` values from all the food and
        fluid observations completed in a particular period.

        The period to calculate for is determined by the `date_time` argument.
        The `date_time` argument can be any time. Whichever period the
        `date_time` is a part of will be the period used for the calculation.

        :param spell_activity_id:
        :type spell_activity_id: int
        :param date_time:
        :type: str or datetime
        :return: Total fluid intake.
        :rtype: int
        """
        activity_model = self.env['nh.activity']
        period_domain = self.get_period_domain(date_time)
        domain = [
            ('data_model', '=', self._name),
            ('spell_activity_id', '=', spell_activity_id)
        ]
        domain.extend(period_domain)

        f_and_f_obs_activities = activity_model.search(domain)
        fluid_intake_values = [activity.data_ref.fluid_taken for activity
                               in f_and_f_obs_activities]

        fluid_intake_total = sum(fluid_intake_values)
        return fluid_intake_total

    def get_period_domain(self, date_time):
        """
        The period to produce domain parameters for is determined by the
        `date_time` argument. The `date_time` argument can be any time.
        Whichever period the `date_time` is a part of will be the period used
        for the calculation.

        :param date_time:
        :type date_time: datetime or str
        :return: Domain parameters that will limit results to a 24 hour period.
        :rtype: list
        """
        date_time = self.env['datetime_utils'].validate_and_convert(date_time)

        period_start_datetime_str = self.get_period_start_datetime(date_time)
        period_end_datetime_str = self.get_period_end_datetime(date_time)
        domain = [
            ('date_terminated', '>=', period_start_datetime_str),
            ('date_terminated', '<', period_end_datetime_str)
        ]
        return domain

    def get_period_start_datetime(self, date_time):
        """
        Get the datetime representing the beginning of the period that the
        passed datetime occurs in.

        :param date_time:
        :type date_time: datetime or str
        :return:
        :rtype: str
        """
        date_time = self.env['datetime_utils'].validate_and_convert(date_time)
        period_start_hour = 7

        period_start_datetime = datetime(
            date_time.year, date_time.month, day=date_time.day,
            hour=period_start_hour
        )
        if self.before_seven_am(date_time):
            period_start_datetime = period_start_datetime - timedelta(days=1)

        period_start_datetime_str = period_start_datetime.strftime(DTF)
        return period_start_datetime_str

    def get_period_end_datetime(self, date_time):
        """
        Get the datetime representing the first microsecond of the period
        after the one that the passed date_time is a part of.

        :param date_time:
        :type date_time: datetime or str
        :return:
        :rtype: str
        """
        date_time = self.env['datetime_utils'].validate_and_convert(date_time)
        period_start_hour = 7

        period_end_datetime = datetime(
            date_time.year, date_time.month, day=date_time.day,
            hour=period_start_hour
        )
        if not self.before_seven_am(date_time):
            period_end_datetime = period_end_datetime + timedelta(days=1)

        period_end_datetime_str = period_end_datetime.strftime(DTF)
        return period_end_datetime_str

    @classmethod
    def before_seven_am(cls, date_time):
        """
        True if the passed date_time is before 07:00 in the morning.

        :param date_time:
        :type date_time: datetime
        :return:
        :rtype: bool
        """
        return date_time.hour < 7

    def get_submission_message(self):
        """
        Override of `nh.clinical.patient.observation` method.

        :return:
        """
        activity_model = self.env['nh.activity']

        data_ref = self.convert_record_to_data_ref()
        domain = [
            ('data_ref', '=', data_ref)
        ]
        obs_activity = activity_model.search(domain)
        obs_activity.ensure_one()
        if obs_activity.state != 'completed':
            raise ValueError(
                "Cannot get the submission message for an observation that is "
                "not completed."
            )

        observation_completion_datetime = obs_activity.date_terminated
        fluid_intake_total = self.calculate_total_fluid_intake(
            obs_activity.spell_activity_id.id, observation_completion_datetime
        )

        period_start_datetime = \
            self.get_period_start_datetime(observation_completion_datetime)
        datetime_utils = self.env['datetime_utils']
        period_start_datetime = \
            datetime_utils.reformat_server_datetime_for_frontend(
                period_start_datetime, two_character_year=True
            )

        message = 'The patient has had {fluid_intake_total}ml of fluid in ' \
                  'the current 24 hour period (starting on ' \
                  '{period_start_datetime}).'
        message = message.format(fluid_intake_total=fluid_intake_total,
                                 period_start_datetime=period_start_datetime)
        return message

    def get_all_completed_food_and_fluid_observation_activities(
            self, spell_activity_id):
        activity_model = self.env['nh.activity']
        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.food_fluid'),
            ('state', '=', 'completed'),
            ('spell_activity_id', '=', spell_activity_id)
        ]
        obs_activities = activity_model.search(domain,
                                               order='date_terminated asc')
        return obs_activities

    @staticmethod
    def calculate_period_score(total_fluid_intake):
        if total_fluid_intake <= 600:
            score = 3
        elif 600 < total_fluid_intake < 1200:
            score = 2
        elif 1200 <= total_fluid_intake < 1500:
            score = 1
        elif total_fluid_intake >= 1500:
            score = 0
        return score

    @api.multi
    def get_formatted_obs(self):
        """
        Override of `nh.clinical.patient.observation`.

        :return:
        :rtype: dict
        """
        if len(self) < 1:
            raise ValueError("Passed recordset is empty, "
                             "cannot get formatted obs.")
        patient_id = self[0].patient_id.id
        obs = self.read_obs_for_patient(patient_id)
        self.convert_field_values_to_labels(obs)
        periods = self.get_period_dictionaries(obs)
        self.format_period_datetimes(periods)
        return periods

    def get_period_dictionaries(self, food_and_fluid_observations,
                                include_units=False):
        """
        Get a list of dictionaries, each one representing a 24 hour
        observation period. Each dictionary contains data about the period as
        well as a nested list of data for the observations.

        :param food_and_fluid_observations:
        :param include_units: Include measurements with units where applicable.
        :type include_units: bool
        :return:
        """
        if not food_and_fluid_observations:
            raise ValueError(
                "Passed observations argument is falsey, expected a list "
                "of dictionaries. Cannot create period dictionaries without "
                "observations."
            )

        food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        an_obs = food_and_fluid_observations[0]
        if an_obs.get('spell_activity_id'):
            spell_activity_id = \
                self._get_id_from_tuple(an_obs['spell_activity_id'])
        else:
            spell_model = self.env['nh.clinical.spell']
            spell_activity = \
                spell_model.get_spell_activity_by_patient(
                    an_obs['patient_id'][0]
                )
            spell_activity_id = spell_activity.id

        period_dictionaries = []
        period_start_datetime_current = None
        period_obs = None
        # Iterate through all the observations and gradually build a list of
        # periods containing their observations.
        for obs in food_and_fluid_observations:
            date_terminated = obs['date_terminated']
            period_start_datetime = \
                food_and_fluid_model.get_period_start_datetime(date_terminated)
            # If this observation is the first in a new period,
            # add the new period to the list.
            if period_start_datetime != period_start_datetime_current:
                period_start_datetime_current = period_start_datetime
                period_dictionary = \
                    self._create_new_period_dictionary(
                        obs, spell_activity_id, include_units=include_units
                    )
                period_dictionaries.append(period_dictionary)
                period_obs = \
                    period_dictionaries[-1]['observations']
            # If this observation is in a period we've already come across
            # then add it.
            period_obs.append(obs)

        return period_dictionaries

    def _create_new_period_dictionary(self, obs, spell_activity_id,
                                      include_units=False):
        """
        Encapsulates logic for initialising a period dictionary,
        further population is required for the dictionary to be complete.

        :param obs:
        :param spell_activity_id:
        :param include_units: Include measurements with units where applicable.
        :type include_units: bool
        :return:
        :rtype: dict
        """
        food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        period = {}

        date_terminated = obs['date_terminated']
        period['period_start_datetime'] = \
            food_and_fluid_model.get_period_start_datetime(date_terminated)
        period['period_end_datetime'] = \
            food_and_fluid_model.get_period_end_datetime(date_terminated)
        total_fluid_intake = \
            food_and_fluid_model.calculate_total_fluid_intake(
                spell_activity_id, date_terminated
            )
        score = \
            food_and_fluid_model.calculate_period_score(total_fluid_intake)

        if include_units:
            total_fluid_intake = "{}ml".format(total_fluid_intake)

        period['total_fluid_intake'] = total_fluid_intake
        period['score'] = score
        period['observations'] = []

        period_end_datetime = datetime.strptime(
            period['period_end_datetime'], DTF
        )
        # If current period.
        if datetime.now() < period_end_datetime:
            period['current_period'] = True
        return period

    def format_period_datetimes(self, periods):
        """
        Format the datetimes in the passed period dictionaries to be more
        user-friendly.

        :param periods:
        :return:
        """
        datetime_utils = self.env['datetime_utils']
        datetime_format = \
            datetime_utils.datetime_format_front_end_two_character_year
        for period in periods:
            period_start_datetime = datetime.strptime(
                period['period_start_datetime'], DTF
            )
            period['period_start_datetime'] = \
                period_start_datetime.strftime(datetime_format)
            period_end_datetime = datetime.strptime(
                period['period_end_datetime'], DTF
            )
            period['period_end_datetime'] = \
                period_end_datetime.strftime(datetime_format)
