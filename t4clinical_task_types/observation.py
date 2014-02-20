# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv

class test_observation(orm.Model):
    _name = 'test.observation'
    _inherit = ['t4.clinical.task.data']
    #_patient_domain = [('')]
    _columns = {
        'patient_id': fields.many2one('res.partner', 'Patient', readonly=True),
        'val1': fields.text('val1'),
        'val2': fields.text('val2')
    }
    
    
    
class test_observation2(orm.Model):
    _name = 'test.observation2'
    _inherit = ['t4.clinical.task.data']    
    _columns = {
        'val1': fields.text('val3'),
        'val2': fields.text('val4')
    }
    
class test_observation3(orm.Model):
    _name = 'test.observation3'
    _inherit = ['t4.clinical.task.data']    
    _columns = {
        'val1': fields.text('val1'),
        'val2': fields.text('val2')
    }