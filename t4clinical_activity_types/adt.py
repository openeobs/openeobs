# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
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
            
       consulting and referring doctors are expected in the submitted values on key='doctors' in format:
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
            _logger.warn("ADT suggested_location '%s' not found! Will pass suggested_location_id = False" % vals['location'])
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
                    d['type'] == 'r' and ref_doctor_ids.append(doctor_id)
                    d['type'] == 'c' and con_doctor_ids.append(doctor_id)
                ref_doctor_ids and vals_copy.update({'ref_doctor_ids': [[4, id] for id in ref_doctor_ids]})
                con_doctor_ids and vals_copy.update({'con_doctor_ids': [[4, id] for id in con_doctor_ids]})
            except:
                _logger.warn("Can't evaluate 'doctors': %s" % (vals['doctors']))   
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id)
          
        super(t4_clinical_adt_patient_admit, self).submit(cr, uid, activity_id, vals_copy, context)
        self.write(cr, uid, activity.data_ref.id, vals_copy) 
        return res 

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(t4_clinical_adt_patient_admit, self).complete(cr, uid, activity_id, context)
        activity_pool = self.pool['t4.activity']
        admit_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context)
        admission_pool = self.pool['t4.clinical.patient.admission']
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
    
class t4_clinical_adt_patient_cancel_admit(orm.Model):
    _name = 't4.clinical.adt.patient.cancel_admit'
    _inherit = ['t4.activity.data']      
    _columns = {
        'other_identifier': fields.text('otherId', required=True),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        patient_pool = self.pool['t4.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier','=',vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s" 
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]        
        vals_copy = vals.copy()
        vals_copy.update({'pos_id': user.pos_id.id, 'patient_id':patient_id})
        res = super(t4_clinical_adt_patient_cancel_admit, self).submit(cr, uid, activity_id, vals_copy, context)
        return res

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.activity']
        admit_cancel_activity = activity_pool.browse(cr, uid, activity_id)
        # get admit activity
        api_pool = self.pool['t4.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, SUPERUSER_ID, admit_cancel_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity, msg="Patient id=%s has no started spell!" % admit_cancel_activity.data_ref.patient_id.id)
        # admit-admission-spell
        admit_activity_id = spell_activity.creator_id \
                            and spell_activity.creator_id.creator_id\
                            and spell_activity.creator_id.creator_id.id \
                            or False
        except_if(not admit_activity_id, msg="adt.admit activity is not found!")
        admit_activity = activity_pool.browse(cr, uid, admit_activity_id)
        # get all children and created activity_ids
        activity_ids = []
        next_level_activity_ids = []

        next_level_activity_ids.extend([child.id for child in admit_activity.child_ids])
        next_level_activity_ids.extend([created.id for created in admit_activity.created_ids])
        activity_ids.extend(next_level_activity_ids)
        #import pdb; pdb.set_trace()
        while next_level_activity_ids:
            for activity in activity_pool.browse(cr, uid, next_level_activity_ids):
                next_level_activity_ids = [child.id for child in activity.child_ids]
                next_level_activity_ids.extend([created.id for created in activity.created_ids])            
                activity_ids.extend(next_level_activity_ids)
        activity_ids = list(set(activity_ids)) 
        _logger.info("Starting activities cancellation due to adt.pateint.cancel_admit activity completion...")       
        for activity in activity_pool.browse(cr, uid, activity_ids):
            activity_pool.cancel(cr, uid, activity.id)
        res = super(t4_clinical_adt_patient_cancel_admit, self).complete(cr, uid, activity_id, context)
        return res


class t4_clinical_adt_patient_discharge(orm.Model):
    _name = 't4.clinical.adt.patient.discharge'
    _inherit = ['t4.activity.data']      
    _columns = {
        'other_identifier': fields.text('otherId', required=True),
        'discharge_date': fields.datetime('Discharge Date')
    }

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        patient_pool = self.pool['t4.clinical.patient']
        discharge_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier', '=', discharge_activity.data_ref.other_identifier)], context=context)
        except_if(not patient_id, msg="Patient not found!")
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, SUPERUSER_ID, patient_id[0], context=context)
        except_if(not spell_activity.id, msg="Patient was not admitted!")
        super(t4_clinical_adt_patient_discharge, self).complete(cr, uid, activity_id, context)
        discharge_pool = self.pool['t4.clinical.patient.discharge']
        discharge_activity_id = discharge_pool.create_activity(
            cr, SUPERUSER_ID,
            {'creator_id': activity_id},
            {'patient_id': patient_id}, context=context)
        res[discharge_pool._name] = discharge_activity_id
        discharge_result = activity_pool.complete(cr, SUPERUSER_ID, discharge_activity_id, context=context)
        res.update(discharge_result)
        return res

class t4_clinical_adt_patient_transfer(orm.Model):
    _name = 't4.clinical.adt.patient.transfer'
    _inherit = ['t4.activity.data']      
    _columns = {
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),                
        'location': fields.text('Location'),
        'from_location_id': fields.many2one('t4.clinical.location', 'Origin Location'),
        'location_id': fields.many2one('t4.clinical.location', 'Transfer Location'),
    }
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        except_if(not ('other_identifier' in vals or 'patient_identifier' in vals), msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        activity_pool = self.pool['t4.activity']
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
        spell_activity = activity_pool.browse(cr, uid, spell_activity_id, context=context)
        patient_id = patient_id[0]           
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.search(cr, uid, [('code', '=', vals['location'])], context=context)
        except_if(not location_id, msg="Location not found!")
        location_id = location_id[0]
        vals.update({'location_id': location_id, 'from_location_id': spell_activity.location_id.id})
        super(t4_clinical_adt_patient_transfer, self).submit(cr, uid, activity_id, vals, context)

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(t4_clinical_adt_patient_transfer, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        move_pool = self.pool['t4.clinical.patient.move']
        transfer_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        # patient move
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, transfer_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id, msg="Spell not found!")
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,{
            'parent_id': spell_activity_id,
            'creator_id': activity_id
        }, {
            'patient_id': transfer_activity.data_ref.patient_id.id,
            'location_id': transfer_activity.data_ref.location_id.pos_id.lot_admission_id.id},
            context=context)
        res[move_pool._name] = move_activity_id
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
        # patient placement
        api_pool.cancel_open_activities(cr, uid, spell_activity_id, 't4.clinical.patient.placement', context=context)
        placement_pool = self.pool['t4.clinical.patient.placement']

        placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, {
            'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
            'creator_id': activity_id
        }, {
            'patient_id': transfer_activity.data_ref.patient_id.id,
            'suggested_location_id': transfer_activity.data_ref.location_id.id
        }, context=context)
        res[placement_pool._name] = placement_activity_id
        return res
        

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
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
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
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        except_if(not 'patient_identifier' in vals_copy.keys() and not 'other_identifier' in vals_copy.keys(),
              msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        hospital_number = vals_copy.get('other_identifier')
        nhs_number = vals_copy.get('patient_identifier')
        if hospital_number:
            patient_domain = [('other_identifier', '=', hospital_number)]
            del vals_copy['other_identifier']
        else:
            patient_domain = [('patient_identifier', '=', nhs_number)]
            del vals_copy['patient_identifier']
        patient_id = patient_pool.search(cr, uid, patient_domain, context=context)
        except_if(not patient_id, msg="Patient doesn't exist! Data: %s" % patient_domain)
        res = patient_pool.write(cr, uid, patient_id, vals_copy, context=context)
        vals_copy.update({'patient_id': patient_id, 'other_identifier': hospital_number, 'patient_identifier': nhs_number})
        super(t4_clinical_adt_patient_update, self).submit(cr, uid, activity_id, vals_copy, context)
        return res


class t4_clinical_adt_spell_update(orm.Model):

    _name = 't4.clinical.adt.spell.update'
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
            _logger.warn("ADT suggested_location '%s' not found! Will pass suggested_location_id = False" % vals['location'])
            suggested_location_id = False
        else:
            suggested_location_id = suggested_location_id[0]
        # patient validation
        patient_pool = self.pool['t4.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier', '=', vals['other_identifier'])])
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
                    doctor_id = partner_pool.search(cr, uid, [['code', '=', d['code']]])
                    if not doctor_id:
                        if d['title']:
                            d['title'] = d['title'].strip()
                            title_pool = self.pool['res.partner.title']
                            title_id = title_pool.search(cr, uid, [['name', '=', d['title']]])
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
                    d['type'] == 'r' and ref_doctor_ids.append(doctor_id)
                    d['type'] == 'c' and con_doctor_ids.append(doctor_id)
                ref_doctor_ids and vals_copy.update({'ref_doctor_ids': [[4, id] for id in ref_doctor_ids]})
                con_doctor_ids and vals_copy.update({'con_doctor_ids': [[4, id] for id in con_doctor_ids]})
            except:
                _logger.warn("Can't evaluate 'doctors': %s" % (vals['doctors']))
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id)

        super(t4_clinical_adt_spell_update, self).submit(cr, uid, activity_id, vals_copy, context)
        self.write(cr, uid, activity.data_ref.id, vals_copy)
        return res

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(t4_clinical_adt_spell_update, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        update_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, update_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id, msg="Spell not found!")
        spell_activity = activity_pool.browse(cr, SUPERUSER_ID, spell_activity_id, context=context)
        data = {
            'con_doctor_ids': [[6, 0,  [d.id for d in update_activity.data_ref.data_ref.con_doctor_ids]]],
            'ref_doctor_ids': [[6, 0, [d.id for d in update_activity.data_ref.data_ref.ref_doctor_ids]]],
            'location_id': update_activity.data_ref.pos_id.lot_admission_id.id,
            'code': update_activity.data_ref.code,
            'start_date': update_activity.data_ref.start_date if update_activity.data_ref.start_date < spell_activity.data_ref.start_date else spell_activity.data_ref.start_date
        }
        res = activity_pool.submit(cr, uid, spell_activity_id, {}, data, context=context)
        activity_pool.write(cr, SUPERUSER_ID, activity_id, {'parent_id': spell_activity_id})
        # patient move
        move_pool = self.pool['t4.clinical.patient.move']
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
            {'parent_id': spell_activity_id, 'creator_id': activity_id},
            {'patient_id': update_activity.data_ref.patient_id.id,
             'location_id': update_activity.data_ref.pos_id.lot_admission_id.id},
            context=context)
        res[move_pool._name] = move_activity_id
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
        # patient placement
        api_pool.cancel_open_activities(cr, uid, spell_activity_id, 't4.clinical.patient.placement', context=context)
        placement_pool = self.pool['t4.clinical.patient.placement']

        placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, {
            'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
            'creator_id': activity_id
        }, {
            'patient_id': update_activity.data_ref.patient_id.id,
            'suggested_location_id': update_activity.data_ref.suggested_location_id.id
        }, context=context)
        res[placement_pool._name] = placement_activity_id
        return res


