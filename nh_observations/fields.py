# -*- coding: utf-8 -*-
"""
Extension of Odoo's field classes to add the 'necessary' attribute.

The necessary attribute declares whether or not a field must be populated in
order for an observation to be considered 'full'.

Fields which represent that data that actually makes up an observation
therefore need to use the types in this module rather than Odoo's own fields.
"""
from openerp import fields as odoo_fields
from openerp import models


class FieldUtils(models.AbstractModel):

    _name = 'nh.clinical.field_utils'

    @classmethod
    def is_obs_field(self, field):
        return isinstance(field, Selection)

    def get_obs_fields(self, model):
        fields = model._fields.values()
        return [field for field in fields if self.is_obs_field(field)]


class Selection(odoo_fields.Selection):

    def __init__(self, selection=None, string=None, necessary=True, **kwargs):
        super(Selection, self).__init__(
            selection=selection, string=string, necessary=necessary, **kwargs
        )
