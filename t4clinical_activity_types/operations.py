# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.activity import except_if
import logging
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
_logger = logging.getLogger(__name__)


class t4_clinical_device_action(orm.AbstractModel):
    _name = 't4.clinical.device.action'
    _inherit = ['t4.clinical.activity.data']
    _columns = {
        'device_id': fields.many2one('t4.clinical.device', 'Device', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
    }
    
class t4_clinical_device_connect(orm.Model):
    _name = 't4.clinical.device.connect'
    _inherit = ['t4.clinical.device.action']


class t4_clinical_device_disconnect(orm.Model):
    _name = 't4.clinical.device.disconnect'
    _inherit = ['t4.clinical.device.action']


class t4_clinical_notification(orm.AbstractModel):
    _name = 't4.clinical.notification'
    _inherit = ['t4.clinical.activity.data']
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
    }


class t4_clinical_notification_hca(orm.Model):
    _name = 't4.clinical.notification.hca'
    _inherit = ['t4.clinical.notification']

class t4_clinical_notification_nurse(orm.Model):
    _name = 't4.clinical.notification.nurse'
    _inherit = ['t4.clinical.notification']


class t4_clinical_patient_move(orm.Model):
    _name = 't4.clinical.patient.move'
    _inherit = ['t4.clinical.activity.data']      
    _columns = {
        'location_id': fields.many2one('t4.clinical.location', 'Destination Location', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
        
    }

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        # move from current or permanent location ??
        location_id = self.pool['t4.clinical.patient'].get_patient_current_location_id(cr, uid, patient_id, context)
        return location_id           


class t4_clinical_patient_placement(orm.Model):
    _name = 't4.clinical.patient.placement'
    _inherit = ['t4.clinical.activity.data'] 
    _transitions = {
        'draft': ['schedule', 'plan','start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'planned': ['schedule','start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'scheduled': ['start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'started': ['complete','cancel','submit','assign','unassign','retrieve','validate'],
        'completed': ['retrieve','validate'],
        'cancelled': ['retrieve','validate']
                    }       
    _columns = {
        'suggested_location_id': fields.many2one('t4.clinical.location', 'Suggested Location'),
        'location_id': fields.many2one('t4.clinical.location', 'Destination Location'),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
        
    }

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        # place from current or permanent location ??
        location_id = self.pool['t4.clinical.patient'].get_patient_current_location_id(cr, uid, patient_id, context)
        return location_id  
    
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        api_pool = self.pool['t4.clinical.api']
        ews_pool = self.pool['t4.clinical.patient.observation.ews']
        placement_activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not placement_activity.location_id, 
                  msg="Location is not set for the placement thus the placement can't be completed! Check location availability.") 
        super(t4_clinical_patient_placement, self).complete(cr, uid, activity_id, context)
        placement_activity = activity_pool.browse(cr, uid, activity_id, context)
        # set spell location
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, placement_activity.data_ref.patient_id.id, context)
        activity_pool.submit(cr, uid, spell_activity_id, {'location_id': placement_activity.data_ref.location_id.id})
        # create EWS
        frequency = placement_activity.data_ref.location_id.pos_id.ews_init_frequency
        ews_activity_id = ews_pool.create_activity(cr, self.t4suid, 
                                                   {'location_id': placement_activity.data_ref.location_id.id,
                                                    'parent_id': spell_activity_id}, 
                                                   {'patient_id': placement_activity.data_ref.patient_id.id}, context)
        activity_pool.schedule(cr, uid, ews_activity_id, date_scheduled=(dt.now()+td(minutes=frequency)).strftime(DTF))
        # create trigger
        api_pool.set_activity_trigger(cr, uid, placement_activity.data_ref.patient_id.id,
                                           't4.clinical.patient.observation.ews', 'minute',
                                           frequency, context)
        return True

     
    def submit(self, cr, uid, activity_id, vals, context=None):
        if vals.get('location_id'):
            location_pool = self.pool['t4.clinical.location']
            available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'], context=context)
            except_if(vals['location_id'] not in available_bed_location_ids, msg="Location id=%s is not available" % vals['location_id'])
        super(t4_clinical_patient_placement, self).submit(cr, uid, activity_id, vals, context)
        return True
        
        
class t4_clinical_patient_discharge(orm.Model):
    _name = 't4.clinical.patient.discharge'    
    _inherit = ['t4.clinical.activity.data']
        
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'location_id': fields.related('activity_id','location_id', type='many2one', relation='t4.clinical.location', string='Location')
    }
    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        # discharge from current or permanent location ??
        location_id = self.pool['t4.clinical.patient'].get_patient_current_location_id(cr, uid, patient_id, context)
        return location_id      

    def complete(self, cr, uid, activity_id, context=None):
        super(t4_clinical_patient_discharge, self).complete(cr, uid, activity_id, context)
        api_pool = self.pool['t4.clinical.api']
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        
        # move
        move_pool = self.pool['t4.clinical.patient.move']
        move_activity_id = move_pool.create_activity(cr, uid, 
            {'parent_id': activity_id}, 
            {'patient_id': activity.data_ref.patient_id.id, 
             'location_id':activity.pos_id.lot_discharge_id.id or activity.pos_id.location_id.id}, 
            context)
        activity_pool.complete(cr, uid, move_activity_id, context)      
        # complete spell 
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, activity.data_ref.patient_id.id, context)
        activity_pool.complete(cr, uid, spell_activity.id, context)
        return True  
        
        
