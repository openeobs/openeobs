# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_spell(orm.Model):
    _name = 't4.clinical.spell'
    _inherit = ['t4.clinical.task.data']
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True), # domain=[('is_patient','=',True)])
        'location_id': fields.many2one('t4.clinical.location', 'Assigned Location', help="If location.usage != 'bed' then the patient is without a bed")
        
        #...
    }
    def get_spell(self, cr, uid, patient_id, context=None):
        """
        returns started spell for the patient or False
        """
        spell_filter = [('patient_id','=',patient_id),('state','in',['started'])]
        spell_id = self.search(cr, uid, spell_filter, context=context)
        res = spell_id and self.browse(cr, uid, spell_id[0], context) or False
        return res
    
    def create(self, cr, uid, vals, context=None):
        current_spell = self.get_spell(cr, uid, vals['patient_id'], context)
        if current_spell:
            res = current_spell.id
            _logger.warn("Attempt to admit a patient with active spell of care! Current spell ID=%s returned." % current_spell.id)
        else:        
            res = super(t4_clinical_spell, self).create(cr, uid, vals, context)
        return res
        
        
    
class t4_clinical_complaint(orm.Model):
    _name = 't4.clinical.complaint'
    _inherit = ['t4.clinical.task.data']
    _rec_name = 'patient_id' # name, date_start  
    _columns = {
        'patient_id': fields.many2one('res.partner', 'Patient'), # domain=[('is_patient','=',True)])
        'descr': fields.text('Description')
        #...
    }