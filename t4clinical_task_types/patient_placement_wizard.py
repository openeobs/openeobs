# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.task import except_if
import logging        
_logger = logging.getLogger(__name__)



class t4_clinical_patient_placement_wizard(orm.Model):
    _name = 't4.clinical.patient.placement.wizard'
    _columns = {
        'placement_ids': fields.many2many('t4.clinical.patient.placement', 'Placements Tasks'),
        
    }