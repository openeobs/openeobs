# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import datetime, timedelta

from openerp import models, fields, SUPERUSER_ID, api
from openerp.addons.nh_observations import fields as obs_fields
from openerp.addons.nh_odoo_fixes import validate
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as datetime


class NhClinicalPatientObservationWeight(models.Model):
    """
    Represents the action of measuring a
    :class:`patient<base.nh_clinical_patient>` weight.
    """
    _name = 'nh.clinical.patient.observation.weight'
    _inherit = 'nh.clinical.patient.observation_scored'

    _required = ['weight']
    _num_fields = ['weight']
    _description = "Weight"

    weight = obs_fields.Float(string='Weight (kg)', digits=(3, 1))
    waist_measurement = obs_fields.Float(string='Waist Measurement (cm)',
                                         digits=(3, 1))
    score = fields.Float(string='Body Mass Index (kg/m2)', digits=(3, 1),
                         compute='_get_score',)

    @api.constrains('weight', 'waist_measurement')
    def _in_min_max_range(self):
        form_description = self.get_form_description(None)

        if self.weight:
            weight_definition = [
                field for field in form_description if
                field.get('name') == 'weight'
            ][0]
            weight_min = weight_definition.get('min')
            weight_max = weight_definition.get('max')

            validate.in_min_max_range(weight_min, weight_max, self.weight)

        if self.waist_measurement:
            waist_measurement_definition = \
                [field for field in form_description
                 if field.get('name') == 'waist_measurement'][0]
            waist_min = waist_measurement_definition.get('min')
            waist_max = waist_measurement_definition.get('max')

            validate.in_min_max_range(waist_min, waist_max,
                                      self.waist_measurement)

    _POLICY = {
        'schedule': [[6, 0]]
    }
    _form_description = [
        {
            'name': 'weight',
            'label': 'Weight (kg)',
            'type': 'float',
            'necessary': 'true',
            'min': 0.0,
            'max': 500.0,
            'digits': [3, 1],
            'initially_hidden': False,
            'info': 'Choose days to weigh and preferably before breakfast'
        },
        {
            'name': 'waist_measurement',
            'label': 'Waist Measurement (cm)',
            'type': 'float',
            'necessary': 'false',
            'min': 30.0,
            'max': 500.0,
            'initially_hidden': False
        }
    ]

    @api.model
    def get_form_description(self, patient_id):
        """
        Override of `nh.clinical.patient.observation_scored` method.

        :param patient_id:
        :return:
        """
        form_description = deepcopy(self._form_description)
        return form_description

    @api.model
    def calculate_score(self, obs_data, return_dictionary=False):
        """
        Override of `nh.clinical.patient.observation_scored` method.

        :param obs_data:
        :param return_dictionary:
        :return:
        """
        is_dict = isinstance(obs_data, dict)
        if is_dict:
            patient_id = obs_data['patient_id'][0]
            weight = obs_data['weight']
        else:
            patient_id = obs_data.patient_id.id
            weight = obs_data.weight
        height_model = self.env['nh.clinical.patient.observation.height']
        height = height_model.get_latest_height(patient_id)

        if not height:
            return None
        bmi = self.calculate_bmi(weight, height)
        return {'score': bmi} if return_dictionary else bmi

    @staticmethod
    def calculate_bmi(weight, height):
        """
        Calculates the patient's BMI.

        :param weight: Patient weight in kilograms.
        :param height: Patient height in centimetres.
        :return: Patient BMI in kilograms per metre squared to one decimal
        place.
        :rtype: float
        """
        weight = float(weight)
        height = float(height)
        if height == 0:
            raise ValueError(
                "Height cannot be zero as it will cause a ZeroDivisionError."
            )
        bmi = weight / height / height
        return bmi

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
            hour = timedelta(hours=1)
            schedule_times = []
            for s in self._POLICY['schedule']:
                schedule_times.append(
                    datetime.now().replace(
                        hour=s[0], minute=s[1], second=0, microsecond=0))
            date_schedule = datetime.now().replace(
                minute=0, second=0, microsecond=0) + timedelta(hours=2)
            utctimes = [fields.Datetime.utc_timestamp(
                cr, uid, t, context=context) for t in schedule_times]
            while all([date_schedule.hour != date_schedule.strptime(
                    ut, datetime).hour for ut in utctimes]):
                date_schedule += hour
            date_scheduled = date_schedule.strftime(datetime)
        return super(NhClinicalPatientObservationWeight, self).schedule(
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

        res = super(NhClinicalPatientObservationWeight, self).complete(
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

    @classmethod
    def get_data_visualisation_resource(cls):
        """
        Returns URL of JS file to plot data visualisation so can be loaded on
        mobile and desktop

        :return: URL of JS file to plot graph
        :rtype: str
        """
        return '/nh_weight/static/src/js/chart.js'

    def get_submission_message(self):
        if self.is_partial:
            message = "BMI could not be calculated as weight was not provided."
        elif not self.score:
            message = \
                "BMI could not be calculated. Please take height measurement."
        else:
            message = "Based on the weight submitted, the patient's BMI is {}"\
                .format(self.score)
        return message

    @api.multi
    def get_formatted_obs(self, replace_zeros=True):
        return super(NhClinicalPatientObservationWeight, self)\
            .get_formatted_obs(replace_zeros=replace_zeros)
