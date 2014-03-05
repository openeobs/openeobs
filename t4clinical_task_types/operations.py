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
        super(t4_clinical_patient_placement, self).complete(cr, uid, task_id, context)
        task_pool = self.pool['t4.clinical.task']
        placement = task_pool.browse_ref(cr, uid, task_id, 'data_ref', context)
        except_if(not placement.patient_id or not placement.location_id, msg="Can't complete placement task without patient and/or location")

class t4_clinical_patient_discharge(orm.Model):
    _name = 't4.clinical.patient.discharge'    
    _inherit = ['t4.clinical.task.data']
    
    def _discharge2location_id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        placement_pool = self.pool['t4.clinical.patient.placement']
        for discharge in self.browse(cr, uid, ids, context):
            placement_id = placement_pool.search(cr, uid,
                                    [('state','=','completed'),('patient_id','=',discharge.patient_id.id)],
                                    order="date_terminated desc", limit=1)
            if not placement_id:
                res[discharge.id] = False
                continue
            placement_id = placement_id[0]
            placement = self.pool['t4.clinical.patient.placement'].browse(cr, uid, placement_id, context)
            res[discharge.id] = placement.location_id.id
        return res
    
    def _search_location_id(self, cr, uid, model, field_name, domain, context):
        #print model, field_name, domain
        
        location_pool = self.pool['t4.clinical.location']
        location_domain = [('id',domain[0][1], domain[0][2])]
        location_ids = location_pool.search(cr, uid, location_domain, context=context)
        patient_ids = []
        for location_id in location_ids:
            
            patient_ids.extend(location_pool.get_location_patient_ids(cr, uid, location_id, context))
        return [('patient_id','in',patient_ids)]
        
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True), # domain=[('is_patient','=',True)])
        'location_id': fields.function(_discharge2location_id, fnct_search=_search_location_id, type='many2one', relation='t4.clinical.location', string='Location')
        
        #...
    }

    def complete(self, cr, uid, task_id, context=None):
        super(t4_clinical_patient_discharge, self).complete(cr, uid, task_id, context)
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)
        assert task.patient_id, "Patient must be set!"
        assert task.location_id, "Patient must be set!"
        discharge = task.data_ref
        # patient
        patient_pool = self.pool['t4.clinical.patient']
        location = patient_pool.get_patient_location_browse(cr, uid, discharge.patient_id.id, context)
        #import pdb; pdb.set_trace()
        # move to discharge_lot
        move_pool = self.pool['t4.clinical.patient.move']
        move_task_id = move_pool.create_task(cr, uid, 
            {'parent_id': task_id}, 
            {'patient_id': discharge.patient_id.id, 
             'location_id':location.pos_id.lot_discharge_id.id or location.pos_id.location_id.id}, 
            context)
        task_pool.start(cr, uid, move_task_id, context)
        task_pool.complete(cr, uid, move_task_id, context)      
        # complete spell
        spell = patient_pool.get_patient_spell_browse(cr, uid, discharge.patient_id.id, context)
        task_pool.complete(cr, uid, spell.task_id.id, context)
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
        super(t4_clinical_patient_admission, self).complete(cr, uid, task_id, context)
        #import pdb; pdb.set_trace()
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)
        admission = task.data_ref
        
        # spell
        spell_task_data = context and context.get('source_task_id') and {'parent_id': context['source_task_id']} or {}
        spell_pool = self.pool['t4.clinical.spell']
        spell_task_id = spell_pool.create_task(cr, uid, 
           spell_task_data,
           {'patient_id': admission.patient_id.id}, 
           context=None)
        #import pdb; pdb.set_trace()
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
        res = {'admission_task_id': task_id,
               'spell_task_id': spell_task_id,
               'move_task_id': move_task_id,
               'placement_task_id': placement_task_id}
        return res
    
    
   
class t4_clinical_location(orm.Model):
    _inherit = 't4.clinical.location'
    
    def available_location_browse(self, cr, uid, parent_id=None, context=None):
        pass
    
    
    
class t4_clinical_patient(orm.Model):
    _inherit = 't4.clinical.patient'


    def get_patient_placement_browse(self, cr, uid, patient_id, context=None):
        pass

    def get_patient_move_browse(self, cr, uid, patient_id, context=None):
        pass

    def get_patient_admission_browse(self, cr, uid, patient_id, context=None):
        pass
   
    def get_patient_discharge_browse(self, cr, uid, patient_id, context=None):
        pass   
   
    def get_patient_location_browse(self, cr, uid, patient_id, context=None):
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


    def get_patient_location_id(self, cr, uid, patient_id, context=None):
        res = self.get_patient_location_browse(cr, uid, patient_id, context)
        res = res and res.id
        return res

class t4_clinical_task(orm.Model):
    _inherit = 't4.clinical.task'  
    
    def get_task_patient_id(self, cr, uid, task_id, context=None):
        """
        Data Model API call
        If the model is patient-related, returns patient_id, otherwise False
        By defult field 'patient_id' is taken as target patient
        """
        #import pdb; pdb.set_trace()
        res = False
        if 'patient_id' in self._columns.keys():
            data = self.browse_ref(cr, uid, task_id, 'data_ref', context=None)
            res = data.patient_id and data.patient_id.id
        return res
    
    def get_task_location_id(self, cr, uid, task_id, context=None):
        """
        Data Model API call
        If the model is location-related, returns location_id, otherwise False
        The location is not necessarily placed(assigned) location
        example: clinical.precedure data model which may happen outside of patient's ward and last for few minutes
        """
#         if task_id == 3775:
#             import pdb; pdb.set_trace()
        res = False
        if 'location_id' in self._columns.keys():
            data = self.pool['t4.clinical.task'].browse_ref(cr, uid, task_id, 'data_ref', context=None)
            res = data.location_id and data.location_id.id
        return res        

    def get_task_spell_id(self, cr, uid, task_id, context=None):
        """
        Data Model API call
        If the model is spell-related and has parent started, not terminated spell, returns spell_id, otherwise False
        By default current spell.id of patient (if any) returned 
        """
        res = False
        if 'patient_id' in self._columns.keys():
            data = self.pool['t4.clinical.task'].browse_ref(cr, uid, task_id, 'data_ref', context=None)
            if data:            
                patient_pool = self.pool['t4.clinical.patient']
                spell = patient_pool.get_patient_spell_browse(cr, uid, data.patient_id.id, context)
                res = spell.id
        return res    
    
    
class t4_clinical_location(orm.Model):
    _inherit = 't4.clinical.location'
    
    def get_location_patient_ids(self, cr, uid, location_id, context=None):
        # current spells
        task_pool = self.pool['t4.clinical.task']
        spell_tasks = self.browse_domain(cr, uid, [('data_model','=','t4.clinical.spell'),('state','=','started')])
        spell_pool = self.pool['t4.clinical.spell']
        spells = spell_pool.browse_domain(cr, uid, [('state','in',['started'])], context)        
        patients = [spell.patient_id for spell in spells]
        patient_pool = self.pool['t4.clinical.patient']
        patient_location_map = {patient.id: patient_pool.get_patient_location_id(cr, uid, patient.id, context) for patient in patients}
        patients_by_location = {}.fromkeys(patient_location_map.values(),[])
        for pat_id, loc_id in patient_location_map.iteritems():
            patients_by_location[loc_id].append(pat_id)
        return patients_by_location.get(location_id,[])
        
    
    
    
    
    
        