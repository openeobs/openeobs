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
        #import pdb; pdb.set_trace()
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

class t4_clinical_api_adt(orm.AbstractModel):
    _name = 't4.clinical.api.adt'
    


    
class t4_clinical_api_frontend(orm.AbstractModel):
    _name = 't4.clinical.api.frontend'