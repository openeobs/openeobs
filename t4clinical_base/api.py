# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID

import logging        
_logger = logging.getLogger(__name__)

    
class t4_clinical_api(orm.AbstractModel):
    _name = 't4.clinical.api'
       
    def get_not_palced_patient_ids(self, cr, uid, location_id=None, context=None):
        domain = [('state','=','started'),('location_id.usage','not in', ['bed'])]
        location_id and  domain.append(('location_id','child_of',location_id))
        spell_pool = self.pool['t4.clinical.spell']
        spell_ids = spell_pool.search(cr, uid, domain)
        patient_ids = [s.patient_id.id for s in spell_pool.browse(cr, uid, spell_ids, context)]
        return patient_ids
    

    def get_patient_spell_activity_id(self, cr, uid, patient_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        domain = [('patient_id','=',patient_id),('state','=','started'),('data_model','=','t4.clinical.spell')]
        spell_activity_id = activity_pool.search(cr, uid, domain)
        if not spell_activity_id:
            return False
        if len(spell_activity_id) >1:
            _logger.warn("For pateint_id=%s found more than 1 started spell_activity_ids: %s " % (patient_id, spell_activity_id))
        return spell_activity_id[0]


    def get_patient_spell_activity_browse(self, cr, uid, patient_id, context=None):
        spell_activity_id = self.get_patient_spell_activity_id(cr, uid, patient_id, context)
        if not spell_activity_id:
            return False
        return self.browse(cr, uid, spell_activity_id, context)

    def set_activity_trigger(self, cr, uid, patient_id, data_model, unit, unit_qty, context=None):
        trigger_pool = self.pool['t4.clinical.patient.activity.trigger']
        trigger_id = trigger_pool.search(cr, uid, [('patient_id','=',patient_id),('data_model','=',data_model)])
        if trigger_id:
            trigger_id = trigger_id[0]
            trigger_pool.write(cr, uid, trigger_id, {'active': False})
        trigger_data = {'patient_id': patient_id, 'data_model': data_model, 'unit': unit, 'unit_qty': unit_qty}
        trigger_id = trigger_pool.create(cr, uid, trigger_data)        
        _logger.debug("activity frequency for patient_id=%s data_model=%s set to %s %s(s)" % (patient_id, data_model, unit_qty, unit))
        return trigger_id

    def get_patient_current_location_browse(self, cr, uid, patient_id, context=None):
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

    def get_patient_current_location_id(self, cr, uid, patient_id, context=None):
        res = self.get_patient_current_location_browse(cr, uid, patient_id, context)
        res = res and res.id
        return res

    def get_patient_permanent_location_browse(self, cr, uid, patient_id, context=None):
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_domain = [('patient_id','=',patient_id), ('state','=','completed')]
        placement = placement_pool.browse_domain(cr, uid, placement_domain, limit=1, order="date_terminated desc", context=context)
        placement = placement and placement[0]
        res = placement and placement.location_id
        return res    
    
    def get_patient_permanent_location_id(self, cr, uid, patient_id, context=None):
        res = self.get_patient_permanent_location_browse(cr, uid, patient_id, context)
        res = res and res.id
        return res    

class t4_clinical_api_adt(orm.AbstractModel):
    _name = 't4.clinical.api.adt'
    


    
class t4_clinical_api_frontend(orm.AbstractModel):
    _name = 't4.clinical.api.frontend'