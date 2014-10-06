# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.nh_activity.activity import except_if
from openerp.addons.nh_clinical_activity_types.parameters import frequencies
import logging
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)


class nh_clinical_notification(orm.AbstractModel):
    _name = 'nh.clinical.notification'
    _inherit = ['nh.activity.data']
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
    }
    _form_description = []

    def get_form_description(self, cr, uid, patient_id, context=None):
        return self._form_description

    def is_cancellable(self, cr, uid, context=None):
        return False
    
    
class nh_clinical_notification_hca(orm.Model):
    _name = 'nh.clinical.notification.hca'
    _inherit = ['nh.clinical.notification']

class nh_clinical_notification_nurse(orm.Model):
    _name = 'nh.clinical.notification.nurse'
    _inherit = ['nh.clinical.notification']


class nh_clinical_notification_frequency(orm.Model):
    _name = 'nh.clinical.notification.frequency'
    _inherit = ['nh.clinical.notification']
    _description = 'Review Frequency'
    _columns = {
        'observation': fields.text('Observation Model', required=True),
        'frequency': fields.selection(frequencies, 'Frequency')
    }
    _notifications = [{'model': 'medical_team', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        review_frequency = activity_pool.browse(cr, uid, activity_id, context=context)
        domain = [
            ('patient_id', '=', review_frequency.data_ref.patient_id.id),
            ('data_model', '=', review_frequency.data_ref.observation),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        obs_ids = activity_pool.search(cr, uid, domain, order='create_date desc, id desc', context=context)
        obs = activity_pool.browse(cr, uid, obs_ids[0], context=context)
        obs_pool = self.pool[review_frequency.data_ref.observation]
        obs_pool.write(cr, uid, obs.data_ref.id, {'frequency': review_frequency.data_ref.frequency}, context=context)
        trigger_notification = review_frequency.creator_id._name == 'nh.clinical.notification.assessment' and \
                               review_frequency.creator_id.creator_id._name == 'nh.clinical.patient.observation.ews' \
                               and review_frequency.creator_id.creator_id.clinical_risk == 'Low'
        if trigger_notification:
            api_pool = self.pool['nh.clinical.api']
            api_pool.trigger_notifications(cr, uid, {
                'notifications': self._notifications,
                'parent_id': review_frequency.parent_id.id,
                'creator_id': activity_id,
                'patient_id': review_frequency.data_ref.patient_id.id,
                'model': review_frequency.data_ref.observation,
                'group': 'nurse'
            }, context=context)
        return super(nh_clinical_notification_frequency, self).complete(cr, uid, activity_id, context=context)

    _form_description = [
        {
            'name': 'frequency',
            'type': 'selection',
            'selection': frequencies,
            'label': 'Observation frequency',
            'initially_hidden': False
        }
    ]


class nh_clinical_notification_assessment(orm.Model):
    _name = 'nh.clinical.notification.assessment'
    _inherit = ['nh.clinical.notification']
    _description = 'Assess Patient'
    _notifications = [{'model': 'frequency', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._notifications,
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id.data_ref._name,
            'group': 'nurse'
        }, context=context)
        return super(nh_clinical_notification_assessment, self).complete(cr, uid, activity_id, context=context)


class nh_clinical_notification_medical_team(orm.Model):
    _name = 'nh.clinical.notification.medical_team'
    _inherit = ['nh.clinical.notification']
    _description = 'Inform Medical Team?'
    _notifications = [{'model': 'doctor_assessment', 'groups': ['nurse']}]

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=context)
        api_pool = self.pool['nh.clinical.api']
        api_pool.trigger_notifications(cr, uid, {
            'notifications': self._notifications,
            'parent_id': activity.parent_id.id,
            'creator_id': activity_id,
            'patient_id': activity.data_ref.patient_id.id,
            'model': activity.creator_id._name,
            'group': 'nurse'
        }, context=context)
        return super(nh_clinical_notification_medical_team, self).complete(cr, uid, activity_id, context=context)

    def is_cancellable(self, cr, uid, context=None):
        return True


class nh_clinical_notification_doctor_assessment(orm.Model):
    _name = 'nh.clinical.notification.doctor_assessment'
    _inherit = ['nh.clinical.notification']
    _description = 'Assessment Required'


class nh_clinical_patient_move(orm.Model):
    _name = 'nh.clinical.patient.move'
    _inherit = ['nh.activity.data']  
    _description = "Patient Move"
    _start_view_xmlid = "view_patient_move_form"
    _schedule_view_xmlid = "view_patient_move_form"
    _submit_view_xmlid = "view_patient_move_form"
    _complete_view_xmlid = "view_patient_move_form"
    _cancel_view_xmlid = "view_patient_move_form"
    _columns = {
        'location_id': fields.many2one('nh.clinical.location', 'Destination Location', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
        'from_location_id': fields.many2one('nh.clinical.location', 'Source Location'),
        
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        #import pdb; pdb.set_trace()
        for move in self.browse(cr, uid, ids, context):
            res.append( [move.id, "%s to %s" % ("patient", "location")] )
        return res   
    
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        patient_pool = self.pool['nh.clinical.patient']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        sql = """
            select location_id from nh_activity
            where data_model = 'nh.clinical.patient.move' and state = 'completed' and patient_id = %s
            order by sequence desc limit 1
        """ % activity.patient_id.id or 0
        cr.execute(sql)
        res = cr.fetchone()
#         import pdb; pdb.set_trace()
        from_location_id = res and res[0] or False
        self.write(cr, uid, activity.data_ref.id, {'from_location_id': from_location_id})
        patient_pool.write(cr, uid, activity.data_ref.patient_id.id, {'current_location_id': activity.data_ref.location_id.id}, context)
        super(nh_clinical_patient_move, self).complete(cr, uid, activity_id, context)
        return {}         
    

class nh_clinical_patient_swap_beds(orm.Model):
    _name = 'nh.clinical.patient.swap_beds'
    _inherit = ['nh.activity.data']  
    _description = "Patient Swap"
    _columns = {
        'location1_id': fields.many2one('nh.clinical.location', 'Location 1', domain=[['usage','=','bed']], required=True),
        'location2_id': fields.many2one('nh.clinical.location', 'Location 2', domain=[['usage','=','bed']], required=True),        
    }
    
    
    # activity.location_id -> bed1, bed2 or closest common parent
    # cross-POS allowed? no
    
    
    # FIXME: implementation simple, but wrong
    # consider 'move policies'
    def complete(self, cr, uid, activity_id, context=None):
        api = self.pool['nh.clinical.api']
        activity = api.browse(cr, uid, 'nh.activity', activity_id)
        location1_id = activity.data_ref.location1_id.id
        location2_id = activity.data_ref.location2_id.id
        
        locations = api.location_map(cr, uid, location_ids=[location1_id, location2_id])
        except_if(not (location1_id in locations and location2_id in locations), msg="Locations not found!")
        except_if(not locations[location1_id]['patient_ids'], msg="No patient in location '%s'" % activity.data_ref.location1_id.name)
        except_if(not locations[location2_id]['patient_ids'], msg="No patient in location '%s'" % activity.data_ref.location2_id.name)
        except_if(not (locations[location2_id]['parent_id'] and locations[location2_id]['parent_id']),
                        msg="At least one of the beds have no parent location!")
        parent_location_id = locations[location2_id]['parent_id']
        patient1_id = locations[location1_id]['patient_ids'][0]
        patient2_id = locations[location2_id]['patient_ids'][0]
        patients = api.patient_map(cr, uid, patient_ids=[patient1_id, patient2_id])
        except_if(not (patient1_id in patients and patient2_id in patients), msg="Patients not found!")
        pos_id = patients[patient1_id]['pos_id']
        spell1_activity_id = patients[patient1_id]['spell_activity_id']
        spell2_activity_id = patients[patient2_id]['spell_activity_id']
        
        obs_data_models = api.get_submodels(cr, uid, ['nh.clinical.patient.observation'])
        
        obs1_activity_ids = api.activity_map(cr, uid, pos_ids=[pos_id], 
                                            patient_ids=[patient1_id], states=['new','scheduled'],
                                            data_models=obs_data_models).keys()
 
        obs2_activity_ids = api.activity_map(cr, uid, pos_ids=[pos_id], 
                                            patient_ids=[patient2_id], states=['new','scheduled'],
                                            data_models=obs_data_models).keys()
        

        for activity_id in obs1_activity_ids + obs2_activity_ids:
            api.cancel(cr, uid, activity_id)

        api.create_complete(cr, SUPERUSER_ID, 'nh.clinical.patient.move',
                            {'parent_id': spell1_activity_id}, 
                            {'location_id': parent_location_id, 'patient_id': patient1_id}) 
        api.create_complete(cr, SUPERUSER_ID, 'nh.clinical.patient.placement',
                            {'parent_id': spell2_activity_id}, 
                            {'location_id': location1_id, 'patient_id': patient2_id,
                             'suggested_location_id': locations[location1_id]['parent_id']}) 
        api.create_complete(cr, SUPERUSER_ID, 'nh.clinical.patient.placement',
                            {'parent_id': spell1_activity_id}, 
                            {'location_id': location2_id, 'patient_id': patient1_id,
                             'suggested_location_id': locations[location2_id]['parent_id']}) 
        api.submit(cr, uid, spell1_activity_id, {'location_id': location2_id})
        api.submit(cr, uid, spell2_activity_id, {'location_id': location1_id})
    


class nh_clinical_patient_placement(orm.Model):
    _name = 'nh.clinical.patient.placement'
    _inherit = ['nh.activity.data']       
    _description = "Patient Placement"
    _start_view_xmlid = "view_patient_placement_form"
    _schedule_view_xmlid = "view_patient_placement_form"
    _submit_view_xmlid = "view_patient_placement_form"
    _complete_view_xmlid = "view_patient_placement_complete"
    _cancel_view_xmlid = "view_patient_placement_form"

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.observation.ews', 'type': 'recurring'}]}
    
    _columns = {
        'suggested_location_id': fields.many2one('nh.clinical.location', 'Suggested Location', required=True),
        'location_id': fields.many2one('nh.clinical.location', 'Destination Location'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'reason': fields.text('Reason'),
        'pos_id': fields.related('activity_id', 'pos_id', type='many2one', relation='nh.clinical.pos', string='POS'),
    }

    _form_description = [
        {
            'name': 'location_id',
            'type': 'selection',
            'label': 'Location',
            'initially_hidden': False
        }
    ]

    def get_form_description(self, cr, uid, patient_id, context=None):
        activity_pool = self.pool['nh.activity']
        location_pool = self.pool['nh.clinical.location']
        fd = list(self._form_description)
        # Find Available Beds
        placement_ids = activity_pool.search(cr, uid, [
            ('patient_id', '=', patient_id),
            ('state', 'not in', ['completed', 'cancelled']),
            ('data_model', '=', 'nh.clinical.patient.placement')
        ])
        location_selection = []
        if placement_ids:
            placement = activity_pool.browse(cr, uid, placement_ids[0], context=context)
            location_ids = location_pool.search(cr, uid, [
                ('usage', '=', 'bed'),
                ('parent_id', 'child_of', placement.location_id.id),
                ('is_available', '=', True)
            ], context=context)
            location_selection = [[l, location_pool.read(cr, uid, l, ['name'], context=context)['name']] for l in location_ids]
        for field in fd:
            if field['name'] == 'location_id':
                field['selection'] = location_selection
        return fd

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        return activity.data_ref.suggested_location_id.id
    
    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        move_pool = self.pool['nh.clinical.patient.move']
        ews_pool = self.pool['nh.clinical.patient.observation.ews']
        placement_activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not placement_activity.data_ref.location_id, 
                  msg="Location is not set, placement can't be completed! activity.id = %s" % placement_activity.id) 
        res = super(nh_clinical_patient_placement, self).complete(cr, uid, activity_id, context)
        
        placement_activity = activity_pool.browse(cr, uid, activity_id, context)
        # set spell location
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, placement_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id, 
                  cap="Spell in state 'started' is not found for patient_id=%s" % placement_activity.data_ref.patient_id.id,
                  msg="Placement can not be completed")
        # move to location
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
                                                    {'parent_id': spell_activity_id,
                                                     'creator_id': activity_id},
                                                    {'patient_id': placement_activity.data_ref.patient_id.id,
                                                     'location_id': placement_activity.data_ref.location_id.id})
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id)
        activity_pool.submit(cr, SUPERUSER_ID, spell_activity_id, {'location_id': placement_activity.data_ref.location_id.id})
        # trigger placement policy activities
        for trigger_activity in self._POLICY['activities']:
            pool = self.pool[trigger_activity['model']]
            ta_activity_id = pool.create_activity(cr, SUPERUSER_ID, {
                'parent_id': spell_activity_id,
                'creator_id': activity_id
            }, {
                'patient_id': placement_activity.data_ref.patient_id.id
            }, context=context)
            if trigger_activity['type'] == 'recurring':
                frequency = activity_pool.browse(cr, SUPERUSER_ID, ta_activity_id, context=context).data_ref.frequency
                date_schedule = (dt.now()+td(minutes=frequency)).strftime(DTF)
            else:
                date_schedule = dt.now().replace(minute=0, second=0, microsecond=0)
            if trigger_activity['type'] == 'start':
                activity_pool.start(cr, SUPERUSER_ID, ta_activity_id, context=context)
            elif trigger_activity['type'] == 'complete':
                if trigger_activity.get('data'):
                    activity_pool.submit(cr, SUPERUSER_ID, ta_activity_id, trigger_activity['data'], context=context)
                activity_pool.complete(cr, SUPERUSER_ID, ta_activity_id, context=context)
            else:
                activity_pool.schedule(cr, SUPERUSER_ID, ta_activity_id, date_schedule, context=context)
        return res

     
    def submit(self, cr, uid, activity_id, vals, context=None):
        if vals.get('location_id'):
            location_pool = self.pool['nh.clinical.location']
            available_bed_location_ids = location_pool.get_available_location_ids(cr, uid, ['bed'], context=context)
            except_if(vals['location_id'] not in available_bed_location_ids, msg="Location id=%s is not available" % vals['location_id'])
        super(nh_clinical_patient_placement, self).submit(cr, uid, activity_id, vals, context)
        return {}
        
        
class nh_clinical_patient_discharge(orm.Model):
    _name = 'nh.clinical.patient.discharge'    
    _inherit = ['nh.activity.data']
        
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'location_id': fields.related('activity_id', 'location_id', type='many2one', relation='nh.clinical.location', string='Location'),
        'discharge_date': fields.datetime('Discharge Date')
    }

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        patient_id = activity.data_ref.patient_id.id
        # discharge from current or permanent location ??
        location_id = self.pool['nh.clinical.api'].patient_map(cr, uid, patient_ids=[patient_id])[patient_id]['location_id']
        #get_patient_current_location_id(cr, uid, patient_id, context)
        return location_id      

    def complete(self, cr, uid, activity_id, context=None):
        super(nh_clinical_patient_discharge, self).complete(cr, uid, activity_id, context)
        api_pool = self.pool['nh.clinical.api']
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context)
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity, msg="Patient id=%s has no started spell!" % activity.patient_id.id)
        #import pdb; pdb.set_trace()
        # move
        move_pool = self.pool['nh.clinical.patient.move']
        move_activity_id = move_pool.create_activity(cr, uid, 
            {'parent_id': activity_id, 'creator_id': activity_id}, 
            {'patient_id': activity.data_ref.patient_id.id, 
             'location_id':activity.pos_id and activity.pos_id.lot_discharge_id.id or activity.pos_id.location_id.id}, 
            context)
        activity_pool.complete(cr, uid, move_activity_id, context)      
        # complete spell 

        activity_pool.complete(cr, uid, spell_activity.id, context)
        if activity.data_ref.discharge_date:
            activity_pool.write(cr, SUPERUSER_ID, activity_id, {'date_terminated': activity.data_ref.discharge_date})
            activity_pool.write(cr, SUPERUSER_ID, spell_activity.id, {'date_terminated': activity.data_ref.discharge_date})
        return {}  
             
