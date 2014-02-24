# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
    
class test_observation3(orm.Model):
    _name = 'test.observation3'
    _inherit = ['t4.clinical.task.data']    
    _columns = {
        'val1': fields.text('val1'),
        'val2': fields.text('val2')
    }

 
    
class t4_clinical_observation_height_weight(orm.Model):
    _name = 't4.clinical.observation.height_weight'
    _inherit = ['t4.clinical.task.data']
    _columns = {
                
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),                
        'height': fields.float('Height', required=True),
        'weight': fields.float('Weight', required=True),
    }
    
    def complete(self, cr, uid, task_ids, context=None):
        return True
    