class t4_clinical_patient_admission(orm.Model):
    _name = 't4.clinical.patient.admission'    
    _inherit = ['t4.clinical.activity.data']
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True), 
        'pos_id': fields.many2one('t4.clinical.pos', 'POS', required=True),
        'suggested_location_id': fields.many2one('t4.clinical.location', 'Suggested Location'),
        'location_id': fields.related('activity_id','location_id', type='many2one', relation='t4.clinical.location', string='Location')
    }
    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        #import pdb; pdb.set_trace()
        location_id = activity.data_ref.pos_id.lot_admission_id.id or activity.data_ref.pos_id.location_id.id
        return location_id 
    
    def complete(self, cr, uid, activity_id, context=None):
        super(t4_clinical_patient_admission, self).complete(cr, uid, activity_id, context)
        #import pdb; pdb.set_trace()
        api_pool = self.pool['t4.clinical.api']
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        admission = activity.data_ref
        
        # spell
        spell_activity_data = context and context.get('parent_activity_id') and {'parent_id': context['parent_activity_id']} or {}
        spell_pool = self.pool['t4.clinical.spell']
        spell_activity_id = spell_pool.create_activity(cr, uid, 
           spell_activity_data,
           {'patient_id': admission.patient_id.id, 'location_id': admission.location_id.id},
           context=None)
        #import pdb; pdb.set_trace()
        activity_pool.start(cr, uid, spell_activity_id, context)
        activity_pool.write(cr, uid, admission.activity_id.id, {'parent_id': spell_activity_id}, context)
        # patient move to lot_admission !!If lot_admission isn't set access rights to see the activity will need to be set to pos.location i.e. all locations in the pos
        move_pool = self.pool['t4.clinical.patient.move']
        move_activity_id = move_pool.create_activity(cr, uid, 
            {'parent_id': admission.activity_id.id}, 
            {'patient_id': admission.patient_id.id, 
             'location_id': activity.pos_id.lot_admission_id.id or activity.pos_id.location_id.id}, 
            context)
        activity_pool.complete(cr, uid, move_activity_id, context)
        # patient placement
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_activity_id = placement_pool.create_activity(cr, uid, 
           {'parent_id': admission.activity_id.id}, 
           {'patient_id': admission.patient_id.id,
            'suggested_location_id': admission.suggested_location_id.id},
           context)
        # set EWS trigger
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        api_pool.set_activity_trigger(cr, uid, admission.patient_id.id,
                                           't4.clinical.patient.observation.ews',
                                           'minute', user.pos_id.ews_init_frequency, context=None)         
        res = {'admission_activity_id': activity_id,
               'spell_activity_id': spell_activity_id,
               'move_activity_id': move_activity_id,
               'placement_activity_id': placement_activity_id}
        return res
    
    
class t4_clinical_patient(orm.Model):
    _inherit = 't4.clinical.patient'

   
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
    
class t4_clinical_location(orm.Model):
    _inherit = 't4.clinical.location'
    
    def get_location_patient_ids(self, cr, uid, location_id, context=None):
        # current spells
        activity_pool = self.pool['t4.clinical.activity']
        spell_Activities = self.browse_domain(cr, uid, [('data_model','=','t4.clinical.spell'),('state','=','started')])
        spell_pool = self.pool['t4.clinical.spell']
        spells = spell_pool.browse_domain(cr, uid, [('state','in',['started'])], context)        
        patients = [spell.patient_id for spell in spells]
        patient_pool = self.pool['t4.clinical.patient']
        patient_location_map = {patient.id: patient_pool.get_patient_location_id(cr, uid, patient.id, context) for patient in patients}
        patients_by_location = {}.fromkeys(patient_location_map.values(),[])
        for pat_id, loc_id in patient_location_map.iteritems():
            patients_by_location[loc_id].append(pat_id)
        return patients_by_location.get(location_id,[])
        
    
    
    
    
    
        