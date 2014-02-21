# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID
import logging        
_logger = logging.getLogger(__name__)
  
class t4_clinical_task_recurrence(orm.Model):
    """
    To be able to track generation flow changing frequency would be 
    best through replacement of current recurrence with a new one and deactivating the old one.
    
    Missed instances are not handled at this stage.
    
    Month, Year: date_next will be the same as date_start with updated month, year.
    Month, Year: if day in [29,30,31] for months missing this days, the last day will be set
    
    date_next trigger: 
    """
    _name = 't4.clinical.task.recurrence'
    _periods = [('minute','Minute'), ('hour', 'Hour'), ('day', 'Day'), ('month', 'Month'), ('year', 'Year')]
    _columns = {
        'name': fields.char('Name', size=256),
        'vals_task': fields.text('Task Vals'), # init task data
        'vals_data': fields.text('Task Data Vals'), # init data data
        'date_start': fields.datetime('Start Date', required=True),
        'date_finish': fields.datetime('Finish Date'), # may be useful to add cycles number
        'qty2gen': fields.integer('Quantity to Generate'),
        'active': fields.boolean('Is Active?'),      
        'unit': fields.selection(_periods, 'Recurrence Unit'),
        'unit_qty': fields.integer('Qty of Recurrence Units'),
        'task_ids': fields.many2many('t4.clinical.task', 'recurrence_task_rel', 'recurrence_id', 'task_id', 'Generated Tasks'),
        'date_next': fields.datetime('Next Date', readonly=True), # =date_start in create 
    }
    
    def create(self, cr, uid, vals, context=None):
        vals.get('date_start') and vals.update({'date_next': vals['date_start']})
        rec_id = super(t4_clinical_task_recurrence, self).create(cr, uid, vals, context)
        return rec_id
    
    def replace(self, cr, uid, ids, vals, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        res = {}
        for rec in self.browse(cr, uid, ids, context):
            old_vals = self.read(cr, uid, rec.id, [], context)
            del old_vals['id']
            self.write(cr, uid, rec.id, {'active': False}, context)
            old_vals.update(vals)
            res[rec.id] = self.create(cr, uid, old_vals, context)
        return res
    
    def date_next(self, date_next, unit, unit_qty, now=None):
        dn = dt.strptime(date_next, "%Y-%m-%d %H:%M:%S")
        deltas = {}.fromkeys([item[0] for item in self._periods],0) #dict(minute=0, hour=0, day=0, month=0, year = 0)
        deltas[unit] = unit_qty
        deltas = {k+'s':v for k,v in deltas.iteritems()} # relativedelta requires years, not year
        # alternative now for test purpose
        now = now and now or dt.now()
        #print deltas
        while dn <= now:
            dn = dn + rd(**deltas)
        return dn.strftime("%Y-%m-%d %H:%M:%S")

            
    def cron(self, cr, uid, *args):
        # args[0] contains alternative now for test purpose
        now = len(args) and args[0] or dt.now().strftime('%Y-%m-%d %H:%M:%S')
        ids = self.search(cr, uid, [('active','=',True),('date_next','<=',now)])
        if not ids:
            return True
        context = None
        task_pool = self.pool['t4.clinical.task']
        for rec in self.browse(cr, uid, ids, context):
            date_next = self.date_next(rec.date_next, rec.unit, rec.unit_qty, dt.strptime(now,"%Y-%m-%d %H:%M:%S"))
            task_id = task_pool.create(cr, uid, eval(str(rec.vals_task)) or {}, context)
            rec.vals_data and task_pool.submit(cr, uid, task_id, eval(rec.vals_data), context)
            active = rec.qty2gen and rec.qty2gen > len(rec.task_ids) and False or True
            rec_data = {'date_next':date_next, 'active':active, 'task_ids':[(4,task_id)]}
            self.write(cr, uid, ids, rec_data, context)
            _logger.info('Task id=%s successfully created according to recurrence id=%s' % (task_id, rec.id))
        return True   
            
            
    _defaults = {
             'active': True,
     }

class t4_clinical_task_type(orm.Model):
    # resources of this model should be created as pre-defined data when creating new data model
    _name = 't4.clinical.task.type'
    
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
        'summary': fields.text('Task Summary'), 
        'type': fields.selection(_types, 'Type', help="Clinical: patient-related task, Administrative: general, non-patient-related task"),        
        'data_model': fields.text('Model name', help='model name', required=True),
        'act_window_xmlid': fields.text('Window Action XMLID'), 
        'act_window_id': fields.function(_aw_xmlid2id, type='many2one', relation='ir.actions.act_window', string='Window Action'),
        'active': fields.boolean('Is Active?', help='When we don\'t need the model anymore we may hide it instead of deleting'),
        'parent_rule': fields.text('Parent Rule', help='Type domain for parent task'),
        'children_rule': fields.text('Children Rule', help='Type domain for children tasks')

    }
    
    _defaults = {
         'active': True,
         'summary': 'Unknown',
         
     }
        
    def create(self, cr, uid, vals, context=None):
        # the model may be created without window action.
        #import pdb; pdb.set_trace()
        if not vals.get('act_window_xmlid'):
            _logger.warning('Field act_window_xmlid is not foulnd in vals during attempt to create a record for t4.clinical.task.type!')
        res = super(t4_clinical_task_type, self).create(cr, uid, vals, context)
        return res
    
