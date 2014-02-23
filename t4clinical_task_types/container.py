# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_spell(orm.Model):
    _name = 't4.clinical.spell'
    _inherit = ['t4.clinical.task.data']
    _rec_name = 'patient_id'
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True), # domain=[('is_patient','=',True)])
        'location_id': fields.many2one('t4.clinical.location', 'Assigned Location', help="If location.usage != 'bed' then the patient is without a bed")
        
        #...
    }
    def current_spell_browse(self, cr, uid, patient_id, location_id, context=None):
        spell_filter = [('patient_id','=',patient_id),('state','in',['started'])]
        spell_id = self.search(cr, uid, spell_filter, context=context)
        if spell_id:
            spell_id = spell_id[0]
            return self.browse(cr, uid, spell_id, context)
        return False
        
    def admit_patient(self, cr, uid, patient_id, location_id, context=None):
        """
        parent_task_id is expected in context
        """
        context = context and context or {}
        current_spell = self.current_spell_browse(self, cr, uid, patient_id, location_id, context=None)
        if current_spell:
            _logger.warn("Attempt to admit a patient with active spell of care! Current spell used, location remains in tact.")
            task_id = current_spell.task_id.id
        else:
            location_pool = self.pool['t4.clinical.location']
            location = self.browse(cr,uid, location_id, context)
              
            task_pool = self.pool['t4.clinical.task']
            vals_data = {'patient_id': patient_id, 'location_id': location.type=='poc' and location.usage=='bed' and location_id or False}
            spell_task_id = self.create_task(cr, uid, vals_data, context)
            task_pool.start(cr, uid, spell_task_id, context)
            move_pool = self.pool['t4.clinical.patient.move']
            vals_data = {'src_location_id': False, 'dst_location_id': location_id, 'patient_id': patient_id}
            move_pool.create_task(cr, uid, vals_data, context)
            _logger.warn("New Spell of Care task ID=%s successfully created for Patient ID=%s. Current Location ID=%s" % (spell_task_id, patient_id, location_id))
            # create a patient.move to the location
        return spell_task_id
        
    def assign_patient(self, cr, uid, patient_id, poc_location_id): # assign to bed
         pass    

    def discharge_patient(self, cr, uid, patient_id, location_id, context=None):
        current_spell = self.current_spell_browse(self, cr, uid, patient_id, location_id, context=None)
        
        
# class t4_clinical_pos(orm.Model):
#     _name = 't4.clinical.pos'    
#     _inherit = 't4.clinical.pos'
    

    
    
class t4_clinical_complaint(orm.Model):
    _name = 't4.clinical.complaint'
    _inherit = ['t4.clinical.task.data']
    _rec_name = 'patient_id' # name, date_start  
    _columns = {
        'patient_id': fields.many2one('res.partner', 'Patient'), # domain=[('is_patient','=',True)])
        'descr': fields.text('Description')
        #...
    }