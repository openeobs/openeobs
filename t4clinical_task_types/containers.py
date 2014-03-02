# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_spell(orm.Model):
    _name = 't4.clinical.spell'
    _inherit = ['t4.clinical.task.data']
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'location_id': fields.many2one('t4.clinical.location', 'Placement Location'),
        'pos_id': fields.related('location_id', 'pos_id', type='many2one', relation='t4.clinical.pos', string='POS')
        #...
    }
    
    def create(self, cr, uid, vals, context=None):
        current_spell = self.browse_domain(cr, uid, [('patient_id','=',vals['patient_id']),('state','in',['started'])], context)
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



class t4_clinical_patient(orm.Model):
    _inherit = 't4.clinical.patient'    
    
    def get_patient_spell_browse(self, cr, uid, patient_id, context=None):
        """
        returns started spell for the patient or False
        """
        spell_pool = self.pool['t4.clinical.spell']
        res = spell_pool.browse_domain(cr, uid, [('patient_id','=',patient_id),('state','in',['started'])], context)
        res = res and res[0]
        return res