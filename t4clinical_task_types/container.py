# -*- coding: utf-8 -*-

from openerp.osv import orm, fields

class t4_clinical_spell(orm.Model):
    _name = 't4.clinical.spell'
    _inherit = ['t4.clinical.task.data']
    _rec_name = 'patient_id' # name, date_start  
    _columns = {
        'patient_id': fields.many2one('res.partner', 'Patient'), # domain=[('is_patient','=',True)])
        
        #...
    }
    
class t4_clinical_complaint(orm.Model):
    _name = 't4.clinical.complaint'
    _inherit = ['t4.clinical.task.data']
    _rec_name = 'patient_id' # name, date_start  
    _columns = {
        'patient_id': fields.many2one('res.partner', 'Patient'), # domain=[('is_patient','=',True)])
        'descr': fields.text('Description')
        #...
    }