class t4_clinical_adt_patient_cancel_discharge(orm.Model):
    _name = 't4.clinical.adt.patient.cancel_discharge'
    _inherit = ['t4.activity.data']
    _columns = {
        'other_identifier': fields.text('otherId', required=True),
        'pos_id': fields.many2one('t4.clinical.pos', 'POS', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        patient_pool = self.pool['t4.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier', '=', vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s"
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]
        vals_copy = vals.copy()
        vals_copy.update({'pos_id': user.pos_id.id, 'patient_id': patient_id})
        res = super(t4_clinical_adt_patient_cancel_discharge, self).submit(cr, uid, activity_id, vals_copy, context)
        return res

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(t4_clinical_adt_patient_cancel_discharge, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        move_pool = self.pool['t4.clinical.patient.move']
        cancel_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, cancel_activity.data_ref.patient_id.id, context=context)
        except_if(spell_activity_id, msg="Patient was not discharged or was admitted again!")
        spell_activity_id = api_pool.get_patient_last_spell_activity_id(cr, SUPERUSER_ID, cancel_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id, msg="Patient was not discharged!")
        domain = [('data_model', '=', 't4.clinical.adt.patient.discharge'),
                  ('state', '=', 'completed'),
                  ('patient_id', '=', cancel_activity.data_ref.patient_id.id)]
        last_discharge_activity_id = activity_pool.search(cr, uid, domain, order='date_terminated desc', context=context)
        except_if(not last_discharge_activity_id, msg='Patient was not discharged!')
        domain = [('data_model', '=', 't4.clinical.patient.move'),
                  ('state', '=', 'completed'),
                  ('patient_id', '=', cancel_activity.data_ref.patient_id.id)]
        move_activity_ids = activity_pool.search(cr, uid, domain, order='date_terminated desc', context=context)
        move_activity = activity_pool.browse(cr, uid, move_activity_ids[1], context=context)
        res[self._name] = activity_pool.write(cr, uid, spell_activity_id, {'state': 'started'}, context=context)
        if move_activity.location_id.usage == 'bed':
            if move_activity.location_id.is_available:
                move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
                    {'parent_id': spell_activity_id, 'creator_id': activity_id},
                    {'patient_id': cancel_activity.data_ref.patient_id.id,
                     'location_id': move_activity.location_id.id},
                    context=context)
                res[move_pool._name] = move_activity_id
                activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
            else:
                move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
                    {'parent_id': spell_activity_id, 'creator_id': activity_id},
                    {'patient_id': cancel_activity.data_ref.patient_id.id,
                     'location_id': move_activity.location_id.pos_id.lot_admission_id.id},
                    context=context)
                res[move_pool._name] = move_activity_id
                activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
                # patient placement
                api_pool.cancel_open_activities(cr, uid, spell_activity_id, 't4.clinical.patient.placement', context=context)
                placement_pool = self.pool['t4.clinical.patient.placement']

                placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
                    'creator_id': activity_id
                }, {
                    'patient_id': cancel_activity.data_ref.patient_id.id,
                    'suggested_location_id': move_activity.location_id.parent_id.id
                }, context=context)
                res[placement_pool._name] = placement_activity_id
        return res


