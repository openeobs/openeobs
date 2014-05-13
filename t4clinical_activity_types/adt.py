# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
from openerp import SUPERUSER_ID
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt'
    _inherit = ['t4.activity.data']       
    _columns = {
    }


class t4_clinical_adt_patient_register(orm.Model):
    _name = 't4.clinical.adt.patient.register'
    _inherit = ['t4.activity.data']      
    _columns = { 
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS', required=True),
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),
        'family_name': fields.text('familyName'),
        'given_name': fields.text('givenName'),
        'middle_names': fields.text('middleName'),  
        'dob': fields.datetime('DOB'),
        'gender': fields.char('Gender', size=1),      
        'sex': fields.char('Sex', size=1),                
    }
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        vals_copy = vals.copy()
        res = {}
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)        
        except_if(not 'patient_identifier' in vals_copy.keys() and not 'other_identifier' in vals_copy.keys(),
              msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        patient_domain = [(k,'=',v) for k,v in vals_copy.iteritems()]
        patient_id = patient_pool.search(cr, uid, patient_domain)
        except_if(patient_id, msg="Patient already exists! Data: %s" % vals_copy)
        patient_id = patient_pool.create(cr, uid, vals_copy, context)

        vals_copy.update({'patient_id': patient_id, 'pos_id': user.pos_id.id})
        super(t4_clinical_adt_patient_register, self).submit(cr, uid, activity_id, vals_copy, context)
        res.update({'patient_id': patient_id})
        return res
    
    def complete(self, cr, uid, activity_id, context=None): 
        res = {}
        super(t4_clinical_adt_patient_register, self).complete(cr, uid, activity_id, context)
        return res       


class t4_clinical_adt_patient_admit(orm.Model):
    """
        adt.patient.admit: 
            - validate patient(patient_id), suggested_location(location_id or false)
            - on validation fail raise exception
            - start admission with patient_id and suggested_location
            
       consultanting and referring doctors are expected in the submitted values on key='doctors' in format:
       [...
       {
       'type': 'c' or 'r',
       'code': code string,
       'title':, 'given_name':, 'family_name':, }
       ...]
       
       if doctor doesn't exist, we create partner, but don't create user
        
             
    """
    
    _name = 't4.clinical.adt.patient.admit'
    _inherit = ['t4.activity.data']      
        
    _columns = {
        'suggested_location_id': fields.many2one('t4.clinical.location', 'Suggested Location', help="Location suggested by ADT for placement. Usually ward."),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS', required=True),
        'location': fields.text('Location'),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"), 
        'other_identifier': fields.text("Other Identifier"),
        'doctors': fields.text("Doctors"),
        'ref_doctor_ids': fields.many2many('res.partner', 'ref_doctor_admit_rel', 'admit_id', 'doctor_id', "Referring Doctors"),
        'con_doctor_ids': fields.many2many('res.partner', 'con_doctor_admit_rel', 'admit_id', 'doctor_id', "Consulting Doctors"),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        res = {}
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        # location validation
        location_pool = self.pool['t4.clinical.location']
        suggested_location_id = location_pool.search(cr, SUPERUSER_ID, 
                                                    [('code','=',vals['location']),
                                                     ('id','child_of',user.pos_id.location_id.id)])
        if not suggested_location_id:
            _logger.warn("ADT suggested_location not found! Will pass suggested_location_id = False")
            suggested_location_id = False
        else:
            suggested_location_id = suggested_location_id[0]
        # patient validation
        patient_pool = self.pool['t4.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier','=',vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s" 
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]
        vals_copy = vals.copy()       
        vals_copy.update({'suggested_location_id': suggested_location_id})  
        vals_copy.update({'patient_id': patient_id, 'pos_id': user.pos_id.id})
        # doctors
        if vals.get('doctors'):
            try:
                doctors = eval(str(vals['doctors']))
                ref_doctor_ids = []
                con_doctor_ids = []
                partner_pool = self.pool['res.partner'] 
                for d in doctors:
                    doctor_id = partner_pool.search(cr, uid, [['code','=',d['code']]])
                    if not doctor_id:
                        if d['title']:
                            d['title'] = d['title'].strip()
                            title_pool = self.pool['res.partner.title']
                            title_id = title_pool.search(cr, uid, [['name','=',d['title']]])
                            title_id = title_id and title_id[0] or title_pool.create(cr, uid, {'name': d['title']})
                        data = {
                                'name': "%s, %s" % (d['family_name'], d['given_name']),
                                'title': title_id,
                                'code': d['code'],
                                'doctor': True
                                }
                        doctor_id = partner_pool.create(cr, uid, data)
                    else:
                        doctor_id > 1 and _logger.warn("More than one doctor found with code '%s' passed id=%s" 
                                                       % (d['code'], doctor_id[0]))
                        doctor_id = doctor_id[0]
                    d['type'] == 'r' and ref_doctor_ids.append(doctor_id) or con_doctor_ids.append(doctor_id)
                ref_doctor_ids and vals_copy.update({'ref_doctor_ids': [6, 0, [id for id in ref_doctor_ids]]})
                con_doctor_ids and vals_copy.update({'con_doctor_ids': [6, 0, [id for id in con_doctor_ids]]})
            except:
               _logger.warn("Can't evaluate 'doctors': %s" % (vals['doctors']))       
        super(t4_clinical_adt_patient_admit, self).submit(cr, uid, activity_id, vals_copy, context)
        return res 

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(t4_clinical_adt_patient_admit, self).complete(cr, uid, activity_id, context)
        activity_pool = self.pool['t4.activity']
        admit_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context)
        admission_pool = self.pool['t4.clinical.patient.admission']
        #import pdb; pdb.set_trace()
        admission_activity_id = admission_pool.create_activity(cr, SUPERUSER_ID, 
                                       {'creator_id': activity_id}, 
                                       # FIXME! pos_id should be taken from adt_user.pos_id
                                       {'pos_id': admit_activity.data_ref.suggested_location_id.pos_id.id,
                                        'patient_id': admit_activity.patient_id.id,
                                        'suggested_location_id':admit_activity.data_ref.suggested_location_id.id})
        res[admission_pool._name] = admission_activity_id
            
        admission_result = activity_pool.complete(cr, SUPERUSER_ID, admission_activity_id, context)
        res.update(admission_result)
        activity_pool.write(cr, SUPERUSER_ID, activity_id, {'parent_id': admission_result['t4.clinical.spell']})
        return res
    
    
class t4_clinical_adt_patient_discharge(orm.Model):
    _name = 't4.clinical.adt.patient.discharge'
    _inherit = ['t4.activity.data']      
    _columns = {
    }


class t4_clinical_adt_patient_transfer(orm.Model):
    _name = 't4.clinical.adt.patient.transfer'
    _inherit = ['t4.activity.data']      
    _columns = {
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),                
        'location': fields.text('Location'),                
    }
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        except_if(not ('other_identifier' in vals or 'patient_identifier' in vals), msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        #patient_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        other_identifier = vals.get('other_identifier')
        patient_identifier = vals.get('patient_identifier')
        domain = []
        other_identifier and domain.append(('other_identifier','=',other_identifier))
        patient_identifier and domain.append(('patient_identifier','=',patient_identifier))
        domain = domain and ['|']*(len(domain)-1) + domain
        print "transfer domain: ", domain
        patient_id = patient_pool.search(cr, uid, domain)
        except_if(not patient_id, msg="Patient not found!")
        #activity = activity_pool.browse(cr, uid, activity_id, context)
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id, context=context)
        except_if(not spell_activity_id, msg="Active spell not found for patient.id=%s !" % patient_id)
        patient_id = patient_id[0]           
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.search(cr, uid, [('code','=',vals['location'])])
        except_if(not location_id, msg="Location not found!")
        location_id = location_id[0]
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_pool.create_activity(cr, uid, {'parent_id': spell_activity_id, 'creator_id': activity_id}, {'patient_id': patient_id}, context)
        super(t4_clinical_adt_patient_transfer, self).submit(cr, uid, activity_id, vals, context)    
        

