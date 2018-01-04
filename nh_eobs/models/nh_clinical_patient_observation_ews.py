# -*- coding: utf-8 -*-
from datetime import datetime as dt
from datetime import timedelta

from openerp.models import Model
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class NhClinicalPatientObservationEws(Model):
    """
    Override to add refusal functionality.
    """
    _inherit = 'nh.clinical.patient.observation.ews'

    def update_next_obs_after_partial(self, partial_obs_activity,
                                      next_obs_activity):
        """
        If the partial is a refusal it is handled very differently to a normal
        partial.

        :param partial_obs_activity:
        :param next_obs_activity:
        :return:
        """
        patient_id = partial_obs_activity.data_ref.patient_id.id

        last_obs_refused = self.is_last_obs_refused(patient_id)
        if last_obs_refused:
            frequencies_model = self.env['nh.clinical.frequencies.ews']
            frequency = \
                frequencies_model.get_refusal_frequency(partial_obs_activity)
            date_scheduled = self.get_date_scheduled_for_refusal(
                partial_obs_activity.date_terminated, frequency)
            self._schedule(next_obs_activity, frequency, date_scheduled)
        else:
            super(NhClinicalPatientObservationEws, self)\
                .update_next_obs_after_partial(partial_obs_activity,
                                               next_obs_activity)

    @staticmethod
    def get_date_scheduled_for_refusal(
            previous_activity_completed_datetime, frequency):
        """
        Get the expected schedule date for a new observation triggered based on
        the passed completion date of the previous observation and it's
        frequency.

        :param previous_activity_completed_datetime: Value for the date
            terminated field of the previous completed observation.
        :type previous_activity_completed_datetime: str
        :param frequency: Frequency in minutes.
        :type frequency: int
        :return:
        """
        previous_activity_completed_datetime = \
            dt.strptime(previous_activity_completed_datetime, DTF)
        date_scheduled = \
            previous_activity_completed_datetime + timedelta(minutes=frequency)
        return date_scheduled
