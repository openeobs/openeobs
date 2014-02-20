# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv

class t4_clinical_patient_move(orm.Model):
    _name = 't4.clinical.patient.move'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'src_location_id': fields.many2one('t4.clinical.location', 'Source Location'),
        'dst_location_id': fields.many2one('t4.clinical.location', 'Destination Location'),
        'patient_id': fields.many2one('res.partner', 'Patient'),
        'reason': fields.text('Reason'),
        
    }
    
class t4_clinical_patient_admission(orm.Model):
    _name = 't4.clinical.patient.addmission'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'move_id': fields.many2one('t4.clinical.patient.move', 'Patient Move'),
        'move_task_id': fields.related('move_id', 'task_id', type='many2one', relation='t4.clinical.task')
    }