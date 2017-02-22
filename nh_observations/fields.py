# -*- coding: utf-8 -*-
"""
Extension of Odoo's field classes to add the 'necessary' attribute.

The necessary attribute declares whether or not a field must be populated in
order for an observation to be considered 'full'.

Fields which represent the data that actually makes up an observation
therefore need to use the types in this module rather than Odoo's own fields.
"""
from openerp import fields as odoo_fields


def get_odoo_field_type_classes():
    selection_type = odoo_fields.MetaField.by_type['selection']
    return selection_type

def set_odoo_field_type_classes(classes):
    odoo_fields.MetaField.by_type['selection'] = classes


odoo_field_type_classes = get_odoo_field_type_classes()


class Selection(odoo_fields.Selection):

    def __init__(self, selection=None, string=None, necessary=True, **kwargs):
        super(Selection, self).__init__(
            selection=selection, string=string, necessary=necessary, **kwargs
        )


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
set_odoo_field_type_classes(odoo_field_type_classes)
