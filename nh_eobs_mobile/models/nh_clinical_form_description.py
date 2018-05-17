# -*- coding: utf-8 -*-
from openerp import models


class FormDescription(models.TransientModel):
    """
    The form description is used to produce a dictionary that can be used in
    combination with a QWeb template to produce HTML for the LiveObs mobile
    pages.
    """
    _name = 'nh.clinical.form_description'

    @classmethod
    def to_dict(cls, model):
        """
        Attempt to automatically generate the form description from the model.

        This method does not yet support all field types.

        :param model: Model object.
        :return:
        :rtype: dict
        """
        form_description = []
        field_utils = cls.pool['nh.clinical.field_utils']
        obs_fields = field_utils.get_obs_fields_from_model(model)

        for field in obs_fields:
            field_description = {
                'name': field.name,
                'type': cls._get_type(field),
                'label': field.string,
                'initially_hidden': False,
                'required': str(field.required).lower(),
                'necessary': str(field.necessary).lower()
            }
            cls._add_size_if_necessary(field, field_description)
            cls._add_selection_keys_if_necessary(field, field_description)
            form_description.append(field_description)

        cls._order_fields(model, form_description)

        return form_description

    @staticmethod
    def _order_fields(model, form_description):
        """
        Order the field description within the form description so that they
        display in the intended order in the UI.

        :param model: Model object.
        :param form_description:
        :type form_description: dict
        :return:
        """
        desired_order = model.get_obs_field_order()
        form_description.sort(key=lambda e: desired_order.index(e.get('name')))

    @staticmethod
    def _get_type(field):
        """
        Map the Odoo field type to our form description type.

        :param field: Field object.
        :return:
        :rtype: str
        """
        if field.type == 'char':
            return 'text'
        elif field.type == 'boolean':
            return 'selection'
        return field.type

    @staticmethod
    def _add_size_if_necessary(field, field_description):
        """
        Add the size key to the field description if there is a size to be
        mapped.

        :param field: Field object.
        :param field_description:
        :type field_description: dict
        """
        if hasattr(field, 'size') and field.size:
            field_description['size'] = field.size

    @staticmethod
    def _add_selection_keys_if_necessary(field, field_description):
        """
        Add the selection keys to the field description if appropriate.

        :param field: Field object.
        :param field_description:
        :type field_description: dict
        """
        if field.type == 'selection':
            field_description['selection'] = field.selection
            field_description['selection_type'] = 'text'
        elif field.type == 'boolean':
            field_description['selection'] = [[True, 'Yes'], [False, 'No']]
            field_description['selection_type'] = 'boolean'