class t4_clinical_task(orm.Model):
    """ task
    """
    
    _name = 't4.clinical.task'
    _name_rec = 'summary'
    _parent_name = 'task_id' # the hierarchy will represent instruction-activity relation. 
    #_inherit = ['mail.thread']

    _states = [('draft','Draft'), ('planned', 'Planned'), ('scheduled', 'Scheduled'), 
               ('started', 'Started'), ('completed', 'Completed'), ('cancelled', 'Cancelled'),
                ('suspended', 'Suspended'), ('aborted', 'Aborted'),('expired', 'Expired')]
    
    def _user2employee_id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        ids = isinstance(ids,(list, tuple)) and ids or [ids]
        employee_pool = self.pool['hr.employee']
        for task in self.browse(cr, uid, ids, context):
            emp_id = employee_pool.search(cr, uid, [('user_id','=',task.user_id.id)], context=context)
            res[task.id] = emp_id and emp_id[0] or False
        return res
    
    _columns = {
        'summary': fields.char('Summary', size=256),
        'task_id': fields.many2one('t4.clinical.task', 'Parent Task'),

        'pos_id': fields.many2one('t4.clinical.pos', 'Point of Service', help="Task with pos_id==False is global, company(trust)-wide"),
        #'location_id': fields.many2one('t4.clinical.location', 'POS Location'),
#         'case_id': fields.many2one('t4.clinical.case', 'Case'), 
#         'spell_id': fields.many2one('t4.clinical.spell', 'Spell of Care'),
        #'patient_id': fields.many2one('res.partner', 'Patient'), 
        'user_id': fields.many2one('res.users', 'Assignee'),
        'employee_id': fields.function(_user2employee_id, type='many2one', relation='hr.employee'),        
        # system data
        'create_date': fields.datetime('Create Date'),
        'write_date': fields.datetime('Write Date'),
        'create_uid': fields.many2one('res.users', 'Created By'),
        'write_uid': fields.many2one('res.users', 'Updated By'),        
        # dates planning
        'date_planned': fields.datetime('Planned Time'),
        'date_scheduled': fields.datetime('Scheduled Time'),
        #dates actions
        'date_started': fields.datetime('Started Time'),
        'date_terminated': fields.datetime('Termination Time', help="Completed, Aborted, Expired"),
        # dates limits
        'date_deadline': fields.datetime('Deadline Time'),
        'date_expiry': fields.datetime('Expiry Time'),
        # completion
        #'time_spent_total': fields.datetime('Total Time spent'), # is it date_complete - date_start ??? if not it means the info should exit somewhere else 
        'notes': fields.text('Notes'),
        'state': fields.selection(_states, 'State'),  
        
        # task type and related model/resource
        'type_id': fields.many2one('t4.clinical.task.type', "Task Type"),
        'data_res_id': fields.integer("Data Model's ResID", help="Data Model's ResID"),
        'data_model': fields.related('type_id','data_model',type='text',string="Data Model")
        
    }
    
    _defaults = {
        'state': 'draft',
        'summary': 'Not specified',
        #'type': 'clinical',
        
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('type_id') and not vals.get('summary'):
            type_pool = self.pool['t4.clinical.task.type']
            task_type = type_pool.browse(cr, uid, vals['type_id'], context)
            vals.update({'summary': task_type.summary})
        rec_id = super(t4_clinical_task, self).create(cr, uid, vals, context)
        return rec_id

    # model triggers (may be not useful)
    def _get_model_method(self, model, method):
        # add more validation here 
        model_pool = self.pool[model]
        method = hasattr(model_pool, method) and getattr(model_pool, method) or False
        return method
    
    # DATA API
    def submit(self, cr, uid, ids, vals, context=None):
        ctx = context and context.copy() or {}
        ctx.update({'t4_source': 't4.clinical.task'})
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        task = self.browse(cr, uid, ids, context)
        model_exception = [t.id for t in task if not t.type_id]        
        if model_exception:
            orm.except_orm("Data can not be submitted for a task without type_id set", 
                           'Make sure that the following tasks are have type_id set: %s' % str(model_exception))            
        allowed_states = ['draft','planned', 'scheduled','started']
        state_exception = [{'id': t.id, 'state': t.state} for t in task if t.state not in allowed_states]        
        if state_exception:
            orm.except_orm("Data can not be submitted for a task in state other than %s!" % allowed_states, 
                           'Make sure that the following tasks are in %s: %s' % (allowed_states, str(state_exception)))    
        
        for t in task:
            model_pool = self.pool[t.data_model]
            if not t.data_res_id:
                data_res_id = model_pool.create(cr, uid, {}, ctx)
                self.write(cr, uid, t.id, {'data_res_id': data_res_id})
            else:
                data_res_id = t.data_res_id
            if not self.validate(cr, uid, t.id, context):
                orm.except_orm("Invalid data!", "Task id %s, data model: %s, data: %s" % (t.id, t.data_model, vals))               
            model_pool.write(cr, uid, data_res_id, vals, context)
        return True

    def submit_act_window(self, cr, uid, ids, fields, context=None):
        #import pdb; pdb.set_trace()
        ctx = context and context.copy() or {}
        ctx.update({'t4_source': 't4.clinical.task'})        
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        task = self.browse(cr, uid, ids[0], context)
        allowed_states = ['draft','planned', 'scheduled','started']
        if task.state not in allowed_states:
            raise orm.except_orm('Data can not be submitted for a task in state %s !' % task.state, 
                           'Make sure that the task is in %s' % allowed_states)

        if not task.type_id:
            raise orm.except_orm('Data model is not set for the task !', 
                           'Set data model first')  
   
        if not task.type_id.act_window_id:   
            raise orm.except_orm('Window action is not set for data model %s' % task.data_model,
                           'Unless window action is not set it is impossible to submit data via UI!')                
        aw_pool = self.pool['ir.actions.act_window']
        aw = aw_pool.browse(cr, uid, task.type_id.act_window_id.id, context)

        return {'type': 'ir.actions.act_window',
                'res_model': aw.res_model,
                'res_id': task.data_res_id, # must always be there 
                'view_type': aw.view_type,
                'view_mode': aw.view_mode,
                'target': aw.target,
                'context': ctx,
                }
        
    def retrieve(self, cr, uid, ids, context=None):  
        return self.retrieve_read(cr, uid, ids, context=None)  
    
    def retrieve_read(self, cr, uid, ids, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        res = {}
        for task in self.browse(cr, uid, ids, context):   
            model_pool = self.pool.get(task.data_model)
            res[task.id] = model_pool and model_pool.read(cr, uid, task.data_res_id, [], context) or False
        return res
    
    def retrieve_browse(self, cr, uid, ids, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        res = {}
        for task in self.browse(cr, uid, ids, context):   
            model_pool = self.pool.get(task.data_model)
            res[task.id] = model_pool and model_pool.browse(cr, uid, task.data_res_id, context) or False
        return res  
          
    def validate(self, cr, uid, ids, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        res = []
        
        for task in self.browse(cr, uid, ids, context):
            model_pool = self.pool[task.data_model]
            res.append(hasattr(model_pool, 'validate') and model_pool.validate(cr,uid,[task.data_res_id], context) or True)
        return all(res)
    
    # MGMT API
    def plan(self, cr, uid, ids, context=None):
        # not to be impl.
        pass 
    def schedule(self, cr, uid, ids, date_scheduled=None, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        allowed_states = ['draft', 'planned']
        for task in self.browse(cr, uid, ids, context):
            if task.state not in allowed_states:
                raise orm.except_orm('Task in state %s can not be scheduled!' % task.state, 
                               'Make sure that the task is in %s' % allowed_states)
            elif not task.date_scheduled  and not date_scheduled:
                raise orm.except_orm('Scheduled date is neither set on task nor passed to the method', 
                               'Make sure that the date is either set on task or passed to the method!')                
            else:
                self.write(cr,uid,ids,{'date_scheduled': date_scheduled or task.date_scheduled, 'state': 'scheduled'}, context)
                
        return True
    
    def assign(self, cr, uid, ids, user_id, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        for task in self.browse(cr, uid, ids, context):
            if task.state not in ['draft','planned','scheduled']:
                raise orm.except_orm('Task in state %s can not be assigned!' % task.state, 
                               'Make sure that the task is in (draft,planned,scheduled)')
            elif task.user_id:
                raise orm.except_orm('Task is assigned already assigned to %s!' % task.user_id.name, 
                               'Un-assign first!')               
            else:
                self.write(cr,uid,ids,{'user_id': user_id}, context)                
        return True        
   
    def unassign(self, cr, uid, ids, user_id, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        allowed_states = ['draft', 'planned', 'scheduled']
        for task in self.browse(cr, uid, ids, context):
            if task.state not in allowed_states:
                raise orm.except_orm('Task in state %s can not be un-assigned!' % task.state, 
                               'Make sure that the task is in %s' % allowed_states)
            elif task.user_id:
                raise orm.except_orm('Non-assigned task can not be un-assigned!', 
                               'Assign first!')               
            else:
                self.write(cr,uid,ids,{'user_id': False}, context)                
        return True 
    
    def button_schedule(self, cr, uid, ids, context=None):
        date_exception = [task.id for task in self.browse(cr, uid, ids, context) if not task.date_scheduled]
        if date_exception:
            raise orm.except_orm("Can't schedule task with scheduled date not set", 
               "The following task have no the date set: %s" % date_exception)
        for task in self.browse(cr, uid, ids, context):
            pass
            
    def button_start(self, cr, uid, ids, fields, context=None):
        res = self.start(cr, uid, ids, context)
        return res
         
    def start(self, cr, uid, ids, context=None):        
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        allowed_states = ['draft', 'planned', 'scheduled']
        for task in self.browse(cr, uid, ids, context):
            if task.state not in ['draft', 'planned', 'scheduled']:
                raise orm.except_orm('Task in state %s can not be started' % task.state, 
                               'Make sure that the task is in %s' % allowed_states)
            elif not task.user_id:
                raise orm.except_orm('Task is not assigned to anyone, thus can not be started', 
                               'Assign first!')               
            else:              
                self.write(cr,uid,ids,{'state': 'started'}, context)             
        return True 
    
    def complete(self, cr, uid, ids, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        allowed_states = ['started']
        for task in self.browse(cr, uid, ids, context):
            if task.state not in allowed_states:
                raise orm.except_orm('Task in state %s can not be completed!' % task.state, 
                               'Make sure that the task is in %s' % allowed_states)
            elif task.state in ['started'] and task.type_id and not self.validate(cr, uid, ids, context):
                raise orm.except_orm('Invalid or missing data for the task id=%s!' % task.id, 
                               'Make sure that data provided is sufficient and valid!')         
            else:
                now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
                self.write(cr,uid,ids,{'state': 'completed', 'date_terminated': now}, context)                
        return True 
    
    def cancel(self, cr, uid, ids, context=None):
        ids = isinstance(ids,(list,tuple)) and ids or [ids]
        allowed_states = ['draft','planned','scheduled','started']
        for task in self.browse(cr, uid, ids, context):
            if task.state not in allowed_states:
                raise orm.except_orm('Task in state %s can not be cancelled!' % task.state, 
                               'Make sure that the task in %s' % allowed_states)           
            else:
                now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
                self.write(cr,uid,ids,{'state': 'cancelled', 'date_terminated': now}, context)                
        return True 
    
    def abort(self, cr, uid, ids, context=None):
        # not to be impl.
        pass  
    

class t4_clinical_task_data(orm.AbstractModel):
    
    _name = 't4.clinical.task.data'
    
    def _task_data2task_type_id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        type_pool = self.pool['t4.clinical.task.type']
        for data_model in self.browse(cr, uid, ids, context):
            type_id = type_pool.search(cr, uid, [('data_model','=',self._name)])
            res[data_model.id] = type_id and type_id[0] or False
        return res
    
    def _task_data2task_id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        task_pool = self.pool['t4.clinical.task']
        for data_model in self.browse(cr, uid, ids, context):
            task_id = task_pool.search(cr, uid, [('data_model','=',self._name),('data_res_id','=',data_model.id)])
            res[data_model.id] = task_id and task_id[0] or False
        return res
    
    
    _columns = {
        'name': fields.char('Name', size=256),
        'task_type_id': fields.function(_task_data2task_type_id, type='many2one', relation='t4.clinical.task.type', string="Task Attrs"),
        'task_id': fields.function(_task_data2task_id, type='many2one', relation='t4.clinical.task', string="Task"),
        'pos_id': fields.related('task_id', 'pos_id', string='Point of Service', type='many2one', relation='t4.clinical.pos'),
        'date_started': fields.related('task_id', 'date_started', string='Start Time', type='datetime'),
        'date_terminated': fields.related('task_id', 'date_terminated', string='Terminated Time', type='datetime'),
        'state': fields.related('task_id', 'state', string='Start Time', type='char', size=64),        
    }

    def create(self, cr, uid, vals, context=None):
        if not context or not context.get('t4_source') == "t4.clinical.task":
            raise orm.except_orm('Only t4.clinical.task can create t4.clinical.task.data records!', 'msg')
        rec_id = super(t4_clinical_task_data, self).create(cr, uid, vals, context)
        return rec_id    
    
    def create_task(self, cr, uid, pos_id=False, vals_data={}, context=None):
        """
        parent_task_id expected in the context
        """
        context = context and context or {}
        parent_task_id = context.get('parent_task_id')
        task_pool = self.pool['t4.clinical.task']
        type_id = type_pool.search(cr, uid, [('data_model','=',self._name)])
        type_id = type_id and type_id[0] or False
        task_id = task_pool.create(cr, uid, {'type_id': type_id, 'pos_id': pos_id, 'task_id': parent_task_id})
        vals_data and task_pool.submit(cr, uid, task_id, vals_data, context)
        return task_id
    
    def save(self, cr, uid, ids, context=None):
        #from pprint import pprint as pp
        #pp(context)
        if context.get('active_id'):
            task_pool = self.pool['t4.clinical.task']
            task_pool.write(cr,uid,context['active_id'],{'data_res_id': ids[0]})
        return {'type': 'ir.actions.act_window_close'}
    
    def validate(self, cr, uid, ids, context=None):
        return True    
    

class observation_test(orm.Model):
    _name = 'observation.test'
    _inherit = ['t4.clinical.task.data']    
    _columns = {
        'val1': fields.text('val1'),
        'val2': fields.text('val2')
    }
