# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import logging        
_logger = logging.getLogger(__name__)

def browse_domain(self, cr, uid, domain, limit=None, order=None, context=None):
    ids = self.search(cr, uid, domain, limit=limit, order=order, context=context)
    return self.browse(cr, uid, ids, context)
orm.Model.browse_domain = browse_domain

def read_domain(self, cr, uid, domain, fields=[], context=None):
    ids = self.search(cr, uid, domain, context=context)
    return self.read(cr, uid, ids, fields, context)   
orm.Model.read_domain = read_domain

def except_if(test=True, cap="Exception!", msg="Message is not defined..."):
    if test:
        raise orm.except_orm(cap, msg)

class t4_clinical_patient_activity_trigger(orm.Model):
    """
    """
    _name = 't4.clinical.patient.activity.trigger'
    _periods = [('minute','Minute'), ('hour', 'Hour'), ('day', 'Day'), ('month', 'Month'), ('year', 'Year')]
    
    def _get_date_next(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for trigger in self.browse(cr, uid, ids, context):
            deltas = {}.fromkeys([item[0] for item in self._periods],0)
            deltas[trigger.unit] = trigger.unit_qty
            deltas = {k+'s':v for k,v in deltas.iteritems()} # relativedelta requires years, not year
            res[trigger.id] = (dt.now() + rd(**deltas)).strftime('%Y-%m-%d %H:%M:%S')
        return res
        
    _columns = {        
        'patient_id': fields.many2one('t4.clinical.patient', 'activity', required=True),
        'data_model': fields.text('Data Model', required=True),
        'unit': fields.selection(_periods, 'Time Unit', required=True),
        'unit_qty': fields.integer('Time Units Qty', required=True),
        'activity_ids': fields.many2many('t4.clinical.activity', 'recurrence_activity_rel', 'recurrence_id', 'activity_id', 'Generated Activities'),
        'date_next': fields.function(_get_date_next, type='datetime', string='Next Date', help='Next date from now'),
        'active': fields.boolean('Is Active?'),
    }

    _defaults = {
             'active': True,
             'unit': 'minute',
     }
    
    def name_get(self, cr, uid, ids, context=None):
        res = [(t.id, "%s %s(s)" % (t.unit_qty, t.unit)) for t in self.browse(cr, uid, ids, context)]
        return res    

        

class t4_clinical_activity_type(orm.Model):
    # resources of this model should be created as pre-defined data when creating new data model
    _name = 't4.clinical.activity.type'
    
    def _aw_xmlid2id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        imd_pool = self.pool['ir.model.data']
        for dm in self.browse(cr, uid, ids, context):
            if not dm.act_window_xmlid:
                res[dm.id] = False
                continue
            imd_id = imd_pool.search(cr, uid, [('name','=',dm.act_window_xmlid),('model','=','ir.actions.act_window')], context=context)[0]
            imd = imd_pool.browse(cr, uid, imd_id, context)
            res[dm.id] = imd.res_id
        return res
    _rec_name = 'summary'
    _types = [('clinical','Clinical'), ('admin', 'Administrative')]             
    _columns = {
        'summary': fields.text('activity Summary'), 
        'type': fields.selection(_types, 'Type', help="Clinical: patient-related activity, Administrative: general, non-patient-related activity"),        
        'data_model': fields.text('Model name', help='model name', required=True),
        'act_window_xmlid': fields.text('Window Action XMLID'), 
        'act_window_id': fields.function(_aw_xmlid2id, type='many2one', relation='ir.actions.act_window', string='Window Action'),
        'active': fields.boolean('Is Active?', help='When we don\'t need the model anymore we may hide it instead of deleting'),
        'parent_rule': fields.text('Parent Rule', help='Type domain for parent activity'),
        'children_rule': fields.text('Children Rule', help='Type domain for children Activities'),

        'schedule_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'start_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'submit_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'complete_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'cancel_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'form_dictionary': fields.text('Form Dictionary')
    }
    
    _defaults = {
         'active': True,
     }
    
    def get_field_models(self, cr, uid, field):
        """
        returns data models having field 'field'
        """
        all_models = [self.pool[data_type.data_model] for data_type in self.browse_domain(cr, uid, [])]
        field_models = [m for m in all_models if field in m._columns.keys()]    
        return field_models    
        
        
    def create(self, cr, uid, vals, context=None):
        if not self.pool.models.get(vals['data_model']):
            _logger.error('Model %s is not found in the model pool!' % vals['data_model'])
        res_id = super(t4_clinical_activity_type, self).create(cr, uid, vals, context)
        return res_id

def data_model_event(callback=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            self, cr, uid, activity_id = args[:4]
            activity_id = isinstance(activity_id, (list, tuple)) and activity_id[0] or activity_id
#             if not activity_id:
#                 import pdb; pdb.set_trace()
            assert isinstance(activity_id, (int, long)) and activity_id > 0, \
                    "activity_id must be INT or LONG and > 0, found type='%s', value=%s, f='%s'" \
                    % (type(activity_id),activity_id, f)
            args_list = list(args)
            args_list[3] = activity_id
            args = tuple(args_list)
            context = kwargs.get('context') or {}
#             ctx = context.copy()
#             ctx.update({'api_callback': True})
            activity = self.browse(cr, uid, activity_id, context)
            model_pool = self.pool.get(activity.data_model)
            res = False
            f(*args, **kwargs)
            if model_pool and callback:
                res = eval("model_pool.%s(*args[1:], **kwargs)" % callback)
            else:
                _logger.error("@data_model_event() skipping call. data_model='%s', args='%s', kwargs='%s'" 
                              % (activity.data_model, args, kwargs))
            return res
        return wrapper
    return decorator
    
class t4_clinical_activity(orm.Model):
    """ activity
    """
    
    _name = 't4.clinical.activity'
    _name_rec = 'summary'
    #_inherit = ['mail.thread']

    _states = [('new','new'), ('planned', 'Planned'), ('scheduled', 'Scheduled'), 
               ('started', 'Started'), ('completed', 'Completed'), ('cancelled', 'Cancelled'),
                ('suspended', 'Suspended'), ('aborted', 'Aborted'),('expired', 'Expired')]
    
    
    def _get_data_type_selection(self, cr, uid, context=None):
        sql = "select data_model, summary from t4_clinical_activity_type"
        cr.execute(sql)
        return cr.fetchall()
    
    def _activity2data_res_id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        if not ids:
            return res
        ids = isinstance(ids, (list, tuple)) and ids or [ids]
        for activity in self.read(cr, uid, ids, ['data_ref'], context):
            res[activity['id']] = activity['data_ref'].split(",")[1]
        return res

    def _is_schedule_allowed(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for activity in self.browse(cr, uid, ids, context):
            res[activity.id] = self.pool[activity.data_model].is_action_allowed(activity.state, 'schedule') \
                            and activity.type_id.schedule_view_id.id
        return res

    def _is_start_allowed(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for activity in self.browse(cr, uid, ids, context):
            res[activity.id] = self.pool[activity.data_model].is_action_allowed(activity.state, 'start') \
                            and activity.type_id.start_view_id.id
        return res

    def _is_submit_allowed(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for activity in self.browse(cr, uid, ids, context):
            res[activity.id] = self.pool[activity.data_model].is_action_allowed(activity.state, 'submit') \
                            and activity.type_id.submit_view_id.id
        return res

    def _is_complete_allowed(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for activity in self.browse(cr, uid, ids, context):
            res[activity.id] = self.pool[activity.data_model].is_action_allowed(activity.state, 'complete') \
                            and activity.type_id.complete_view_id.id
        return res

    def _is_cancel_allowed(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for activity in self.browse(cr, uid, ids, context):
            res[activity.id] = self.pool[activity.data_model].is_action_allowed(activity.state, 'cancel') \
                            and activity.type_id.cancel_view_id.id
        return res
    
    _columns = {
        'summary': fields.char('Summary', size=256),
        
        # hierarchies
        'parent_id': fields.many2one('t4.clinical.activity', 'Parent activity', readonly=True, help="Business hierarchy"), 
        'child_ids': fields.one2many('t4.clinical.activity', 'parent_id', 'Child Activities', readonly=True),     
        'creator_id': fields.many2one('t4.clinical.activity', 'Creator activity', readonly=True, help="Evolution hierarchy"), 
        'created_ids': fields.one2many('t4.clinical.activity', 'creator_id', 'Created Activities', readonly=True),
        # state
        'notes': fields.text('Notes'),
        'state': fields.selection(_states, 'State', readonly=True),
        # identification
        'user_id': fields.many2one('res.users', 'Assignee', readonly=True),
        'user_ids': fields.many2many('res.users', 'activity_user_rel', 'activity_id','user_id','Users', readonly=True),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', readonly=True),
        'location_id': fields.many2one('t4.clinical.location', 'Location', readonly=True),        
        'pos_id': fields.many2one('t4.clinical.pos', 'POS', readonly=True),
        # system data
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Write Date', readonly=True),
        'create_uid': fields.many2one('res.users', 'Created By', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated By', readonly=True),        
        # dates planning
        'date_planned': fields.datetime('Planned Time', readonly=True),
        'date_scheduled': fields.datetime('Scheduled Time', readonly=True),
        #dates actions
        'date_started': fields.datetime('Started Time', readonly=True),
        'date_terminated': fields.datetime('Termination Time', help="Completed, Aborted, Expired", readonly=True),
        # dates limits
        'date_deadline': fields.datetime('Deadline Time', readonly=True),
        'date_expiry': fields.datetime('Expiry Time', readonly=True),
        # activity type and related model/resource
        'type_id': fields.many2one('t4.clinical.activity.type', "activity Type", required=True),
        'data_res_id': fields.function(_activity2data_res_id, type='integer', string="Data Model's ResID", help="Data Model's ResID", readonly=True),
        'data_model': fields.text("Data Model", required=True),
        'data_ref': fields.reference('Data Reference', _get_data_type_selection, size=256, readonly=True),
        # UI actions
        'is_schedule_allowed': fields.function(_is_schedule_allowed, type='boolean', string='Is Schedule Allowed?'),
        'is_start_allowed': fields.function(_is_start_allowed, type='boolean', string='Is Start Allowed?'),
        'is_submit_allowed': fields.function(_is_submit_allowed, type='boolean', string='Is Submit Allowed?'),
        'is_complete_allowed': fields.function(_is_complete_allowed, type='boolean', string='Is Complete Allowed?'),
        'is_cancel_allowed': fields.function(_is_cancel_allowed, type='boolean', string='Is Cancel Allowed?'),
        
    }
    
    _sql_constrints = {
        ('data_ref_unique', 'unique(data_ref)', 'Data reference must be unique!'),
   }
    
    _defaults = {
        'state': 'new',
        #'summary': 'Not specified',
    }

    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('summary') and vals.get('data_model'):
            type_pool = self.pool['t4.clinical.activity.type']
            type_id = type_pool.search(cr, uid, [['data_model','=',vals['data_model']]])
            if type_id:
                type = type_pool.read(cr, uid, type_id[0], ['summary'], context=context)
                vals.update({'summary': type['summary']})
                vals.update({'type_id': type['id']})
        activity_id = super(t4_clinical_activity, self).create(cr, uid, vals, context)
        _logger.debug("activity '%s' created, activity.id=%s" % (vals.get('data_model'), activity_id))
        return activity_id
        
    def write(self,cr, uid, ids, vals, context=None):
        res = super(t4_clinical_activity, self).write(cr, uid, ids, vals, context)
        return res
    
    # DATA API
    
    @data_model_event(callback="start_act_window")
    def start_act_window(self, cr, uid, activity_id, fields, context=None):
        return {}
    
    @data_model_event(callback="schedule_act_window")
    def schedule_act_window(self, cr, uid, activity_id, fields, context=None):
        return {}
    
    @data_model_event(callback="submit_act_window")
    def submit_act_window(self, cr, uid, activity_id, fields, context=None):
        return {}
    
    @data_model_event(callback="complete_act_window")
    def complete_act_window(self, cr, uid, activity_id, fields, context=None):
        return {}
    
    @data_model_event(callback="cancel_act_window")
    def cancel_act_window(self, cr, uid, activity_id, fields, context=None):
        return {}      
    
    @data_model_event(callback="update_activity")
    def update_activity(self, cr, uid, activity_id, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)
        return {}        
    
    @data_model_event(callback="submit")
    def submit(self, cr, uid, activity_id, vals, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)
        assert isinstance(vals, dict), "vals must be a dict, found to be %s" % type(vals)
        return {}    
    
    @data_model_event(callback="retrieve") 
    def retrieve(self, cr, uid, activity_id, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)
        return {}
           
 
    @data_model_event(callback="validate")          
    def validate(self, cr, uid, activity_id, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)
        return {}
    
    # MGMT API
    @data_model_event(callback="schedule")
    def schedule(self, cr, uid, activity_id, date_scheduled=None, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)
        if date_scheduled:
            date_formats = ['%Y-%m-%d %H:%M:%S','%Y-%m-%d %H:%M','%Y-%m-%d %H', '%Y-%m-%d']
            res = []
            for df in date_formats:
                try:
                    dt.strptime(date_scheduled, df)
                except:
                    res.append(False)
                else:
                    res.append(True)
            #assert any(res), "date_scheduled must be one of the following types: %s. Found: %s" % (date_formats, date_scheduled) 
        return {}
    
    @data_model_event(callback="assign")
    def assign(self, cr, uid, activity_id, user_id, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)
        assert isinstance(user_id,(int, long)), "user_id must be int or long, found to be %s" % type(user_id)
        return {}        
    
    @data_model_event(callback="unassign")   
    def unassign(self, cr, uid, activity_id, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)
        return {} 
    
    @data_model_event(callback="start")        
    def start(self, cr, uid, activity_id, context=None): 
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)            
        return {} 
    
    @data_model_event(callback="complete")
    def complete(self, cr, uid, activity_id, context=None):    
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)      
        return {} 
    
    @data_model_event(callback="cancel")    
    def cancel(self, cr, uid, activity_id, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)            
        return {} 
    
    @data_model_event(callback="cancel")
    def abort(self, cr, uid, activity_id, context=None):
        assert isinstance(activity_id,(int, long)), "activity_id must be int or long, found to be %s" % type(activity_id)
        return {}


        
class t4_clinical_activity_data(orm.AbstractModel):
    
    _name = 't4.clinical.activity.data'  
    _transitions = {
        'new': ['schedule', 'plan','start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'planned': ['schedule','start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'scheduled': ['start','complete','cancel','submit','assign','unassign','retrieve','validate'],
        'started': ['complete','cancel','submit','assign','unassign','retrieve','validate'],
        'completed': ['retrieve','validate'],
        'cancelled': ['retrieve','validate']
                    }
    def is_action_allowed(self, state, action):
        return action in self._transitions[state]
        
    _columns = {
        'name': fields.char('Name', size=256),
        'type_id': fields.related('activity_id', 'type_id', type='many2one', relation='t4.clinical.activity.type', string="activity Data Type"),
        'activity_id': fields.many2one('t4.clinical.activity', "activity"),
        'date_started': fields.related('activity_id', 'date_started', string='Start Time', type='datetime'),
        'date_terminated': fields.related('activity_id', 'date_terminated', string='Terminated Time', type='datetime'),
        'state': fields.related('activity_id', 'state', string='State', type='char', size=64),  
        'data_model': fields.related('type_id','data_model',type='text',string="Data Model"),    
        'pos_id': fields.related('activity_id', 'pos_id', type='many2one', relation='t4.clinical.pos', string='POS'),        
    }
    
    def create(self, cr, uid, vals, context=None):
#         if not context or not context.get('t4_source') == "t4.clinical.activity":
#             raise orm.except_orm('Only t4.clinical.activity can create t4.clinical.activity.data records!', 'msg')
        rec_id = super(t4_clinical_activity_data, self).create(cr, uid, vals, context)
        return rec_id    
    
    def create_activity(self, cr, uid, vals_activity={}, vals_data={}, context=None):
        assert isinstance(vals_activity, dict), "vals_activity must be a dict, found %" % type(vals_activity)
        assert isinstance(vals_data, dict), "vals_data must be a dict, found %" % type(vals_data)
        activity_pool = self.pool['t4.clinical.activity']
        data_type_pool = self.pool['t4.clinical.activity.type']
        type_id = data_type_pool.search(cr, uid, [('data_model','=',self._name)])
        if not type_id:
            raise orm.except_orm("Model %s is not registered as t4.clinical.activity.type!" % self._name, "Add the type!")
        type_id = type_id and type_id[0] or False
        vals_activity.update({'data_model': self._name})
        vals_activity.update({'type_id': type_id})
        new_activity_id = activity_pool.create(cr, uid, vals_activity, context)
        vals_data and activity_pool.submit(cr, uid, new_activity_id, vals_data, context)

        return new_activity_id
    
    def submit_ui(self, cr, uid, ids, context=None):
        if context.get('active_id'):
            activity_pool = self.pool['t4.clinical.activity']
            activity_pool.write(cr,uid,context['active_id'],{'data_ref': "%s,%s" % (self._name, str(ids[0]))})
            activity = activity_pool.browse(cr, uid, context['active_id'], context)
            activity_pool.update_activity(cr, SUPERUSER_ID, activity.id, context)
            _logger.debug("activity '%s', activity.id=%s data submitted via UI" % (activity.data_model, activity.id))
        return {'type': 'ir.actions.act_window_close'}
    
    def complete_ui(self, cr, uid, ids, context=None):
        print context
        if context.get('active_id'):
            activity_pool = self.pool['t4.clinical.activity']
            activity_pool.write(cr,uid,context['active_id'],{'data_ref': "%s,%s" % (self._name, str(ids[0]))})
            activity = activity_pool.browse(cr, uid, context['active_id'], context)
            activity_pool.update_activity(cr, SUPERUSER_ID, activity.id, context)
            activity_pool.complete(cr, uid, activity.id, context)            
            _logger.debug("activity '%s', activity.id=%s data completed via UI" % (activity.data_model, activity.id))
        return {'type': 'ir.actions.act_window_close'}
    
    def start_act_window(self, cr, uid, activity_id, context=None):
        return self.act_window(cr, uid, activity_id, "start", context)
    def schedule_act_window(self, cr, uid, activity_id, context=None):
        return self.act_window(cr, uid, activity_id, "schedule", context)
    def submit_act_window(self, cr, uid, activity_id, context=None):
        return self.act_window(cr, uid, activity_id, "submit", context)
    def complete_act_window(self, cr, uid, activity_id, context=None):
        return self.act_window(cr, uid, activity_id, "complete", context)
    def cancel_act_window(self, cr, uid, activity_id, context=None):
        return self.act_window(cr, uid, activity_id, "cancel", context)        
        
        
        
    def act_window(self, cr, uid, activity_id, command, context=None):
        activity_id = isinstance(activity_id, (list, tuple)) and activity_id[0] or activity_id
        activity_pool = self.pool['t4.clinical.activity']  
        activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(activity.state not in ['new','planned', 'scheduled','started'], msg="Data can not be submitted for a activity in state %s !" % activity.state)
        except_if(not activity.type_id,msg="Data model is not set for the activity!")
        #import pdb; pdb.set_trace()
        try:
            view = eval("activity.type_id.%s_view_id" % command)
        except:
            except_if(True,msg="Command '%s' is not recognized!" % command)
        except_if(not view, msg="Command '%s' view is not set for data model '%s'" % (command, activity.data_model))                
        ctx = context or {}
        ctx.update({'t4_source': 't4.clinical.activity'}) 
        aw = {      
            'type': 'ir.actions.act_window',
            'view_id': view.id,
            'res_model': view.model,
            'res_id': activity.data_res_id, # must always be there 
            'view_type': view.type,
            'view_mode': view.type,
            'target': "new",
            'context': ctx,
            'name': view.name
        }
        return aw   
    

    def validate(self, cr, uid, activity_id, context=None):
        return {}    

    def start(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not self.is_action_allowed(activity.state, 'start'), msg="activity of type '%s' can not be started from state '%s'" % (activity.data_model, activity.state))                  
        activity_pool.write(cr, uid, activity_id, {'state': 'started', 'date_started': dt.now().strftime(DTF)}, context)
        _logger.debug("activity '%s', activity.id=%s started" % (activity.data_model, activity.id))        
        return {}

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not self.is_action_allowed(activity.state, 'complete'), msg="activity of type '%s' can not be completed from state '%s'" % (activity.data_model, activity.state))      
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S') 
        activity_pool.write(cr, uid, activity.id, {'state': 'completed', 'date_terminated': now}, context)     
        _logger.debug("activity '%s', activity.id=%s completed" % (activity.data_model, activity.id))   
        api_pool = self.pool['t4.clinical.api']
        trigger = api_pool.get_activity_trigger_browse(cr, uid, activity.patient_id.id, activity.data_model, context)
        if trigger:
            model_activity_id = self.pool[activity.data_model].create_activity(cr, uid, {'creator_id': activity_id}, 
                                                                                        {'patient_id': activity.patient_id.id}) 
            activity_pool.schedule(cr, uid, model_activity_id, trigger.date_next, context)
        return {}

    def assign(self, cr, uid, activity_id, user_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not self.is_action_allowed(activity.state, 'assign'), msg="activity of type '%s' can not be assigned in state '%s'" % (activity.data_model, activity.state))
        except_if(activity.user_id, msg="activity is assigned already assigned to %s!" % activity.user_id.name)         
        activity_vals = {'user_id': user_id}
        if len(activity.user_id.employee_ids or []) == 1:
            activity_vals.update({'employee_id': activity.user_id.employee_ids[0].id})
        if activity.user_id.employee_ids: 
            activity_vals.update({'employee_ids': [(4, e.id) for e  in activity.user_id.employee_ids]})
        activity_pool.write(cr, uid, activity_id, activity_vals)
        _logger.debug("activity '%s', activity.id=%s assigned to user.id=%s" % (activity.data_model, activity.id, user_id)) 
        return {}
    
    def unassign(self, cr, uid, activity_id, user_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not self.is_action_allowed(activity.state, 'unassign'), msg="activity of type '%s' can not be unassigned in state '%s'" % (activity.data_model, activity.state))
        except_if(activity.user_id, msg="activity is not assigned yet!")               
        activity_pool.write(cr, uid, activity_id,{'user_id': False}, context) 
        _logger.debug("activity '%s', activity.id=%s unassigned" % (activity.data_model, activity.id))         
        return {}
            
    def abort(self, cr, uid, activity_id, context=None):
        return {}
    
    def cancel(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not self.is_action_allowed(activity.state, 'cancel'), msg="activity of type '%s' can not be cancelled in state '%s'" % (activity.data_model, activity.state))        
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        activity_pool.write(cr, uid, activity_id,{'state': 'cancelled', 'date_terminated': now}, context)
        _logger.debug("activity '%s', activity.id=%s cancelled" % (activity.data_model, activity.id))         
        return {}

    def retrieve(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)    
        except_if(not self.is_action_allowed(activity.state, 'retrieve'), msg="Data can't be retrieved from activity of type '%s' in state '%s'" % (activity.data_model, activity.state))
        return self.retrieve_read(cr, uid, activity_id, context=None)         


    def retrieve_read(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        model_pool = self.pool[activity.data_model]
        return model_pool.read(cr, uid, activity.data_res_id, [], context)
    
    
    def retrieve_browse(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        return activity.data_ref 

    def schedule(self, cr, uid, activity_id, date_scheduled=None, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context=None)
        except_if(not self.is_action_allowed(activity.state, 'schedule'), msg="activity of type '%s' can't be scheduled in state '%s'" % (activity.data_model, activity.state))
        except_if(not activity.date_scheduled and not date_scheduled, msg="Scheduled date is neither set on activity nor passed to the method")
        date_scheduled = date_scheduled or activity.date_scheduled
        activity_pool.write(cr, uid, activity_id, {'date_scheduled': date_scheduled, 'state': 'scheduled'}, context)
        _logger.debug("activity '%s', activity.id=%s scheduled, date_scheduled='%s'" % (activity.data_model, activity.id, date_scheduled))        
        return {}

    def submit(self, cr, uid, activity_id, vals, context=None):
        activity_pool = self.pool['t4.clinical.activity']        
        activity = activity_pool.browse(cr, uid, activity_id, context)              
        except_if(not activity.type_id, msg="Data type is not set for this activity")          
        except_if(not self.is_action_allowed(activity.state, 'submit'), msg="Data can't be submitted to activity of type '%s' in state '%s'" % (activity.data_model, activity.state))
        
        data_vals = vals.copy()
         
        if not activity.data_ref:
            _logger.debug("activity '%s', activity.id=%s data submitted: %s" % (activity.data_model, activity.id, str(data_vals)))
            data_vals.update({'activity_id':activity_id})
            data_id = self.create(cr, uid, data_vals, context)
            activity_pool.write(cr, uid, activity_id, {'data_ref': "%s,%s" % (self._name,data_id)})
        else:      
            _logger.debug("activity '%s', activity.id=%s data submitted: %s" % (activity.data_model, activity.id, str(vals)))
            self.write(cr, uid, activity.data_ref.id, vals, context)
        
        self.update_activity(cr, SUPERUSER_ID, activity_id, context)
        return {} 
    
    def update_activity(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']        
        activity = activity_pool.browse(cr, uid, activity_id, context)   
        activity_vals = {}    
        location_id = self.get_activity_location_id(cr, uid, activity_id)
        patient_id = self.get_activity_patient_id(cr, uid, activity_id)
        pos_id = self.get_activity_pos_id(cr, uid, activity_id)
        user_ids = self.get_activity_user_ids(cr, uid, activity_id)    
        activity_vals.update({'location_id': location_id})
        activity_vals.update({'patient_id': patient_id})
        activity_vals.update({'pos_id': pos_id})
        activity_vals.update({'user_ids': [(6, 0, user_ids)]})
        activity_pool.write(cr, uid, activity_id, activity_vals)
        ##print"activity_vals: %s" % activity_vals
        _logger.debug("activity '%s', activity.id=%s updated with: %s" % (activity.data_model, activity.id, activity_vals))
        return {}             

    def get_activity_pos_id(self, cr, uid, activity_id, context=None):
        pos_id = False 
        if 'pos_id' in self._columns.keys():
            data = self.browse_domain(cr, uid, [('activity_id','=',activity_id)])[0]
            pos_id = data.pos_id and data.pos_id.id or False 
        if pos_id:
            return pos_id
        location_id = self.get_activity_location_id(cr, uid, activity_id)
        if not location_id:
            patient_id = self.get_activity_patient_id(cr, uid, activity_id)
            location_id = self.pool['t4.clinical.api'].get_patient_current_location_id(cr, uid, patient_id, context)
        if location_id:
            location = self.pool['t4.clinical.location'].browse(cr, uid, location_id, context)
            pos_id = location.pos_id and location.pos_id.id or False
        return pos_id
        
    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        location_id = False
        data = self.browse_domain(cr, uid, [('activity_id','=',activity_id)])[0]
        if 'location_id' in self._columns.keys():
            location_id = data.location_id and data.location_id.id or False 
        return location_id

    def get_activity_patient_id(self, cr, uid, activity_id, context=None):
        patient_id = False
        #import pdb; pdb.set_trace()
        data = self.browse_domain(cr, uid, [('activity_id','=',activity_id)])[0]
        if 'patient_id' in self._columns.keys():
            patient_id = data.patient_id and data.patient_id.id or False    
        return patient_id
    
    def get_activity_user_ids(self, cr, uid, activity_id, context=None):
        group_pool = self.pool['res.groups']
        location_pool = self.pool['t4.clinical.location']  
        user_pool = self.pool['res.users']
        activity = self.pool['t4.clinical.activity'].browse(cr, uid, activity_id, context)   
        # get groups where current type is allowed
        group_ids = group_pool.search(cr, uid, [('activity_type_ids','=',activity.type_id.id)])  
        location_id = self.get_activity_location_id(cr, uid, activity_id, context)
        user_ids = []
        if location_id:
            ids = user_pool.search(cr, uid, [['location_ids','!=',False],['groups_id','in',group_ids]])
            for user in user_pool.browse(cr, uid, ids):
                if location_id in user_pool.get_all_responsibility_location_ids(cr, uid, user.id):
                    user_ids.append(user.id)
#                 _logger.info("""get_activity_user_ids() \n
#                             user_pool.get_all_responsibility_location_ids(cr, uid, user.id): % s \n
#                             user.location_ids: %s \n
#                             user_ids: %s \n
#                         """ % (user_pool.get_all_responsibility_location_ids(cr, uid, user.id),
#                                user.location_ids,
#                                user_ids
#                                ))
                    #import pdb; pdb.set_trace()
        return list(set(user_ids))


    def get_activity_browse(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        return activity_pool.browse(cr, uid, activity_id, context)
