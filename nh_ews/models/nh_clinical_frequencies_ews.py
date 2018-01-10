# -*- coding: utf-8 -*-
from openerp import api
from openerp.models import AbstractModel


class NhClinicalFrequenciesEws(AbstractModel):
    """
    This model retrieves different frequencies that may have been configured
    for the system such as `low_risk` (the frequency of an obs for a low risk
    patient) and `obs_restart` (the frequency of an obs created after a
    patient has just started having observations performed on them again since
    coming off of 'obs stop' status).

    Currently the methods all retrieve configuration from the database by
    calling `ir.config_parameter.get_param()`. This is an Odoo model that acts
    as an interface to a simple key-value store accessible only by the
    superuser.

    All the methods call `get_param` on this model which in turn calls the
    `ir.config_parameter` version.
    """
    _name = 'nh.clinical.frequencies.ews'

    def get_minimum_frequency(self, clinical_risk):
        """
        Get the parameter which specifies the minimum frequency that can
        safely be set for a particular risk. The parameter must follow a
        particular naming convention that the method assumes.

        :param clinical_risk:
        :type clinical_risk: str
        :return: Minimum frequency config parameter value.
        :rtype: int
        """
        return self._get_param('{}_risk_minimum', clinical_risk)

    def get_maximum_frequency(self, clinical_risk):
        """
        Get the value for the config parameter which specifies the minimum
        frequency that can safely by set for a particular risk. The parameter
        must follow a particular naming convention that the method assumes.
        :param clinical_risk:
        :type clinical_risk: str
        :return: Maximum frequency config parameter value.
        :rtype: int
        """
        return self._get_param('{}_risk_maximum', clinical_risk)

    @api.model
    def get_risk_frequency(self, clinical_risk):
        """
        Get the value for the config parameter which specifies the frequency
        that should be used for observations on patients that have a
        particular clinical risk.
        :param clinical_risk:
        :return: Risk frequency config parameter value.
        :rtype: int
        """
        if isinstance(clinical_risk, int):
            ews_model = self.env['nh.clinical.patient.observation.ews']
            case = clinical_risk
            clinical_risk = ews_model.convert_case_to_risk(case).lower()
            if clinical_risk == 'none':
                clinical_risk = 'no'
        return self._get_param('{}_risk', clinical_risk)

    def get_placement_frequency(self):
        """
        Get the config parameter to be used for the EWS observation created
        when a patient is placed.

        :return: Placement frequency config parameter.
        :rtype: int
        """
        return self._get_param('placement')

    def _get_param(self, string, *args):
        """
        Format the passed arguments into the passed string to get the
        parameter name to be retrieved. The underlying method does not raise
        if the parameter does not exist but this method does.

        :param string:
        :param args:
        :return: Requested frequency for a particular situation.
        :rtype: int
        :raises: ValueError
        """
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
