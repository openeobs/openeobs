# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
from openerp.addons.t4activity.activity import except_if
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_spell(orm.Model):
    _name = 't4.clinical.spell'
    _inherit = ['t4.activity.data']
    _rec_name = 'code'
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'location_id': fields.many2one('t4.clinical.location', 'Placement Location'),
        'pos_id': fields.many2one('t4.clinical.pos', 'Placement Location', required=True),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"),
        'ews_frequency': fields.integer("EWS Frequency", help="EWS frequency in minutes")
    }
    _defaults = {
         'code': lambda s, cr, uid, c: s.pool['ir.sequence'].next_by_code(cr, uid, 't4.clinical.spell', context=c),
         'ews_frequency': 15
     }

    def create(self, cr, uid, vals, context=None):
        current_spell_id = self.search(cr, uid, [('patient_id','=',vals['patient_id']),('state','in',['started'])], context)
#         if current_spell_id:
#             import pdb; pdb.set_trace()
        if current_spell_id:
            res = current_spell[0]
            _logger.warn("Started spell already exists! Current spell ID=%s returned." % current_spell_id[0])
        else:        
            res = super(t4_clinical_spell, self).create(cr, uid, vals, context)
        return res
