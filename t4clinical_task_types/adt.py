# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.task import except_if
import logging        
_logger = logging.getLogger(__name__)



class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt'
    _inherit = ['t4.clinical.task.data']       
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),
        'family_name': fields.text('familyName'),
        'given_name': fields.text('givenName'),
        'middle_names': fields.text('middleName'),  
        'dob': fields.datetime('DOB'),
        'gender': fields.char('Gender', size=1),      
        'sex': fields.char('Sex', size=1),
    }

class t4_clinical_adt_patient_register(orm.Model):
    _name = 't4.clinical.adt.patient.register'
    _inherit = ['t4.clinical.adt']      
    _columns = { 
    }
    
    def submit(self, cr, uid, task_id, vals, context=None):
        except_if(not 'patient_identifier' in vals.keys() and not 'other_identifier' in vals.keys(),
              msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        patient_domain = [(k,'=',v) for k,v in vals.iteritems()]
        patient_id = patient_pool.search(cr, uid, patient_domain)
        if patient_id:
            patient_id = patient_id[0]
            except_if(patient_id, msg="Patient with the data submitted already exists! Data: %s" % vals)
            # handle duplicate patient here        
        patient_pool = self.pool['t4.clinical.patient']
        patient_pool.create(cr, uid, vals, context)
        super(t4_clinical_adt, self).submit(cr, uid, task_id, vals, context)
        return True
        

class t4_clinical_adt_patient_admit(orm.Model):
    _name = 't4.clinical.adt.patient.admit'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'location': fields.text('Location'),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"), 
        'other_identifier': fields.text("Other Identifier")              
    }
    def submit(self, cr, uid, task_id, vals, context=None):
#         except_if(not 'patient_identifier' in vals.keys() and not 'other_identifier' in vals.keys(),
#               msg="patient_identifier or other_identifier not found in submitted data!")
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.search(cr, uid, [('code','=',vals['location'])])
        except_if(not location_id, msg="Location not found!")
        location_id = location_id[0]
        
        patient_pool = self.pool['t4.clinical.patient']
        patient_id = patient_pool.search(cr, uid, [('other_identifier','=',vals['other_identifier'])])
        if not patient_id:
            except_if(True, "Patient not found!")
        elif len(patient_id) > 1:
            except_if(True, "More than one patient found!")
        patient_id = patient_id[0]
        super(t4_clinical_adt_patient_admit, self).submit(cr, uid, task_id, vals, context)
        admission_pool = self.pool['t4.clinical.patient.admission']
        vals_copy = vals.copy()

        #del vals_copy['location']        
        vals_copy.update({'location_id': location_id})  

        #del vals_copy['other_identifier']        
        vals_copy.update({'patient_id': patient_id})  
        admission_task_id = admission_pool.create_task(cr, uid, {}, vals_copy)
        task_pool = self.pool['t4.clinical.task']
        task_pool.start(cr, uid, admission_task_id, context)
        ctx = context and context.copy() or {}
        ctx.update({'source_task_id': task_id})        
        tasks = task_pool.complete(cr, uid, admission_task_id, ctx)
        return True    

class t4_clinical_adt_patient_discharge(orm.Model):
    _name = 't4.clinical.adt.patient.discharge'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }

class t4_clinical_adt_patient_transfer(orm.Model):
    _name = 't4.clinical.adt.patient.transfer'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }
    
class t4_clinical_adt_patient_merge(orm.Model):
    _name = 't4.clinical.adt.patient.merge'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'from_identifier': fields.text('From patient Identifier'),
        'into_identifier': fields.text('Into Patient Identifier'),        
    }
    
    def submit(self, cr, uid, task_id, vals, context=None):
        except_if(not ('from_identifier' in vals and 'into_identifier' in vals), msg="from_identifier or into_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        from_id = self.search(cr, uid, [('other_identifier', '=', vals['from_identifier'])])
        into_id = self.search(cr, uid, [('other_identifier', '=', vals['into_identifier'])])    
        # compare and combine data
        patient_pool.write(cr, uid, from_id, {'active':False}, context)
        
             
    
class t4_clinical_adt_patient_update(orm.Model):
    _name = 't4.clinical.adt.patient.update'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }