# -*- coding: utf-8 -*-
from openerp import fields


def is_obs_field(field):
    return type(field) is Selection


class Selection(fields.Selection):

    def __init__(self, selection=None, string=None, necessary=True, **kwargs):
        super(Selection, self).__init__(
            selection=selection, string=string, necessary=necessary, **kwargs
        )
