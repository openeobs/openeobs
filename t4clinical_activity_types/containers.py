# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_spell(orm.Model):
    _name = 't4.clinical.spell'
    _inherit = ['t4.clinical.activity.data']
    
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'location_id': fields.many2one('t4.clinical.location', 'Placement Location'),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"),
        #...
    }
    _defaults = {
         'code': lambda s, cr, uid, c: s.pool['ir.sequence'].next_by_code(cr, uid, 't4.clinical.spell', context=c) 
     }

    def create(self, cr, uid, vals, context=None):
        current_spell = self.browse_domain(cr, uid, [('patient_id','=',vals['patient_id']),('state','in',['started'])], context)
        if current_spell:
            res = current_spell.id
            _logger.warn("Attempt to admit a patient with active spell of care! Current spell ID=%s returned." % current_spell.id)
        else:        
            res = super(t4_clinical_spell, self).create(cr, uid, vals, context)
        return res
