# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.activity import except_if
import logging
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)

class t4_clinical_device_session(orm.AbstractModel):
    _name = 't4.clinical.device.session'
    _description = 'Device Session'
    _inherit = ['t4.clinical.activity.data']
    _columns = {
        'device_id': fields.many2one('t4.clinical.device', 'Device', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }
    
class t4_clinical_device_connect(orm.Model):
    _name = 't4.clinical.device.connect'
    _inherit = ['t4.clinical.activity.data']
    _description = 'Connect Device'
    _columns = {
        'device_id': fields.many2one('t4.clinical.device', 'Device', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }

class t4_clinical_device_disconnect(orm.Model):
    _name = 't4.clinical.device.disconnect'
    _inherit = ['t4.clinical.activity.data']
    _description = 'Disconnect Device'
    _columns = {
        'device_id': fields.many2one('t4.clinical.device', 'Device', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
    }


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
    #_rec_name = 'patient_id'    
    _description = "Patient Move"
    _start_view_xmlid = "view_patient_move_form"
    _schedule_view_xmlid = "view_patient_move_form"
    _submit_view_xmlid = "view_patient_move_form"
    _complete_view_xmlid = "view_patient_move_form"
    _cancel_view_xmlid = "view_patient_move_form"
    _columns = {
        'location_id': fields.many2one('t4.clinical.location', 'Destination Location', required=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
        
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        #import pdb; pdb.set_trace()
        for move in self.browse(cr, uid, ids, context):
            res.append( [move.id, "%s to %s" % ("patient", "location")] )
        return res   
    
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        patient_pool = self.pool['t4.clinical.patient']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_pool.write(cr, uid, activity.data_ref.patient_id.id, {'current_location_id': activity.data_ref.location_id.id}, context)
        super(t4_clinical_patient_move, self).complete(cr, uid, activity_id, context)
        return {}         
    

class t4_clinical_patient_placement(orm.Model):
    _name = 't4.clinical.patient.placement'
    _inherit = ['t4.clinical.activity.data'] 
    _transitions = {
        'new': ['schedule', 'plan','start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'planned': ['schedule','start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'scheduled': ['start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'started': ['complete','cancel','submit','assign','unassign','retrieve','validate'],
        'completed': ['retrieve','validate'],
        'cancelled': ['retrieve','validate']
                    }       
    _description = "Patient Placement"
    _start_view_xmlid = "view_patient_placement_form"
    _schedule_view_xmlid = "view_patient_placement_form"
    _submit_view_xmlid = "view_patient_placement_form"
    _complete_view_xmlid = "view_patient_placement_form"
    _cancel_view_xmlid = "view_patient_placement_form"
    
    _columns = {
        'suggested_location_id': fields.many2one('t4.clinical.location', 'Suggested Location', required=True),
        'location_id': fields.many2one('t4.clinical.location', 'Destination Location'),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
        
    }

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        return activity.data_ref.suggested_location_id.id
    
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        api_pool = self.pool['t4.clinical.api']
        move_pool = self.pool['t4.clinical.patient.move']
        ews_pool = self.pool['t4.clinical.patient.observation.ews']
        gcs_pool = self.pool['t4.clinical.patient.observation.gcs']
        placement_activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not placement_activity.data_ref.location_id, 
                  msg="Location is not set for the placement thus the placement can't be completed!") 
        super(t4_clinical_patient_placement, self).complete(cr, uid, activity_id, context)
        
        placement_activity = activity_pool.browse(cr, uid, activity_id, context)
        # set spell location
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, placement_activity.data_ref.patient_id.id, context=context)
        # move to location
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
                                                    {'parent_id': spell_activity_id,
                                                     'creator_id': activity_id},
                                                    {'patient_id': placement_activity.data_ref.patient_id.id,
                                                     'location_id': placement_activity.data_ref.location_id.id})
        activity_pool.complete(cr, uid, move_activity_id)
        #import pdb; pdb.set_trace()
        activity_pool.submit(cr, SUPERUSER_ID, spell_activity_id, {'location_id': placement_activity.data_ref.location_id.id})
        # create EWS
        frequency = placement_activity.pos_id.ews_init_frequency
        ews_activity_id = ews_pool.create_activity(cr, SUPERUSER_ID, 
                                                   {#'location_id': placement_activity.data_ref.location_id.id,
                                                    'parent_id': spell_activity_id,
                                                    'creator_id': activity_id}, 
                                                   {'patient_id': placement_activity.data_ref.patient_id.id}, context)
        activity_pool.schedule(cr, uid, ews_activity_id, date_scheduled=(dt.now()+td(minutes=frequency)).strftime(DTF))
        # create GCS
        gcs_activity_id = gcs_pool.create_activity(cr, SUPERUSER_ID,
                                                   {#'location_id': placement_activity.data_ref.location_id.id,
                                                    'parent_id': spell_activity_id,
                                                    'creator_id': activity_id},
                                                   {'patient_id': placement_activity.data_ref.patient_id.id}, context)
        activity_pool.schedule(cr, uid, gcs_activity_id, date_scheduled=(dt.now()+td(minutes=frequency)).strftime(DTF))
        return {}

     
    def submit(self, cr, uid, activity_id, vals, context=None):
        if vals.get('location_id'):
            location_pool = self.pool['t4.clinical.location']
            available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'], context=context)
            except_if(vals['location_id'] not in available_bed_location_ids, msg="Location id=%s is not available" % vals['location_id'])
        super(t4_clinical_patient_placement, self).submit(cr, uid, activity_id, vals, context)
        return {}
        
        
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
        location_id = self.pool['t4.clinical.api'].get_patient_current_location_id(cr, uid, patient_id, context)
        return location_id      

    def complete(self, cr, uid, activity_id, context=None):
        super(t4_clinical_patient_discharge, self).complete(cr, uid, activity_id, context)
        api_pool = self.pool['t4.clinical.api']
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context)
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity, msg="Patient id=%s has no started spell!" % activity.patient_id.id)
        #import pdb; pdb.set_trace()
        # move
        move_pool = self.pool['t4.clinical.patient.move']
        move_activity_id = move_pool.create_activity(cr, uid, 
            {'parent_id': activity_id, 'creator_id': activity_id}, 
            {'patient_id': activity.data_ref.patient_id.id, 
             'location_id':activity.pos_id and activity.pos_id.lot_discharge_id.id or activity.pos_id.location_id.id}, 
            context)
        activity_pool.complete(cr, uid, move_activity_id, context)      
        # complete spell 

        activity_pool.complete(cr, uid, spell_activity.id, context)
        return {}  
        
        
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
        location_id = activity.data_ref.pos_id.lot_admission_id.id #or activity.data_ref.pos_id.location_id.id
        return location_id 
    
    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(t4_clinical_patient_admission, self).complete(cr, uid, activity_id, context)
        #import pdb; pdb.set_trace()
        api_pool = self.pool['t4.clinical.api']
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context)
        admission = activity.data_ref
        
        # spell
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, admission.patient_id.id, context=context)
        # FIXME! hadle multiple POS
        except_if(spell_activity_id, msg="Patient id=%s has started spell!" % admission.patient_id.id)
        spell_pool = self.pool['t4.clinical.spell']
        spell_activity_id = spell_pool.create_activity(cr, SUPERUSER_ID, 
           {'creator_id': activity_id},
           {'patient_id': admission.patient_id.id, 'location_id': admission.location_id.id, 'pos_id': admission.pos_id.id},
           context=None)
        res[spell_pool._name] = spell_activity_id
        activity_pool.start(cr, SUPERUSER_ID, spell_activity_id, context)
        activity_pool.write(cr, SUPERUSER_ID, admission.activity_id.id, {'parent_id': spell_activity_id}, context)
        # patient move to lot_admission !!If lot_admission isn't set access rights to see the activity will need to be set to pos.location i.e. all locations in the pos
        move_pool = self.pool['t4.clinical.patient.move']
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID, 
            {'parent_id': spell_activity_id, 'creator_id': activity_id}, 
            {'patient_id': admission.patient_id.id, 
             'location_id': activity.pos_id.lot_admission_id.id}, 
            context)
        res[move_pool._name] = move_activity_id
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
        # patient placement
        placement_pool = self.pool['t4.clinical.patient.placement']
        
        placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, 
           {'parent_id': spell_activity_id, 'creator_id': activity_id},
           {'patient_id': admission.patient_id.id,
            'suggested_location_id': admission.suggested_location_id.id},
           context)
        res[placement_pool._name] = placement_activity_id
       
        return res
    
        
    
    
    
    
    
        