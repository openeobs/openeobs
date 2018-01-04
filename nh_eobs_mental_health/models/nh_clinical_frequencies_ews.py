# -*- coding: utf-8 -*-
from openerp.models import AbstractModel


class NhClinicalFrequenciesEws(AbstractModel):
    """
    Override to add support for obs stop.
    """
    _inherit = 'nh.clinical.frequencies.ews'

    def get_obs_restart_frequency(self):
        """
        Get the config parameter to be used for the EWS observation created
        when a patient's obs stop status ends.

        :return: Obs restart frequency config parameter.
        :rtype: int
        """
        return self._get_param('obs_restart')

    def get_refusal_frequency(self, refused_obs_activity):
        """
        Override to add support for obs stop.

        :param refused_obs_activity:
        :return:
        """
        ews_model = self.env['nh.clinical.patient.observation.ews']
        spell_activity_id = refused_obs_activity.spell_activity_id.id

        if ews_model.obs_stop_before_refusals(spell_activity_id):
            next_obs_frequency = self.get_obs_restart_frequency()
            next_obs_frequency = \
                self._cap_frequency_at_24_hours(next_obs_frequency)
            return next_obs_frequency

        return super(NhClinicalFrequenciesEws, self).get_refusal_frequency(
            refused_obs_activity)