class nh_clinical_patient_admission(orm.Model):
    _name = 'nh.clinical.patient.admission'    
    _inherit = ['nh.activity.data']
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True), 
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', required=True),
        'suggested_location_id': fields.many2one('nh.clinical.location', 'Suggested Location'),
        'location_id': fields.related('activity_id','location_id', type='many2one', relation='nh.clinical.location', string='Location'),
        'start_date': fields.datetime("Admission Start Date"),
    }
            
            
    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        #import pdb; pdb.set_trace()
        location_id = activity.data_ref.pos_id.lot_admission_id.id #or activity.data_ref.pos_id.location_id.id
        return location_id 
    
    
    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(nh_clinical_patient_admission, self).complete(cr, uid, activity_id, context)
        #import pdb; pdb.set_trace()
        api_pool = self.pool['nh.clinical.api']
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context)
        admission = activity.data_ref
        
        # spell
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, admission.patient_id.id, context=context)
        # FIXME! hadle multiple POS
        except_if(spell_activity_id, msg="Patient id=%s has started spell!" % admission.patient_id.id)
        spell_pool = self.pool['nh.clinical.spell']
        spell_activity_id = spell_pool.create_activity(cr, SUPERUSER_ID, 
           {'creator_id': activity_id},
           {'patient_id': admission.patient_id.id,
            'location_id': admission.location_id.id,
            'pos_id': admission.pos_id.id,
            'start_date': admission.start_date},
           context=None)
        # copy doctors
        #import pdb; pdb.set_trace()
        if activity.creator_id.data_model == "nh.clinical.adt.patient.admit":
            doctor_data = {
                           'con_doctor_ids': [[4, d.id] for d in activity.creator_id.data_ref.con_doctor_ids],
                           'ref_doctor_ids': [[4, d.id] for d in activity.creator_id.data_ref.ref_doctor_ids]
                           }
            activity_pool.submit(cr, uid, spell_activity_id, doctor_data, context)
            
        res[spell_pool._name] = spell_activity_id
        activity_pool.start(cr, SUPERUSER_ID, spell_activity_id, context)
        activity_pool.write(cr, SUPERUSER_ID, admission.activity_id.id, {'parent_id': spell_activity_id}, context)
        # patient move to lot_admission !!If lot_admission isn't set access rights to see the activity will need to be set to pos.location i.e. all locations in the pos
        move_pool = self.pool['nh.clinical.patient.move']
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID, 
            {'parent_id': spell_activity_id, 'creator_id': activity_id}, 
            {'patient_id': admission.patient_id.id, 
             'location_id': activity.pos_id.lot_admission_id.id}, 
            context)
        res[move_pool._name] = move_activity_id
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
        # patient placement
        placement_pool = self.pool['nh.clinical.patient.placement']
        
        placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, 
           {'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
            'creator_id': activity_id},
           {'patient_id': admission.patient_id.id,
            'suggested_location_id': admission.suggested_location_id.id},
           context)
        res[placement_pool._name] = placement_activity_id
       
        return res