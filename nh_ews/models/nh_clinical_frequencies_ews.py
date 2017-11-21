# -*- coding: utf-8 -*-
from openerp.models import AbstractModel


class NhClinicalFrequenciesEws(AbstractModel):

    _name = 'nh.clinical.frequencies.ews'

    def get_minimum_frequency(self, clinical_risk):
        return self._get_param('{}_risk_minimum', clinical_risk)

    def get_maximum_frequency(self, clinical_risk):
        return self._get_param('{}_risk_maximum', clinical_risk)

    def get_risk_frequency(self, clinical_risk):
        return self._get_param('{}_risk', clinical_risk)

    def get_placement_frequency(self):
        return self._get_param('placement')

    def get_obs_restart_frequency(self):
        return self._get_param('obs_restart')

    def _get_param(self, string, *args):
        config_model = self.env['ir.config_parameter']
        if len(args):
            parameter_name = string.format(*args)
        else:
            parameter_name = string
        frequency = config_model.get_param(parameter_name, default=None)
        if frequency is None:
            raise ValueError("No parameter with name '{}' exists. "
                             "Ensure it has been set via the UI "
                             "or data XML.".format(parameter_name))
        frequency = int(frequency)
        return frequency
