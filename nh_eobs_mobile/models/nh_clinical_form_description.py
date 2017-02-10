# -*- coding: utf-8 -*-
from openerp import models

from openerp.addons.nh_observations.fields import is_obs_field


class FormDescription(models.TransientModel):

    _name = 'nh.clinical.form_description'

    @classmethod
    def to_dict(cls, model=None):
        form_description = []
        model_fields = model._fields.values()
        obs_fields = [field for field in model_fields
                      if is_obs_field(field)]
        for field in obs_fields:
            field_description = {
                'name': field.name,
                'type': field.type,
                'label': field.string,
                'selection': field.selection,
                'selection_type': 'text',
                'initially_hidden': False,
                'required': str(field.required).lower(),
                'necessary': str(field.necessary).lower()
            }
            form_description.append(field_description)
        return form_description
