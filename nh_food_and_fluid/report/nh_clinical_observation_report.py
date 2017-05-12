# -*- coding: utf-8 -*-

from openerp import models


class NhClinicalObservationReport(models.Model):

    _name = 'report.nh.clinical.observation_report'
    _inherit = 'report.nh.clinical.observation_report'

    def get_report_data(self, data, ews_only=False):
        report_data = super(NhClinicalObservationReport, self)\
            .get_report_data(data, ews_only=ews_only)
        food_and_fluid_data = self.get_food_and_fluid_report_data(data)
        report_data['food_and_fluid'] = food_and_fluid_data
        return report_data

    def get_food_and_fluid_report_data(self, data):
        food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        food_and_fluid_observation_activities = self.get_model_data(
            self.spell_activity_id, food_and_fluid_model._name,
            data.start_time, data.end_time
        )

        if food_and_fluid_observation_activities:
            periods = food_and_fluid_model.get_period_dictionaries(
                food_and_fluid_observation_activities, include_units=True)
            self._format_many_2_many_fields(periods)
            food_and_fluid_model.format_period_datetimes(periods)
        else:
            periods = []

        return {'periods': periods}

    def _add_empty_periods(self, period_dictionaries):
        pass

    def _format_many_2_many_fields(self, food_and_fluid_report_data):
        food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        obs_list = []
        for observation_period in food_and_fluid_report_data:
            for observation in observation_period['observations']:
                obs_list.append(observation['values'])
        food_and_fluid_model.format_many_2_many_fields(obs_list,
                                                       ['recorded_concerns',
                                                        'dietary_needs'])
