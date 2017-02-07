# -*- coding: utf-8 -*-
from openerp import models


class FieldToFormDescriptionConverter(models.AbstractModel):

    _name = 'field_to_form_description_converter'

    @classmethod
    def convert(cls, fields):
        form_description_fields = []
        for field in fields:
            form_description_field = {
                'name': field.name,
                'type': field.type,
                'label': field.string,
                'mandatory': field.required,
                'selection': field.selection,
                'selection_type': 'text',
                'initially_hidden': False
            }
            form_description_fields.append(form_description_field)
        return form_description_fields
