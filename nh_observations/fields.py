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


# TODO EOBS-2588: Get field order from declaration order
class Selection(odoo_fields.Selection):
    _slots = {
        'necessary': True,
    }


class Boolean(odoo_fields.Boolean):
    _slots = {
        'necessary': True,
    }


class Char(odoo_fields.Char):
    _slots = {
        'necessary': True,
    }


class Text(odoo_fields.Text):
    _slots = {
        'necessary': True,
    }


class Integer(odoo_fields.Integer):
    _slots = {
        'necessary': True,
    }


class Many2one(odoo_fields.Many2one):
    _slots = {
        'necessary': True,
    }


class One2many(odoo_fields.One2many):
    _slots = {
        'necessary': True,
    }


class Many2Many(odoo_fields.Many2many):
    _slots = {
        'necessary': True,
    }


class Float(odoo_fields.Float):
    _slots = {
        'necessary': True,
    }


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
