# -*- coding: utf-8 -*-
from openerp import models


class FormDescription(models.TransientModel):

    _name = 'nh.clinical.form_description'

    @classmethod
    def to_dict(cls, model):
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
        desired_order = model.get_obs_field_order()
        form_description.sort(key=lambda e: desired_order.index(e.get('name')))

    @staticmethod
    def _get_type(field):
        if field.type == 'char':
            return 'text'
        elif field.type == 'boolean':
            return 'selection'
        return field.type

    @staticmethod
    def _add_size_if_necessary(field, field_description):
        if hasattr(field, 'size') and field.size:
            field_description['size'] = field.size

    @staticmethod
    def _add_selection_keys_if_necessary(field, field_description):
        if field.type == 'selection':
            field_description['selection'] = field.selection
            field_description['selection_type'] = 'text'
        elif field.type == 'boolean':
            field_description['selection'] = [[True, 'Yes'], [False, 'No']]
            field_description['selection_type'] = 'boolean'
