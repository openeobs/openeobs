# -*- coding: utf-8 -*-
from openerp import models


class FormDescription(models.TransientModel):

    _name = 'nh.clinical.form_description'

    @classmethod
    def to_dict(cls, model):
        form_description = []
        field_utils = cls.pool['nh.clinical.field_utils']
        obs_fields = field_utils.get_obs_fields(model)
        for field in obs_fields:
            field_description = {
                'name': field.name,
                'type': field.type,
                'label': field.string,
                'selection': field.selection,
                'selection_type': 'text',
                'initially_hidden': False,
                'required': field.required,
                'necessary': field.necessary
            }
            form_description.append(field_description)
        desired_order = model.get_obs_field_order()
        form_description.sort(key=lambda e: desired_order.index(e['name']))
        return form_description
