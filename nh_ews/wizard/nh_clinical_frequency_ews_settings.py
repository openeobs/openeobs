# -*- coding: utf -*-
from openerp import fields, api
from openerp.addons.nh_odoo_fixes import validate
from openerp.models import TransientModel, MAGIC_COLUMNS


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
    low_risk_minimum = fields.Integer()
    medium_risk_minimum = fields.Integer()
    high_risk_minimum = fields.Integer()

    no_risk_maximum = fields.Integer()
    low_risk_maximum = fields.Integer()
    medium_risk_maximum = fields.Integer()
    high_risk_maximum = fields.Integer()

    no_risk = fields.Integer(
        min='no_risk_minimum', max='no_risk_maximum')
    low_risk = fields.Integer(
        min='low_risk_minimum', max='low_risk_maximum')
    medium_risk = fields.Integer(
        min='medium_risk_minimum', max='medium_risk_maximum')
    high_risk = fields.Integer(
        min='high_risk_minimum', max='high_risk_maximum')

    placement = fields.Integer()

    obs_restart = fields.Integer()

    @api.constrains('no_risk', 'low_risk', 'medium_risk', 'high_risk')
    def _in_min_max_range(self):
        """
        Validate that the values of the constrained fields are within the
        range specified by the values of their correspondingly named
        'minimum' and 'maximum' fields.
        """
        validate.fields_in_min_max_range(
            self, ['no_risk', 'low_risk', 'medium_risk', 'high_risk'])

    @api.multi
    def set_params(self):
        """
        Sets the values of config parameters so they are stored in the
        database.
        """
        field_names = self._get_field_names()

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

    def _get_field_names(self):
        """
        Gets all the field names for the record excluding 'magic' fields like
        `create_date` that Odoo puts on every record.
        :return: List of 'normal' field names.
        :rtype: list
        """
        field_names = [field_name for field_name in self._columns.keys()
                       if field_name not in MAGIC_COLUMNS]
        return field_names
