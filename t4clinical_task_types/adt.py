# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.task import except_if
import logging        
_logger = logging.getLogger(__name__)



class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        
        
    }

class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.new'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
        
    }

class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.discharge'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }

class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.transfer'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }
    
class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.merge'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }
    
class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.update'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }