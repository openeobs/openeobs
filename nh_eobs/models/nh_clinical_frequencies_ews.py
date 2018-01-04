# -*- coding: utf-8 -*-
from openerp.models import AbstractModel


class NhClinicalFrequenciesEws(AbstractModel):
    """
    Override adds logic for getting frequency following a refusal.
    """
    _inherit = 'nh.clinical.frequencies.ews'

    def get_refusal_frequency(self, refused_obs_activity):
        """
        Frequency to be used for scheduling a new EWS observation when a
        patient has just refused their previous EWS observation.

        The frequency varies depending on the current status of the patient.
        The main reason a method like this is necessary for getting the
        frequency specifically for refusals is because refusals are a type of
        partial observation but they behave entirely differently to a normal
        partial
        (see `nh_ews.ews.nh_clinical_patient_observation_ews.complete()`).

        :return: Refusal frequency config parameter.
        :rtype: int
        """
        ews_model = self.env['nh.clinical.patient.observation.ews']
        spell_activity_id = refused_obs_activity.spell_activity_id.id

        if ews_model.obs_stop_before_refusals(spell_activity_id):
            next_obs_frequency = self.get_obs_restart_frequency()
        elif ews_model.transferred_and_placed_before_refusals(refused_obs_activity):
            next_obs_frequency = self.get_transfer_frequency()
        else:
            last_full_obs_activity = ews_model.get_last_full_obs_activity(
                spell_activity_id)
            if last_full_obs_activity:
                case = ews_model.get_case(last_full_obs_activity.data_ref)
                next_obs_frequency = self.get_risk_frequency(case)
            else:
                next_obs_frequency = self.get_placement_frequency()

        next_obs_frequency = \
            self._cap_frequency_at_24_hours(next_obs_frequency)
        return next_obs_frequency

    @staticmethod
    def _cap_frequency_at_24_hours(frequency):
        return 1440 if frequency > 1440 else frequency
