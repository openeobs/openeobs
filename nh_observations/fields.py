# -*- coding: utf-8 -*-
"""
Extension of Odoo's field classes to add the 'necessary' attribute.

The necessary attribute declares whether or not a field must be populated in
order for an observation to be considered 'full'.

Fields which represent the data that actually makes up an observation
therefore need to use the types in this module rather than Odoo's own fields.
"""
import copy

from openerp import fields as odoo_fields


def get_odoo_field_type_classes():
    type_to_class_dict = copy.deepcopy(odoo_fields.MetaField.by_type)
    return type_to_class_dict


def set_odoo_field_type_classes(type_to_class_dict):
    odoo_fields.MetaField.by_type = type_to_class_dict


odoo_field_type_to_class_dict = get_odoo_field_type_classes()


class ObservationField(odoo_fields.Field):

    def __init__(self, string=None, necessary=True, initially_hidden=False,
                 reference=None, minimum=None, maximum=None, *args, **kwargs):
        super(ObservationField, self).__init__(
            string=string, necessary=necessary,
            initially_hidden=initially_hidden, reference=reference,
            minimum=minimum, maximum=maximum, *args, **kwargs
        )


class MultiSelect(ObservationField):
    pass


class Selection(odoo_fields.Selection, ObservationField):

    def __init__(self, *args, **kwargs):
        super(Selection, self).__init__(
            *args, **kwargs
        )


class Text(odoo_fields.Text):

    def __init__(self, string=None, necessary=True, **kwargs):
        super(Text, self).__init__(
            string=string, necessary=necessary, **kwargs
        )


class Integer(odoo_fields.Integer):

    def __init__(self, string=None, necessary=True, **kwargs):
        super(Integer, self).__init__(
            string=string, necessary=necessary, **kwargs
        )


class Many2one(odoo_fields.Many2one):

    def __init__(self, comodel_name=None, string=None, necessary=True,
                 **kwargs):
        super(Many2one, self).__init__(
            comodel_name=comodel_name, string=string, necessary=necessary,
            **kwargs
        )


class One2many(odoo_fields.One2many):

    def __init__(self, comodel_name=None, inverse_name=None, string=None,
                 necessary=True, **kwargs):
        super(One2many, self).__init__(
            comodel_name=comodel_name, inverse_name=inverse_name,
            string=string, necessary=necessary, **kwargs
        )


class Many2Many(odoo_fields.Many2many):

    def __init__(self, comodel_name=None, relation=None, column1=None,
                 column2=None, string=None, necessary=True, **kwargs):
        super(Many2Many, self).__init__(
            comodel_name=comodel_name,
            relation=relation,
            column1=column1,
            column2=column2,
            string=string,
            necessary=necessary,
            **kwargs
        )


class Float(odoo_fields.Float):

    def __init__(self, *args, **kwargs):
        super(Float, self).__init__(*args, **kwargs)


# Hack to reset the `MetaField.by_type` dictionary to the state it was in
# before these class declarations were read.
#
# For some reason Odoo maintains the `by_type` dictionary as a mapping between
# field types and the classes they should be instantiated from.
#
# Only V7 fields and 'manual' V8 fields appear to be affected by this, but it's
# troublesome because it means that without the reset below, all subsequent
# field declarations are given a type from `nh_observations.fields` despite
# being declared as ordinary Odoo fields like so:
#
#     _columns = {
#         `foo: openerp.osv.fields.selection`
#     }
set_odoo_field_type_classes(odoo_field_type_to_class_dict)
