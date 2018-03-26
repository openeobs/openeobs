from datetime import datetime, timedelta

from openerp import models, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NhClinicalPatient(models.Model):

    _inherit = 'nh.clinical.patient'

    @api.one
    def serialise(self):
        patient_dict = super(NhClinicalPatient, self).serialise()

        latest_two_ews = self.get_latest_completed_ews(limit=2)
        latest_ews = latest_two_ews[0] if latest_two_ews else None

        patient_dict['clinical_risk'] = \
            latest_ews.clinical_risk if latest_ews else None,
        patient_dict['frequency'] = latest_ews.frequency if latest_ews else 0,
        patient_dict['next_ews_time'] = self.get_next_ews_time(
            latest_ews.date_scheduled),
        patient_dict['ews_score'] = latest_ews.score if latest_ews else '',
        patient_dict['ews_trend'] = self.get_ews_trend(
            latest_two_ews[0].score, latest_two_ews[1].score),
        patient_dict['refusal_in_effect'] = self.get_refusal_in_effect(),
        patient_dict['rapid_tranq'] = self.get_rapid_tranq_status()

    def get_next_ews_time(self, date_scheduled):
        if not date_scheduled:
            return '00:00 hours'
        date_scheduled = datetime.strptime(date_scheduled, DTF)
        datetime_utils_model = self.env['datetime_utils']
        now = datetime_utils_model.get_current_time()

        time_delta = date_scheduled - now
        zero_time_delta = timedelta()  # All parameters default to 0.

        overdue = ''
        # If negative then date_scheduled is in the past and so EWS is overdue.
        if time_delta < zero_time_delta:
            overdue = 'overdue: '
            # Convert to positive timedelta before further logic because
            # representation of negative timedeltas is really weird.
            time_delta = abs(time_delta)
        days = '{} day(s) '.format(time_delta.days) if time_delta.days else ''
        # Dividing by int will drop fractional remainder leaving only full
        # hours.
        hours_int = time_delta.seconds / 3600
        hours = '{0:02d}'.format(hours_int)
        # Subtracting the calculated full hours leaves only full minutes.
        minutes_int = (time_delta.seconds - hours_int * 3600) / 60
        minutes = '{0:02d}'.format(minutes_int)
        ews_due_datetime_str = \
            '{overdue}{days}{hours}:{minutes} hours'.format(
                overdue=overdue, days=days, hours=hours, minutes=minutes)
        return ews_due_datetime_str

    def get_latest_completed_ews(self, limit=1):
        ews_model = self.env['nh.clinical.patient.observation.ews']
        latest_ews = ews_model.search([
            ('patient_id', '=', self.id),
            ('state', '=', 'completed')
        ], order='date_terminated desc', limit=limit)
        return latest_ews

    @staticmethod
    def get_ews_trend(last_ews_score, second_to_last_ews_score):
        if last_ews_score is None and second_to_last_ews_score is None:
            return 'none'
        elif last_ews_score is None:
            return 'no latest'
        elif second_to_last_ews_score is None:
            return 'first'
        elif last_ews_score < second_to_last_ews_score:
            return 'down'
        elif last_ews_score == second_to_last_ews_score:
            return 'same'
        elif last_ews_score > second_to_last_ews_score:
            return 'up'

    def get_refusal_in_effect(self):
        return None

    def get_rapid_tranq_status(self):
        return False
