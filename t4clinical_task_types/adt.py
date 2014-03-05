# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.task import except_if
import logging        
_logger = logging.getLogger(__name__)



class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt'
    _inherit = ['t4.clinical.task.data']
    _identifiers = ['otherId','patientId']
    _optional_fields = ['familyName', 'givenName', 'middleNames']         
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'patientid': fields.text('patientId'),
        'otherid': fields.text('otherId'),
        'familyname': fields.text('familyName'),
        'givenname': fields.text('givenName'),
        'middlename': fields.text('middleName'),        
        
    }

class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.patient.register'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = { 
    }
    
    def submit(self, cr, uid, task_id, vals, context=None):
        if not 'patientid' in vals.keys() and not 'otherid' in vals.keys():
            except_if(not 'nhs_number' in vals.keys() and not 'hospital_number' in vals.keys(),
                  msg="Neither patientid nor otherid found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        fields_map = {
              'patientid': 'patient_identifier',
              'otherid': 'other_identifier',
              'familyname': 'family_name',
              'givenname': 'given_name',
              'middlename': 'middle_names'
        }
        vals_patient = {fieldsmap[lowercase(k)]: v for k, v in vals.iteritems()}
        vals_adt = {lowercase(k): v for k, v in vals.iteritems()}
        super(t4_clinical_adt, self).submit(cr, uid, task_id, vals_adt, context)
        patient_pool.create(cr, uid, vals_patient, context)
        return True
        

class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.patient.admit'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = { 
    }
    

class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.patient.discharge'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }

class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.patient.transfer'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }
    
class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.patient.merge'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'from_patientid': fields.text('From patientId'),
        'into_patientid': fields.text('Into patientId'),        
    }
    
    def submit(self, cr, uid, task_id, vals, context=None):
        except_if(vals[''])
        patient_pool = self.pool['t4.clinical.patient']
        oldId_id = self.search(cr, uid, [('other_identifier', '=', oldIdentifier)])
        newIdentifier_id = self.search(cr, uid, [('other_identifier', '=', newIdentifier)])         
    
class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt.patient.update'
    _inherit = ['t4.clinical.task.data', 't4.clinical.adt']      
    _columns = {
    }