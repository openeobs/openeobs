# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.task import except_if
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
        return res
        
    def get_patient_location_browse(self, cr, uid, patient_id, context=None):
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
        return res
        
    def get_patient_location_browse(self, cr, uid, patient_id, context=None):
        """
        returns latest location
        """
        domain = [('state','=','completed'), ('patient_id','=',patient_id)]
        ids = self.search(cr, uid, domain, context=context, limit=1, order='id desc')
        return ids and self.browse(cr, uid, ids[0], context).location_id or False
    
    def complete(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        placement = task_pool.browse_ref(cr, uid, task_id, 'data_ref', context)
        except_if(not placement.patient_id or not placement.location_id, msg="Can't complete placement task without patient and/or location")

class t4_clinical_patient_discharge(orm.Model):
    _name = 't4.clinical.patient.discharge'    
    _inherit = ['t4.clinical.task.data']
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True), # domain=[('is_patient','=',True)])

        
        #...
    }

    def complete(self, cr, uid, task_id, context=None):
        
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)
        discharge = task.data_ref
        # get spell.pos_id.lot_discharge_id
        spell_pool = self.pool['t4.clinical.spell']
        spell = spell_pool.get_patient_spell_browse(cr, uid, discharge.patient_id.id, context)
        # patient
        patient_pool = self.pool['t4.clinical.patient']
        location = patient_pool.current_patient_location_browse(cr, uid, discharge.patient_id.id, context)
        #import pdb; pdb.set_trace()
        # move to discharge_lot
        move_pool = self.pool['t4.clinical.patient.move']
        move_task_id = move_pool.create_task(cr, uid, 
            {'parent_id': task_id}, 
            {'patient_id': discharge.patient_id.id, 'location_id':location.pos_id.lot_discharge_id.id or location.pos_id.location_id.id}, 
            context)
        task_pool.start(cr, uid, move_task_id, context)
        task_pool.complete(cr, uid, move_task_id, context)      
        # complete spell
        spell_pool.complete(cr, uid, spell.id, context)
        return True  
        
        
class t4_clinical_patient_admission(orm.Model):
    _name = 't4.clinical.patient.admission'    
    _inherit = ['t4.clinical.task.data']
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True), # domain=[('is_patient','=',True)])
        'location_id': fields.many2one('t4.clinical.location', 'Initial Location')
        
        #...
    }
    
    def complete(self, cr, uid, task_id, context=None):
        #import pdb; pdb.set_trace()
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)
        admission = task.data_ref
        
        # spell
        spell_pool = self.pool['t4.clinical.spell']
        spell_task_id = spell_pool.create_task(cr, uid, 
           {},
           {'patient_id': admission.patient_id.id}, 
           context=None)
        task_pool.start(cr, uid, spell_task_id, context)
        task_pool.write(cr, uid, admission.task_id.id, {'parent_id': spell_task_id}, context)
        # patient move
        move_pool = self.pool['t4.clinical.patient.move']
        move_task_id = move_pool.create_task(cr, uid, 
            {'parent_id': admission.task_id.id}, 
            {'patient_id': admission.patient_id.id, 'location_id':admission.location_id.id}, 
            context)
        task_pool.start(cr, uid, move_task_id, context)
        task_pool.complete(cr, uid, move_task_id, context)
        # patient placement
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_task_id = placement_pool.create_task(cr, uid, 
           {'parent_id': admission.task_id.id}, 
           {'patient_id': admission.patient_id.id}, 
           context)
        return True
    
    
   
class t4_clinical_location(orm.Model):
    _inherit = 't4.clinical.location'
    
    def available_location_browse(self, cr, uid, parent_id=None, context=None):
        pass
    
    
    
class t4_clinical_patient(orm.Model):
    _inherit = 't4.clinical.patient'
   
    def current_patient_location_browse(self, cr, uid, patient_id, context=None):
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_domain = [('patient_id','=',patient_id), ('state','=','completed')]
        placement = placement_pool.browse_domain(cr, uid, placement_domain, limit=1, order="date_terminated desc", context=context)
        placement = placement and placement[0]
        move_pool = self.pool['t4.clinical.patient.move']
        move_domain = [('patient_id','=',patient_id), ('state','=','completed')]
        move = move_pool.browse_domain(cr, uid, move_domain, limit=1, order="date_terminated desc", context=context)
        move = move and move[0]
        res = False
        if placement and move:
            res = placement.date_terminated > move.date_terminated and placement.location_id or move.location_id
        elif placement and not move:
            res = placement.location_id
        elif not placement and move:
            res = move.location_id
        return res
    
      
    
    
    
    