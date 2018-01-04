# -*- coding: utf-8 -*-
from openerp.models import AbstractModel


class NhClinicalFrequenciesEws(AbstractModel):

    _inherit = 'nh.clinical.frequencies.ews'

    def get_obs_restart_frequency(self):
        """
        Get the config parameter to be used for the EWS observation created
        when a patient's obs stop status ends.

        :return: Obs restart frequency config parameter.
        :rtype: int
        """
        return self._get_param('obs_restart')
