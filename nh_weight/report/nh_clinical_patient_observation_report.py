# -*- coding: utf-8 -*-
import copy

from openerp import models


class NhClinicalPatientObservationReport(models.AbstractModel):

    _name = 'report.nh.clinical.observation_report'
    _inherit = 'report.nh.clinical.observation_report'

    def get_report_data(self, data, ews_only=False):
        report_data = super(NhClinicalPatientObservationReport, self)\
            .get_report_data(data, ews_only=ews_only)

        weight_dict = {
            'weight': 'nh.clinical.patient.observation.weight'
        }

        weight = self.get_activity_data_from_dict(
            weight_dict,
            self.spell_activity_id,
            data
        )
        report_data["patient"] = self.process_patient_weight(
            report_data["patient"], weight)

        if not ews_only:
            report_data["weights"] = weight['weight']
            json_weight_data = []
            for activity in weight['weight']:
                json_weight_data.append(copy.deepcopy(activity['values']))
            json_data = self.get_model_data_as_json(json_weight_data)
            report_data['weight_data'] = json_data

        if 'weights' in report_data:
            for obs_dict in report_data['weights']:
                self.env['nh.clinical.patient.observation']\
                    ._replace_falsey_values(obs_dict['values'],
                                            replace_zeros=True)

        return report_data

    def _localise_and_format_datetimes(self, report_data):
        super(NhClinicalPatientObservationReport, self)\
            ._localise_and_format_datetimes(report_data)
        for obs in report_data.get('weights', []):
            self._localise_dict_time(obs['values'], 'date_terminated')

    @staticmethod
    def process_patient_weight(patient, weight):
        weights = weight['weight']
        weight = False
        if len(weights) > 0:
            weight = weights[-1]['values']['weight']
        patient['weight'] = weight
        return patient