class t4_clinical_adt_patient_merge(orm.Model):
    _name = 't4.clinical.adt.patient.merge'
    _inherit = ['t4.activity.data']      
    _columns = {
        'from_identifier': fields.text('From patient Identifier'),
        'into_identifier': fields.text('Into Patient Identifier'),        
    }
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        except_if(not ('from_identifier' in vals and 'into_identifier' in vals), msg="from_identifier or into_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        from_id = self.search(cr, uid, [('other_identifier', '=', vals['from_identifier'])])
        into_id = self.search(cr, uid, [('other_identifier', '=', vals['into_identifier'])])
        except_if(not(from_id and into_id), msg="Source or destination patient not found!")    
        # compare and combine data. may need new cursor to have the update in one transaction
        for model_pool in self.pool._models.values():
            if model_pool._name.startswith("t4.clinical") and 'patient_id' in model_pool.columns.keys() and model_pool._name != self._name:
                ids = model_pool.search(cr, uid, [('patient_id','=',from_id)])
                ids and model_pool.write(cr, uid, ids, {'patient_id': into_id})
        from_data = patient_pool.read(cr, uid, from_id, context)        
        into_data = patient_pool.read(cr, uid, into_id, context)
        vals_into = {}
        for fk, fv in from_data.iteritems():
            for ik, iv in into_data.iteritems():
                if not fv:
                    continue
                if fv and iv and fv != iv:
                    pass # which to choose ?
                if fv and not iv:
                    vals_into.update({ik: fv})
        patient_pool.write(cr, uid, into_id, vals_into, context)
        patient_pool.write(cr, uid, from_id, {'active': False}, context)
        super(t4_clinical_adt_patient_merge, self).submit(cr, uid, activity_id, vals, context)
        

class t4_clinical_adt_patient_update(orm.Model):
    _name = 't4.clinical.adt.patient.update'
    _inherit = ['t4.activity.data']      
    _columns = {
    }