# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)
from openerp import tools

class t4_???(orm.Model):
    _name = "t4.??"
    _description = "???"
    _auto = False
    _table = "???"
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
                drop view if exists {view};
                create or replace view {view} as (


                THE VIEW



                )
        """ % (view = self._table))