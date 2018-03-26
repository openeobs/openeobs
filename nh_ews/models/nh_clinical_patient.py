from datetime import datetime

from openerp import models, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NhClinicalPatient(models.Model):

    _inherit = 'nh.clinical.patient'

    @api.one
    def serialise(self):
        patient_dict = super(NhClinicalPatient, self).serialise()
        latest_three_ews = self.get_latest_ews(limit=3)
        latest_ews = latest_three_ews[0] if latest_three_ews else None
        patient_dict['clinical_risk'] = \
            latest_ews.clinical_risk if latest_ews else None,
        patient_dict['frequency'] = latest_ews.frequency if latest_ews else 0,
        patient_dict['next_ews_time'] = self.get_next_ews_time(
            latest_ews.date_scheduled),
        patient_dict['ews_score'] = latest_ews.score if latest_ews else '',
        patient_dict['ews_trend'] = self.get_ews_trend(),
        patient_dict['refusal_in_effect'] = self.get_refusal_in_effect(),
        patient_dict['rapid_tranq'] = self.get_rapid_tranq_status()

    def get_next_ews_time(self, date_scheduled):
        if not date_scheduled:
            return '00:00 hours'
        date_scheduled = datetime.strptime(date_scheduled, DTF)
        datetime_utils_model = self.env['datetime_utils']
        now = datetime_utils_model.get_current_time()

        time_delta = date_scheduled - now
        ews_due_datetime_str = ''
        # If negative then date_scheduled is in the past and so EWS is overdue.
        if time_delta < 0:
            ews_due_datetime_str += 'overdue: '
        if time_delta.days:
            ews_due_datetime_str += '{} days'.format(time_delta.days)
        ews_due_datetime_str += '{}:{}'.format(time_delta.hours,
                                               time_delta.minutes)
        return ews_due_datetime_str

    def get_latest_ews(self, limit=1):
        ews_model = self.env['nh.clinical.patient.observation.ews']
        latest_ews = ews_model.search([
            ('patient_id', '=', self.id),
            ('state', '=', 'completed')
        ], order='date_terminated desc', limit=limit)
        return latest_ews

    def get_ews_trend(self):
        return 'same'

    def get_refusal_in_effect(self):
        return None

    def get_rapid_tranq_status(self):
        return False