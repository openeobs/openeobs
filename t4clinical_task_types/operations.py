# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_patient_move(orm.Model):
    _name = 't4.clinical.patient.move'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        #'src_location_id': fields.many2one('t4.clinical.location', 'Source Location'),
        'location_id': fields.many2one('t4.clinical.location', 'Destination Location', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
        
    }
    def create(self, cr, uid, vals, context=None):
   
        res = super(t4_clinical_patient_move, self).create(cr, uid, vals, context)
        _logger.info("New Patient Move ID=%s successfully created" % (res))
        return res
        
    def get_location(self, cr, uid, patient_id, context=None):
        """
        returns latest location
        """
        domain = [('state','=','completed'), ('patient_id','=',patient_id)]
        ids = self.search(cr, uid, domain, context=context, limit=1, order='id desc')
        return ids and self.browse(cr, uid, ids[0], context).location_id or False


class t4_clinical_patient_placement(orm.Model):
    _name = 't4.clinical.patient.placement'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'location_id': fields.many2one('t4.clinical.location', 'Destination Location'),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
        
    }
    
    def create(self, cr, uid, vals, context=None):
   
        res = super(t4_clinical_patient_placement, self).create(cr, uid, vals, context)
        _logger.info("New Patient Placement ID=%s successfully created" % (res))
        return res
        
    def get_location(self, cr, uid, patient_id, context=None):
        """
        returns latest location
        """
        domain = [('state','=','completed'), ('patient_id','=',patient_id)]
        ids = self.search(cr, uid, domain, context=context, limit=1, order='id desc')
        return ids and self.browse(cr, uid, ids[0], context).location_id or False

class t4_clinical_admission(orm.Model):
    _name = 't4.clinical.patient.admission'    
    _inherit = ['t4.clinical.task.data']
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True), # domain=[('is_patient','=',True)])
        'location_id': fields.many2one('t4.clinical.location', 'Initial Location')
        
        #...
    }
    
    def complete(self, cr, uid, task_ids, context=None):
        res = True
        task_pool = self.pool['t4.clinical.task']
        spell_pool = self.pool['t4.clinical.spell']
        move_pool = self.pool['t4.clinical.patient.move']
        placement_pool = self.pool['t4.clinical.patient.placement']
        task_ids = isinstance(task_ids, (list, tuple)) and task_ids or [task_ids]
        adm_ids = self.search(cr, uid, [('task_id', 'in', task_ids)], context=context)
        #import pdb; pdb.set_trace()
        for adm in self.browse(cr, uid, adm_ids, context):
            spell_task_id = spell_pool.create_task(cr, uid, {},{'patient_id': adm.patient_id.id}, context=None)
            task_pool.start(cr, uid, spell_task_id, context)
            task_pool.write(cr, uid, adm.task_id.id, {'parent_id': spell_task_id}, context)
            move_task_id = move_pool.create_task(cr, uid, {'parent_id': adm.task_id.id}, {'patient_id': adm.patient_id.id, 'location_id':adm.location_id.id}, context)
            task_pool.start(cr, uid, move_task_id, context)
            task_pool.complete(cr, uid, move_task_id, context)
            # if location.type != poc and/or bed, create patient allocation task with parent_id = admission.task_id
            placement_idmove_task_id = placement_pool.create_task(cr, uid, {'parent_id': adm.task_id.id}, {'patient_id': adm.patient_id.id}, context)
        return res
    
    
    
    
    
    
    
    
    
    
    
    
    
    