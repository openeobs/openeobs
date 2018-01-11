# -*- coding: utf -*-
from openerp import fields, api
from openerp.models import TransientModel


class NhClinicalFrequenciesEws(TransientModel):
    """
    Allows various frequencies used throughout the system to be configured.
    Overrides `res.config.settings` which is an Odoo model that provides some
    useful out of the box functionality for configuration. See link below for
    more information:

    http://odoo-development.readthedocs.io/en/latest/dev/py/res.config.settings
    .html
    """
    _name = 'nh.clinical.frequencies.ews_settings'
    _inherit = 'res.config.settings'

    no_risk_minimum = fields.Integer()
    no_risk_maximum = fields.Integer()
    no_risk = fields.Integer()

    low_risk_minimum = fields.Integer()
    low_risk_maximum = fields.Integer()
    low_risk = fields.Integer()

    medium_risk_minimum = fields.Integer()
    medium_risk_maximum = fields.Integer()
    medium_risk = fields.Integer()

    high_risk_maximum = fields.Integer()
    high_risk_minimum = fields.Integer()
    high_risk = fields.Integer()

    placement_minimum = fields.Integer()
    placement_maximum = fields.Integer()
    placement = fields.Integer()

    obs_restart_minimum = fields.Integer()
    obs_restart_maximum = fields.Integer()
    obs_restart = fields.Integer()

    transfer_refusal_minimum = fields.Integer()
    transfer_refusal_maximum = fields.Integer()
    transfer_refusal = fields.Integer()

    unknown_risk_refusal_minimum = fields.Integer()
    unknown_risk_refusal_maximum = fields.Integer()
    unknown_risk_refusal = fields.Integer()

    # Even though the 'minimum' and 'maximum' fields do not themselves need
    # to be validated they must still be added to the constrains so that the
    # record passed to the validation method is populated with their new
    # values.
    # For example if a user sets all the values at once along with minimums
    # and maximums that make the new values valid, the method would still
    # raise because it would be use the existing values in the database for
    # minimum and maximum. Adding the minimum and maximum fields to the
    # constrains fixed this.
    @api.constrains(
        'no_risk_minimum', 'no_risk_maximum', 'no_risk',
        'low_risk_minimum', 'low_risk_maximum', 'low_risk',
        'medium_risk_minimum', 'medium_risk_maximum', 'medium_risk',
        'high_risk_minimum', 'high_risk_maximum', 'high_risk',
        'placement_minimum', 'placement_maximum', 'placement',
        'obs_restart_minimum', 'obs_restart_maximum', 'obs_restart',
        'transfer_refusal_minimum', 'transfer_refusal_maximum',
        'transfer_refusal',
        'unknown_risk_refusal_minimum', 'unknown_risk_refusal_maximum',
        'unknown_risk_refusal'
    )
    def _in_min_max_range(self):
        """
        Validate that the values of the constrained fields are within the
        range specified by the values of their correspondingly named
        'minimum' and 'maximum' fields.
        """
        validation_utils = self.env['nh.clinical.validation_utils']
        validation_utils.fields_in_min_max_range(self)

    @api.multi
    def set_params(self):
        """
        Sets the values of config parameters so they are stored in the
        database.
        """
        field_utils = self.env['nh.clinical.field_utils']
        field_names = field_utils.get_field_names(self)

        config_parameters_model = self.env['ir.config_parameter']
        for field_name in field_names:
            field_value = getattr(self, field_name)
            config_parameters_model.set_param(field_name, field_value)

    @api.model
    def get_default_params(self, field_names):
        """
        The `get_default_params` method retrieves the values of existing
        configuration parameters that have already been set previously so the
        record is pre-populated.

        When the user is looking at a view this has the effect of the
        configuration screen showing what the existing values are so they are
        informed when and if they set new ones.

        :param field_names: The names of all the fields on the record, each
        of which represents one of the configuration parameters.
        :type field_names: list
        :return: Current parameter names and values.
        :rtype: dict
        """
        current_param_values = {}
        config_parameters_model = self.env['ir.config_parameter']
        for field_name in field_names:
            current_param_values[field_name] = \
                config_parameters_model.get_param(field_name, '')
        return current_param_values