class t4_clinical_adt_patient_cancel_transfer(orm.Model):
    _name = 't4.clinical.adt.patient.cancel_transfer'
    _inherit = ['t4.activity.data']
    _columns = {
        'other_identifier': fields.text('otherId', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        patient_pool = self.pool['t4.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier', '=', vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s"
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]
        vals_copy = vals.copy()
        vals_copy.update({'patient_id': patient_id})
        res = super(t4_clinical_adt_patient_cancel_transfer, self).submit(cr, uid, activity_id, vals_copy, context)
        return res

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(t4_clinical_adt_patient_cancel_transfer, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['t4.activity']
        api_pool = self.pool['t4.clinical.api']
        move_pool = self.pool['t4.clinical.patient.move']
        cancel_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        domain = [('data_model', '=', 't4.clinical.adt.patient.transfer'),
                  ('state', '=', 'completed'),
                  ('patient_id', '=', cancel_activity.data_ref.patient_id.id)]
        transfer_activity_ids = activity_pool.search(cr, uid, domain, order='date_terminated desc', context=context)
        except_if(not transfer_activity_ids, msg='Patient was not transfered!')
        transfer_activity = activity_pool.browse(cr, uid, transfer_activity_ids[0], context=context)

        # patient move
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, cancel_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id, msg="Spell not found!")
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,{
            'parent_id': spell_activity_id,
            'creator_id': activity_id
        }, {
            'patient_id': cancel_activity.data_ref.patient_id.id,
            'location_id': transfer_activity.data_ref.from_location_id.pos_id.lot_admission_id.id},
            context=context)
        res[move_pool._name] = move_activity_id
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
        # patient placement
        api_pool.cancel_open_activities(cr, uid, spell_activity_id, 't4.clinical.patient.placement', context=context)
        placement_pool = self.pool['t4.clinical.patient.placement']

        placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, {
            'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
            'creator_id': activity_id
        }, {
            'patient_id': cancel_activity.data_ref.patient_id.id,
            'suggested_location_id': transfer_activity.data_ref.from_location_id.id
        }, context=context)
        res[placement_pool._name] = placement_activity_id
        return res