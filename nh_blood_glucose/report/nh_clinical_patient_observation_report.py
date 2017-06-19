# -*- coding: utf-8 -*-
from openerp import models


class NhClinicalPatientObservationReport(models.AbstractModel):

    _name = 'report.nh.clinical.observation_report'
    _inherit = 'report.nh.clinical.observation_report'

    def get_report_data(self, data, ews_only=False):
        report_data = super(NhClinicalPatientObservationReport, self)\
            .get_report_data(data, ews_only=ews_only)

        if not ews_only:
            blood_glucose_dict = {
                'blood_glucose':
                    'nh.clinical.patient.observation.blood_glucose'
            }

            blood_glucose_data = self.get_activity_data_from_dict(
                blood_glucose_dict,
                self.spell_activity_id,
                data
            )
            report_data["blood_glucoses"] = blood_glucose_data['blood_glucose']

            self._register_graph_data('blood_glucoses', 'blood_glucose_data')

            for obs_dict in report_data.get('blood_glucoses', []):
                self.env['nh.clinical.patient.observation']\
                    ._replace_falsey_values(
                        obs_dict['values'], replace_zeros=True)
        return report_data

    def _localise_and_format_datetimes(self, report_data):
        super(NhClinicalPatientObservationReport, self)\
            ._localise_and_format_datetimes(report_data)
        for obs in report_data.get('blood_glucoses', []):
            self._localise_dict_time(obs['values'], 'date_terminated')
