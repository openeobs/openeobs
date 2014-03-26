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
    
    def init(self, cr):
        self._events.append(['t4.clinical.patient.placement', self._name])

    def create(self, cr, uid, vals, context=None):
        current_spell = self.browse_domain(cr, uid, [('patient_id','=',vals['patient_id']),('state','in',['started'])], context)
        if current_spell:
            res = current_spell.id
            _logger.warn("Attempt to admit a patient with active spell of care! Current spell ID=%s returned." % current_spell.id)
        else:        
            res = super(t4_clinical_spell, self).create(cr, uid, vals, context)
        return res
    
    def get_spell_browse(self, cr, uid, pateint_id, context=None):
        spell_id = spell_pool.search(cr, uid, [('patient_id', '=', patient_id),('state', '=', 'started')])
        if spell_id:
            spell_id = spell_id[0]

    def on_placement_complete(self, cr, uid, activity_id, context):
        activity_pool = self.pool['t4.clinical.activity']
        placement_activity = activity_pool.browse(cr, uid, activity_id)
        spell_activity_id = activity_pool.get_patient_spell_activity_id(cr, uid, placement_activity.patient_id.id, context)
        activity_pool.submit(cr, uid, spell_activity_id, {'location_id': placement_activity.data_ref.location_id.id})
        return True
    
    def event(self, cr, uid, model, event, activity_id, context=None):
        
        if model == 't4.clinical.patient.placement' and event == "complete":
            self.on_placement_complete(cr, uid, activity_id, context)
        #super(t4_clinical_spell, self).event(cr, uid, model, event, activity_id, context)
