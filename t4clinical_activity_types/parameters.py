# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
import logging        
_logger = logging.getLogger(__name__)

frequencies = [
    (15, 'Every 15 Minutes'),
    (30, 'Every 30 Minutes'),
    (60, 'Every Hour'),
    (120, 'Every 2 Hours'),
    (240, 'Every 4 Hours'),
    (360, 'Every 6 Hours'),
    (720, 'Every 12 Hours'),
    (1440, 'Every Day')
]

class t4_clinical_o2level(orm.Model):
    _name = 't4.clinical.o2level'      
    _columns = {
        'name': fields.char("O2 Target Name", size=5),
        'min': fields.integer("Min"),
        'max': fields.integer("Max"),               
    }
    
class t4_clinical_patient_o2target(orm.Model):
    _name = 't4.clinical.patient.o2target'
    _inherit = ['t4.activity.data']       
    _rec_name = 'level_id'
    _columns = {
        'level_id': fields.many2one('t4.clinical.o2level', 'O2 Level', required=True),                
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
   }
    
class t4_clinical_patient_mrsa(orm.Model):
    _name = 't4.clinical.patient.mrsa'
    _inherit = ['t4.activity.data'] 
    _columns = {
        'mrsa': fields.boolean('MRSA', required=True),                
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
   }

class t4_clinical_patient_diabetes(orm.Model):
    _name = 't4.clinical.patient.diabetes'
    _inherit = ['t4.activity.data'] 
    _columns = {
        'diabetes': fields.boolean('Diabetes', required=True),                
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
   }     