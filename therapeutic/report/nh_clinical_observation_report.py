from openerp import models


class NhClinicalPatientObservationReport(models.AbstractModel):

    _name = 'report.nh.clinical.observation_report'
    _inherit = 'report.nh.clinical.observation_report'

    def get_report_data(self, data, ews_only=False):
        report_data = super(NhClinicalPatientObservationReport, self)\
            .get_report_data(data, ews_only=ews_only)

        self._add_therapeutic_level_data(report_data, data.spell_id)
        self._add_therapeutic_obs_data(report_data, data.spell_id)

        return report_data

    def _add_therapeutic_level_data(self, report_data, spell_id):
        therapeutic_level_model = self.env['nh.clinical.therapeutic.level']

        levels = therapeutic_level_model.search([
            ('spell', '=', spell_id)
        ], order='create_date asc, id asc')
        levels_dict_list = levels.serialise()

        report_data['therapeutic_level_history'] = levels_dict_list

    def _add_therapeutic_obs_data(self, report_data, spell_id):
        spell_model = self.env['nh.clinical.spell']
        spell = spell_model.browse(spell_id)
        patient_id = spell.patient_id.id

        therapeutic_obs_model = \
            self.env['nh.clinical.patient.observation.therapeutic']
        obs = therapeutic_obs_model.search([
            ('patient_id', '=', patient_id)
        ], order='date_terminated asc, id asc')
        obs_dict_list = obs.serialise()

        report_data['therapeutic_observations'] = obs_dict_list

    def _localise_and_format_datetimes(self, report_data):
        super(NhClinicalPatientObservationReport, self)\
            ._localise_and_format_datetimes(report_data)
        for obs in report_data.get('therapeutic_level_history', []) + \
                report_data.get('therapeutic_observations', []):
            self._localise_dict_time(obs, 'date')
