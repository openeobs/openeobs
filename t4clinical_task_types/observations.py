# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv

fields.xmlrpclib.allow_none = True

class t4_clinical_patient_observation(orm.AbstractModel):
    _name = 't4.clinical.patient.observation'
    _required = [] # fields required for complete observation
    
    def _is_partial(self, cr, uid, ids, field, args, context=None):
        ids = isinstance(ids, (tuple, list)) and ids or [ids]
        if not self._required:
            return {id: False for id in ids}
        res = {obs['id']: not bool(set(self._required) & set(eval(obs['none_values']))) for obs in self.read_none(cr, uid, ids, ['none_values'], context)}
        return res    
    
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'is_partial': fields.function(_is_partial, type='boolean', string='Is Partial?'),
        'none_values': fields.text('Non-updated fields'),
        
    }
    _defaults = {

     }
    
    def create(self, cr, uid, vals, context=None):
        none_values = list(set(vals.keys()) & set(self._required))
        vals.update({'none_values': none_values})
        return super(t4_clinical_patient_observation, self).create(cr, uid, vals, context)        
    
    
                
    def write(self, cr, uid, ids, vals, context=None):
        ids = isinstance(ids, (tuple, list)) and ids or [ids]
        if not self._required:
            return super(t4_clinical_patient_observation, self).write(cr, uid, ids, vals, context)
        for obs in self.read(cr, uid, ids, ['none_values'], context):
            none_values = list(set(vals.keys()) & set(eval(obs['none_values'])))
            vals.update({'none_values': none_values})
            super(t4_clinical_patient_observation, self).write(cr, uid, obs['id'], vals, context)
        return True

   

        
class test_observation3(orm.Model):
    _name = 'test.observation3'
    _inherit = ['t4.clinical.task.data']    
    _columns = {
        'val1': fields.text('val1'),
        'val2': fields.text('val2')
    }

 
    
class t4_clinical_patient_observation_height_weight(orm.Model):
    _name = 't4.clinical.patient.observation.height_weight'
    _inherit = ['t4.clinical.task.data','t4.clinical.patient.observation']
    _required = ['height', 'weight']
    _columns = {
                       
        'height': fields.float('Height'),
        'weight': fields.float('Weight'),
    }
    

    
    def complete(self, cr, uid, task_ids, context=None):
        super(t4_clinical_patient_observation_height_weight, self).complete(cr, uid, task_id, context)
        return True

    def get_task_location_id(self, cr, uid, task_id, context=None):
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement = placement_pool.browse_domain(cr, uid, [], limit=1, order="date_terminated desc")
        #import pdb; pdb.set_trace()
        location_id = placement and placement[0].location_id.id or False
        return location_id     