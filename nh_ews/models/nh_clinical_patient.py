from datetime import datetime, timedelta

from openerp import models, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NhClinicalPatient(models.Model):
    """
    Patient override to add EWS data to some methods.
    """
    _inherit = 'nh.clinical.patient'

    @api.one
    def serialise(self):
        """
        Override to add EWS data to patient dictionary.

        :return:
        :rtype: dict
        """
        patient_dict = super(NhClinicalPatient, self).serialise()[0]

        last_two_ews = self.get_latest_completed_ews(limit=2)
        last_ews = last_two_ews[0] if last_two_ews else None
        second_to_last_ews = last_two_ews[1] if len(last_two_ews) > 1 else None

        patient_dict['clinical_risk'] = last_ews and last_ews.clinical_risk
        patient_dict['frequency'] = last_ews.frequency if last_ews else 0,

        scheduled_ews_activity = self.get_next_scheduled_ews_activity()
        date_scheduled = scheduled_ews_activity.date_scheduled \
            if scheduled_ews_activity else None
        patient_dict['next_ews_time'] = self.get_next_ews_time(date_scheduled)

        patient_dict['ews_score'] = last_ews.score if last_ews else ''

        last_ews_score = last_ews and last_ews.score
        second_to_last_ews_score = second_to_last_ews and \
            second_to_last_ews.score
        patient_dict['ews_trend'] = self.get_ews_trend(
            last_ews_score, second_to_last_ews_score)

        return patient_dict

    def get_next_ews_time(self, date_scheduled):
        """
        Get the time until the next EWS observation is due or if it is already
        over due, the amount of time that has passed since it was due.

        :param date_scheduled: The value of the `date_scheduled` field found
        on the EWS activity record.
        :type date_scheduled: str
        :return: Next EWS due time.
        :rtype: str
        """
        if not date_scheduled:
            return ''
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

    def get_latest_completed_ews(self, limit=1, include_partials=False):
        """
        :param limit:
        :type limit: int
        :return: The latest full (not partial) completed EWS observation.
        :rtype: nh.clinical.patient.observation.ews record
        """
        ews_model = self.env['nh.clinical.patient.observation.ews']
        domain = [
            ('patient_id', '=', self.id),
            ('state', '=', 'completed')
        ]
        if not include_partials:
            # TODO this makes page load terrible.
            domain.append(('is_partial', '=', False))
        latest_ews = ews_model.search(
            domain, order='date_terminated desc, id desc', limit=limit)
        return latest_ews

    def get_next_scheduled_ews_activity(self):
        activity_model = self.env['nh.activity']
        next_scheduled_ews = activity_model.search([
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('patient_id', '=', self.id),
            ('state', '=', 'scheduled')
        ], order='date_scheduled asc', limit=1)
        return next_scheduled_ews

    @staticmethod
    def get_ews_trend(last_ews_score, second_to_last_ews_score):
        """
        Imagine EWS scores plotted on a graph. You could find a trend between
        any 2 points by seeing if the second point is equal, lower, or higher
        than the first point. This method does that but also takes into account
        edge cases like no EWS observations.

        :param last_ews_score:
        :type last_ews_score: int
        :param second_to_last_ews_score:
        :type second_to_last_ews_score: int
        :return:
        :rtype: str
        """
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
