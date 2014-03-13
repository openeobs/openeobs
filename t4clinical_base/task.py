# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID
import logging        
_logger = logging.getLogger(__name__)

def res2ref(self, model, res_id):
    return "%s,%s" % (str(model), str(res_id))

def ref2res(self, ref):
    if ref:
        model, res_id = ref.split(",")
        res_id = int(res_id)
    else:
        model, res_id = False, False
    return model, res_id

def create_ref(self, cr, uid, host_id, ref_model, ref_vals,  ref_field, context=None):
    """
    created resource in model ref_model and binds it to host_id.ref_field
    """
    
    if not isinstance(host_id, (int,long)):
        raise orm.except_orm("host_id must be integer or long!",
                              "Current host_id=%s" % host_id)
    if not self.pool.models.get(ref_model):
        raise orm.except_orm("Model %s is not found in the model pool!" % ref_model,
                              "Create the model!")
    ref_model = self.pool[ref_model]
    ref_id = ref_model.create(cr, uid, ref_vals, context)
    self.write(cr, uid, host_id, {ref_field: "%s,%s" % (ref_model._name, ref_id)}, context)
    return ref_id

def browse_ref(self, cr, uid, host_id, ref_field, context=None):
    if not isinstance(host_id, (int,long)):
        raise orm.except_orm("host_id must be integer or long!",
                              "Current host_id=%s" % host_id)    
    host_resource = self.browse(cr, uid, host_id, context)
    return eval("host_resource.%s" % ref_field)

def read_ref(self, cr, uid, host_id, ref_field, fields=[], context=None):
    if not isinstance(host_id, (int,long)):
        raise orm.except_orm("host_id must be integer or long!",
                              "Current host_id=%s" % host_id)    
    host_resource = self.read(cr, uid, host_id, [ref_field], context)
    model,res_id = host_resource[ref_field].split(',')
    ref_model = self.pool[model]
    if not model or not res_id:
        return []
    return ref_model.read(cr, uid, int(res_id), fields, context)

def write_ref(self, cr, uid, host_id, vals, ref_field, context=None):
    """
    writes to resource related to host_id.ref_field
    returns True or False
    """
    if not isinstance(host_id, (int,long)):
        raise orm.except_orm("host_id must be integer or long!",
                              "Current host_id=%s" % host_id)    
    host_resource = self.read(cr, uid, host_id, [ref_field], context)
    model,res_id = host_resource[ref_field].split(',')
    if not res_id or not model:
        return False
    ref_model = self.pool[model]
    #import pdb; pdb.set_trace()
    return ref_model.write(cr, uid, int(res_id), vals, context)

def search_ref(self, cr, uid, host_domain, ref_domain, ref_field, context=None):
    """
    returns host_ids that are intersection of host_domain and ref_domain 
    """
    field_list = [rd[0] for rd in ref_domain if isinstance(rd,(list, tuple))]
    sql_models = """select 
                        imf.model
                    from %s 
                    inner join ir_model_fields imf on imf.model = split_part(%s,',',1)
                    group by imf.model
                    having array_agg(imf.name) @> array[%s]
                    """ % ( self._table, ref_field, ",".join(field_list))
    cr.execute(sql_models)
    models = cr.fetchall()
    if not models:
        return []
    refs = []
    for model in models:
        model_pool = self.pool[model[0]]
        ids = model_pool.search(cr, uid, ref_domain, context=None)
        for id in ids:
            refs.append("%s,%s", (model_pool._name,str(id)))
    host_domain.append((ref_field,'in',refs))    
    host_ids = search(cr, uid, host_domain, context=None)
    return host_ids


def read_none(self, cr, uid, ids, fields=[], context=None):
    """
    If in the DB field value=false in the result it will be replaced with None
    """
    import psycopg2
    from psycopg2 import extras
    from openerp.tools import config
        
    single = not isinstance(ids, (tuple,  list))
    ids =  isinstance(ids, (tuple,  list)) and ids or [ids]
    read_vals = self.read(cr, uid, ids, fields, context)
    numeric_fields = [k for k in self._columns if self._columns[k]._type in ('integer', 'float')]
    if not numeric_fields:
        return single and read_vals[0] or read_vals
    numeric_fields.append('id')
    kwargs = {'database': config['db_name'], 'user': config['db_user'], 'password': config['db_password']}
    config['db_host'] and kwargs.update({'host': config['db_host']})
    config['db_port'] and kwargs.update({'port': config['db_port']}) 
    cn = psycopg2.connect(**kwargs)
    cr2 = cn.cursor(cursor_factory=extras.DictCursor)
    sql = "select %s from %s where id in (%s)" % (",".join(numeric_fields), self._table, ",".join([str(id) for id in ids]))
    cr2.execute(sql)
    res = cr2.fetchall()
    sql_vals = [{k:v for k,v in r.iteritems()} for r in res]
    cr2.close()
    cn.close()     
    cr.execute(sql)
    #import pdb; pdb.set_trace()
    for sql_row in sql_vals:
        [row.update(sql_row) for row in read_vals if row['id'] == sql_row['id']][0]

    return single and read_vals[0] or read_vals

def browse_domain(self, cr, uid, domain, limit=None, order=None, context=None):
    ids = self.search(cr, uid, domain, limit=limit, order=order, context=context)
    ##print ids
    return self.browse(cr, uid, ids, context)

def read_domain(self, cr, uid, domain, fields=[], context=None):
    ids = self.search(cr, uid, domain, context=context)
    return self.read(cr, uid, ids, fields, context)   

def except_if(test=True, cap="Exception!", msg="Message is not defined..."):
    if test:
        raise orm.except_orm(cap, msg)
    
def browse_model(self, cr, uid, model, ids, context=None):
    model_pool = self.pool.get('model')
    except_if(not model_pool, msg="Model '%s' is not found in the model pool!" % model)
    return model_pool.browse(cr, uid, ids, context)   
     
orm.Model.res2ref = res2ref
orm.Model.ref2res = ref2res 
orm.Model.create_ref = create_ref    
orm.Model.browse_ref = browse_ref
orm.Model.read_ref = read_ref
orm.Model.write_ref = write_ref
orm.Model.search_ref = search_ref  
orm.Model.read_none = read_none
orm.Model.browse_domain = browse_domain
orm.Model.read_domain = read_domain
orm.Model.browse_model = browse_model


class t4_clinical_patient_task_trigger(orm.Model):
    """
    """
    _name = 't4.clinical.patient.task.trigger'
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
        'active': fields.boolean('Is Active?'), 
        'patient_id': fields.many2one('t4.clinical.patient', 'Task'),
        'data_model': fields.text('Data Model'),
        'unit': fields.selection(_periods, 'Recurrence Unit'),
        'unit_qty': fields.integer('Qty of Recurrence Units'),
        'task_ids': fields.many2many('t4.clinical.task', 'recurrence_task_rel', 'recurrence_id', 'task_id', 'Generated Tasks'),
        'date_next': fields.function(_get_date_next, type='datetime', string='Next Date', help='Next date from now')
    }

    _defaults = {
             'active': True,
     }
    
    def name_get(self, cr, uid, ids, context=None):
        res = [(t.id, "%s %s(s)" % (t.unit_qty, t.unit)) for t in self.browse(cr, uid, ids, context)]
        return res    

      
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
    
    _defaults = {
             'active': True
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
        ##print deltas
        while dn <= now:
            dn = dn + rd(**deltas)
        return dn.strftime("%Y-%m-%d %H:%M:%S")

            
    def cron(self, cr, uid, *args):
        # args[0] contains alternative now for test purpose
        now = len(args) and args[0] or dt.now().strftime('%Y-%m-%d %H:%M:%S')
        ids = self.search(cr, uid, [('date_next','<=',now)])
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
        'children_rule': fields.text('Children Rule', help='Type domain for children tasks'),
        'start_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'schedule_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'submit_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'complete_view_id': fields.many2one('ir.ui.view', "Submit View"),
        'cancel_view_id': fields.many2one('ir.ui.view', "Submit View"),
    }
    
    _defaults = {
         'active': True,    
     }
    
    def get_field_models(self, cr, uid, field):
        all_models = [self.pool[data_type.data_model] for data_type in self.browse_domain(cr, uid, [])]
        field_models = [m for m in all_models if field in m._columns.keys()]    
        return field_models    
        
        
    def create(self, cr, uid, vals, context=None):
        if not vals.get('act_window_xmlid'):
            _logger.warning('Field act_window_xmlid is not found in vals during attempt to create a record for t4.clinical.task.type!')
        if not self.pool.models.get(vals['data_model']):
            _logger.error('Model %s is not found in the model pool!' % vals['data_model'])
        res_id = super(t4_clinical_task_type, self).create(cr, uid, vals, context)
        return res_id

def data_model_event(callback=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            self, cr, uid, task_id = args[:4]
            task_id = isinstance(task_id, (list, tuple)) and task_id[0] or task_id
            args_list = list(args)
            args_list[3] = task_id
            args = tuple(args_list)
            context = kwargs.get('context') or {}
#             ctx = context.copy()
#             ctx.update({'api_callback': True})
            task = self.browse(cr, uid, task_id, context)
            model_pool = self.pool.get(task.data_model)
            res = False
            f(*args, **kwargs)
            if model_pool and callback:
                res = eval("model_pool.%s(*args[1:], **kwargs)" % callback)
            return res
        return wrapper
    return decorator
    
class t4_clinical_task(orm.Model):
    """ task
    """
    
    _name = 't4.clinical.task'
    _name_rec = 'type_id'
    #_parent_name = 'task_id' # the hierarchy will represent instruction-activity relation. 
    #_inherit = ['mail.thread']

    _states = [('draft','Draft'), ('planned', 'Planned'), ('scheduled', 'Scheduled'), 
               ('started', 'Started'), ('completed', 'Completed'), ('cancelled', 'Cancelled'),
                ('suspended', 'Suspended'), ('aborted', 'Aborted'),('expired', 'Expired')]
    
    
    def _get_data_type_selection(self, cr, uid, context=None):
        sql = "select data_model, summary from t4_clinical_task_type"
        cr.execute(sql)
        return cr.fetchall()
    
    def _task2data_res_id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        if not ids:
            return res
        ids = isinstance(ids, (list, tuple)) and ids or [ids]
        for task in self.read(cr, uid, ids, ['data_ref'], context):
            res[task['id']] = self.ref2res(task['data_ref'])[1]
        return res

    
    _columns = {
        'summary': fields.char('Summary', size=256),
        'parent_id': fields.many2one('t4.clinical.task', 'Parent Task'), 
        'child_ids': fields.one2many('t4.clinical.task', 'parent_id', 'Child Tasks'),     

        'creator_task_id': fields.many2one('t4.clinical.task', 'Creator Task'), 
        'created_task_ids': fields.one2many('t4.clinical.task', 'creator_task_id', 'Created Tasks'), 

        'notes': fields.text('Notes'),
        'state': fields.selection(_states, 'State'),
        # coordinates
        'user_id': fields.many2one('res.users', 'Assignee'),
        'user_ids': fields.many2many('res.users', 'task_user_rel', 'task_id','user_id','Users'),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'location_id': fields.many2one('t4.clinical.location', 'Location'),        
        'pos_id': fields.related('location_id', 'pos_id', type='many2one', relation='t4.clinical.pos', string='POS'),
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
        # task type and related model/resource
        'type_id': fields.many2one('t4.clinical.task.type', "Task Type"),
        'data_res_id': fields.function(_task2data_res_id, type='integer', string="Data Model's ResID", help="Data Model's ResID"),
        'data_model': fields.related('type_id','data_model',type='text',string="Data Model"),
        'data_ref': fields.reference('Data Reference', _get_data_type_selection, size=256)
        
    }
    
    _sql_constrints = {
        ('data_ref_unique', 'unique(data_ref)', 'Data reference must be unique!'),
   }
    
    _defaults = {
        'state': 'draft',
        'summary': 'Not specified',
    }

    def get_task_ids(self, cr, uid, data_model, data_domain=[], order=None, limit=None, context=None):
        data_pool = self.pool[data_model]
        task_ids = [d.task_id.id for d in data_pool.browse_domain(cr, uid, data_domain, order=order, limit=limit)]
        return task_ids
    
    def create(self, cr, uid, vals, context=None):
        task_id = super(t4_clinical_task, self).create(cr, uid, vals, context)
        task = self.browse(cr, uid, task_id, context)
        _logger.info("Task '%s' created, task.id=%s" % (task.data_model, task_id))
        return task_id
        
    def write(self,cr, uid, ids, vals, context=None):
        res = super(t4_clinical_task, self).write(cr, uid, ids, vals, context)
        return res
    
    # DATA API
    
    @data_model_event(callback="start_act_window")
    def start_act_window(self, cr, uid, task_id, fields, context=None):
        return True
    
    @data_model_event(callback="schedule_act_window")
    def schedule_act_window(self, cr, uid, task_id, fields, context=None):
        return True
    
    @data_model_event(callback="submit_act_window")
    def submit_act_window(self, cr, uid, task_id, fields, context=None):
        return True
    
    @data_model_event(callback="complete_act_window")
    def complete_act_window(self, cr, uid, task_id, fields, context=None):
        return True
    
    @data_model_event(callback="cancel_act_window")
    def cancel_act_window(self, cr, uid, task_id, fields, context=None):
        return True      
    
    
    @data_model_event(callback="submit")
    def submit(self, cr, uid, task_id, vals, context=None):
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)
        assert isinstance(vals, dict), "vals must be a dict, found to be %s" % type(vals)
        return True    
    
    @data_model_event(callback="retrieve") 
    def retrieve(self, cr, uid, task_id, context=None):
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)
        return True
           
 
    @data_model_event(callback="validate")          
    def validate(self, cr, uid, task_id, context=None):
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)
        return True
    
    # MGMT API
    @data_model_event(callback="schedule")
    def schedule(self, cr, uid, task_id, date_scheduled=None, context=None):
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)
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
        return True
    
    @data_model_event(callback="assign")
    def assign(self, cr, uid, task_id, user_id, context=None):
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)
        assert isinstance(user_id,(int, long)), "user_id must be int or long, found to be %s" % type(user_id)
        return True        
    
    @data_model_event(callback="unassign")   
    def unassign(self, cr, uid, task_id, context=None):
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)
        return True 
    
    @data_model_event(callback="start")        
    def start(self, cr, uid, task_id, context=None): 
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)            
        return True 
    
    @data_model_event(callback="complete")
    def complete(self, cr, uid, task_id, context=None):    
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)      
        return True 
    
    @data_model_event(callback="cancel")    
    def cancel(self, cr, uid, task_id, context=None):
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)            
        return True 
    
    @data_model_event(callback="cancel")
    def abort(self, cr, uid, task_id, context=None):
        assert isinstance(task_id,(int, long)), "task_id must be int or long, found to be %s" % type(task_id)
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
    
    def get_available_bed_location_ids(self, cr, uid, location_id=None, context=None):
        """
        beds not placed into and not in non-terminated placement tasks
        """
        #import pdb; pdb.set_trace()
        domain = [('usage','=','bed')]
        location_id and  domain.append(('location_id','child_of',location_id)) 
        location_pool = self.pool['t4.clinical.location']
        location_ids = location_pool.search(cr, uid, domain)
        spell_pool = self.pool['t4.clinical.spell']
        domain = [('state','=','started'),('location_id','in',location_ids)]
        spell_ids = spell_pool.search(cr, uid, domain)
        location_ids = list(set(location_ids) - set([s.location_id.id for s in spell_pool.browse(cr, uid, spell_ids, context)]))
        placement_pool = self.pool['t4.clinical.patient.placement']
        domain = [('date_terminated','=',False),('location_id','in',location_ids)]    
        placement_ids = placement_pool.search(cr, uid, domain)
        location_ids = list(set(location_ids) - set([p.location_id.id for p in placement_pool.browse(cr, uid, placement_ids, context)]))
        return location_ids

    def get_not_palced_patient_ids(self, cr, uid, location_id=None, context=None):
        #import pdb; pdb.set_trace()
        domain = [('state','=','started'),('location_id','=',False)]
        location_id and  domain.append(('location_id','child_of',location_id))
        spell_pool = self.pool['t4.clinical.spell']
        spell_ids = spell_pool.search(cr, uid, domain)
        patient_ids = [s.patient_id.id for s in spell_pool.browse(cr, uid, spell_ids, context)]
        return patient_ids
           
    def get_patient_spell_task_id(self, cr, uid, patient_id, context=None):
        domain = [('patient_id','=',patient_id),('state','=','started'),('data_model','=','t4.clinical.spell')]
        spell_task_id = self.search(cr, uid, domain)
        if not spell_task_id:
            return False
        if len(spell_task_id) >1:
            _logger.warn("For pateint_id=%s found more than 1 started spell_task_ids: %s " % (patient_id, spell_task_id))
        return spell_task_id[0]
    
    def get_patient_spell_task_browse(self, cr, uid, patient_id, context=None):
        spell_task_id = self.get_patient_spell_task_id(cr, uid, patient_id, context)
        if not spell_task_id:
            return False
        return self.browse(cr, uid, spell_task_id, context)

    def set_task_trigger(self, cr, uid, patient_id, data_model, unit, unit_qty, context=None):
        trigger_pool = self.pool['t4.clinical.patient.task.trigger']
        trigger_id = trigger_pool.search(cr, uid, [('patient_id','=',patient_id),('data_model','=',data_model)])
        if trigger_id:
            trigger_id = trigger_id[0]
            trigger_pool.write(cr, uid, trigger_id, {'active': False})

        trigger_data = {'patient_id': patient_id, 'data_model': data_model, 'unit': unit, 'unit_qty': unit_qty}
        trigger_id = trigger_pool.create(cr, uid, trigger_data)        
        _logger.info("Task frequency for patient_id=%s data_model=%s set to %s %s(s)" % (patient_id, data_model, unit_qty, unit))
        return trigger_id
        
class t4_clinical_task_data(orm.AbstractModel):
    
    _name = 't4.clinical.task.data'  
    _events = [] # (event_model, handler_model)  
    _columns = {
        'name': fields.char('Name', size=256),
        'type_id': fields.related('task_id', 'type_id', type='many2one', relation='t4.clinical.task.type', string="Task Data Type"),
        'task_id': fields.many2one('t4.clinical.task', "Task"),
        'date_started': fields.related('task_id', 'date_started', string='Start Time', type='datetime'),
        'date_terminated': fields.related('task_id', 'date_terminated', string='Terminated Time', type='datetime'),
        'state': fields.related('task_id', 'state', string='Start Time', type='char', size=64),  
        'data_model': fields.related('type_id','data_model',type='text',string="Data Model"),    
        'pos_id': fields.related('task_id', 'pos_id', type='many2one', relation='t4.clinical.pos', string='POS'),        
    }
    
    def event(self, cr, uid, model, event, task_id, context=None):
        assert model in self.pool.models.keys(), "Model is not found in model pool!"
        assert isinstance(task_id, (int, long)), "task_id must be int or long, found %" % type(task_id)
        """
        This method may be called by any other method when it needs to notify about event
        ex.: placement to notify about completion so interested data models can update location_id
        """
        # get derived models
        print "event self:", self
        for e in self._events:
            if e[0] == model:
                pool = self.pool[e[1]]
                pool.event(cr, uid, model, event, task_id)
        return True
    
    def create(self, cr, uid, vals, context=None):
#         if not context or not context.get('t4_source') == "t4.clinical.task":
#             raise orm.except_orm('Only t4.clinical.task can create t4.clinical.task.data records!', 'msg')
        rec_id = super(t4_clinical_task_data, self).create(cr, uid, vals, context)
        return rec_id    
    
    def create_task(self, cr, uid, vals_task={}, vals_data={}, context=None):
        assert isinstance(vals_task, dict), "vals_task must be a dict, found %" % type(vals_task)
        assert isinstance(vals_data, dict), "vals_data must be a dict, found %" % type(vals_data)
        task_pool = self.pool['t4.clinical.task']
        data_type_pool = self.pool['t4.clinical.task.type']
        type_id = data_type_pool.search(cr, uid, [('data_model','=',self._name)])
        if not type_id:
            raise orm.except_orm("Model %s is not registered as t4.clinical.task.type!" % self._name,
                       "Add the type!")
        type_id = type_id and type_id[0] or False
        vals_task.update({'type_id': type_id})
        new_task_id = task_pool.create(cr, uid, vals_task, context)
        vals_data and task_pool.submit(cr, uid, new_task_id, vals_data, context)
        return new_task_id
    
    def submit_ui(self, cr, uid, ids, context=None):
        if context.get('active_id'):
            task_pool = self.pool['t4.clinical.task']
            task_pool.write(cr,uid,context['active_id'],{'data_ref': "%s,%s" % (self._name, str(ids[0]))})
            task = task_pool.browse(cr, uid, context['active_id'], context)
            _logger.info("Task '%s', task.id=%s data submitted via UI" % (task.data_model, task.id))
        return {'type': 'ir.actions.act_window_close'}
    
    
    def start_act_window(self, cr, uid, task_id, context=None):
        return self.act_window(cr, uid, task_id, "start", context)
    def schedule_act_window(self, cr, uid, task_id, context=None):
        return self.act_window(cr, uid, task_id, "schedule", context)
    def submit_act_window(self, cr, uid, task_id, context=None):
        return self.act_window(cr, uid, task_id, "submit", context)
    def complete_act_window(self, cr, uid, task_id, context=None):
        return self.act_window(cr, uid, task_id, "complete", context)
    def cancel_act_window(self, cr, uid, task_id, context=None):
        return self.act_window(cr, uid, task_id, "cancel", context)        
        
        
        
    def act_window(self, cr, uid, task_id, command, context=None):
        task_id = isinstance(task_id, (list, tuple)) and task_id[0] or task_id
        task_pool = self.pool['t4.clinical.task']  
        task = task_pool.browse(cr, uid, task_id, context)
        except_if(task.state not in ['draft','planned', 'scheduled','started'], msg="Data can not be submitted for a task in state %s !" % task.state)
        except_if(not task.type_id,msg="Data model is not set for the task!")
        #import pdb; pdb.set_trace()
        try:
            view = eval("task.type_id.%s_view_id" % command)
        except:
            except_if(True,msg="Command '%s' is not recognized!" % command)
        except_if(not view, msg="%s view is not set for data model %s" % (command.capitalize(), task.data_model))                
        #view_pool = self.pool['ir.ui.view']
        #view = view_pool.browse(cr, uid, view.id, context)
        ctx = context or {}
        ctx.update({'t4_source': 't4.clinical.task'}) 
        aw = {'type': 'ir.actions.act_window',
                    'res_model': view.model,
                    'res_id': task.data_res_id, # must always be there 
                    'view_type': view.type,
                    'view_mode': view.type,
                    'target': "new",
                    'context': ctx,
                    'name': view.name
                    }
        return aw   
    

    def validate(self, cr, uid, task_id, context=None):
        return True    

    def start(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        allowed_states = ['draft', 'planned', 'scheduled']
        task = task_pool.browse(cr, uid, task_id, context)
        except_if(task.state not in ['draft', 'planned', 'scheduled'], msg="Task in state %s can not be started" % task.state)                  
        task_pool.write(cr, uid, task_id, {'state': 'started'}, context)
        _logger.info("Task '%s', task.id=%s started" % (task.data_model, task.id))        
        return True

    def complete(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)
        except_if(task.state not in ['started'], msg="Task in state %s can not be completed!" % task.state)      
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S') 
        task_pool.write(cr, uid, task.id, {'state': 'completed', 'date_terminated': now}, context)     
        _logger.info("Task '%s', task.id=%s completed" % (task.data_model, task.id))   
        trigger_pool = self.pool['t4.clinical.patient.task.trigger']
        trigger_id = trigger_pool.search(cr, uid, [('patient_id','=',task.patient_id.id),('data_model','=',self._name)])
        if trigger_id:
            trigger_id = trigger_id[0]
            trigger = trigger_pool.browse(cr, uid, trigger_id, context)
            model_pool = self.pool[task.data_model]
            
            model_task_id = model_pool.create_task(cr, uid, {}, {'patient_id': task.patient_id.id})  
            task_pool.schedule(cr, uid, model_task_id, trigger.date_next, context)
        return True

    def assign(self, cr, uid, task_id, user_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)
        allowed_states = ['draft','planned','scheduled']
        except_if(task.state not in ['draft','planned','scheduled'], msg="Task in state %s can not be assigned!" % task.state)
        except_if(task.user_id, msg="Task is assigned already assigned to %s!" % task.user_id.name)         
        task_vals = {'user_id': user_id}
        if len(task.user_id.employee_ids or []) == 1:
            task_vals.update({'employee_id': task.user_id.employee_ids[0].id})
        if task.user_id.employee_ids: 
            task_vals.update({'employee_ids': [(4, e.id) for e  in task.user_id.employee_ids]})
        task_pool.write(cr, uid, task_id, task_vals)
        _logger.info("Task '%s', task.id=%s assigned to user.id=%s" % (task.data_model, task.id, user_id)) 
        return True
    
    def unassign(self, cr, uid, task_id, user_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)
        except_if(task.state not in ['draft','planned','scheduled'], msg="Task in state %s can not be unassigned!" % task.state)
        except_if(task.user_id, msg="Task is not assigned yet!")               
        task_pool.write(cr, uid, task_id,{'user_id': False}, context) 
        _logger.info("Task '%s', task.id=%s unassigned" % (task.data_model, task.id))         
        return True
            
    def abort(self, cr, uid, task_id, context=None):
        return True
    
    def cancel(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        allowed_states = ['draft','planned','scheduled','started']
        task = task_pool.browse(cr, uid, task_id, context)
        except_if(task.state not in ['draft','planned','scheduled','started'], msg="Task in state %s can not be cancelled!" % task.state)         
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        task_pool.write(cr, uid, task_id,{'state': 'cancelled', 'date_terminated': now}, context)
        _logger.info("Task '%s', task.id=%s cancelled" % (task.data_model, task.id))         
        return True

    def retrieve(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context)    
        return self.retrieve_read(cr, uid, task_id, context=None)         


    def retrieve_read(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        return task_pool.read_ref(cr, uid, task_id, 'data_ref', context)
    
    
    def retrieve_browse(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        return task_pool.browse_ref(cr, uid, task_id, 'data_ref', context) 

    def schedule(self, cr, uid, task_id, date_scheduled=None, context=None):
        task_pool = self.pool['t4.clinical.task']
        task = task_pool.browse(cr, uid, task_id, context=None)
        #except_if(task.state not in ['draft', 'planned'], msg="Task in state %s can not be scheduled!" % task.state)
        except_if(not task.date_scheduled and not date_scheduled, msg="Scheduled date is neither set on task nor passed to the method")
        date_scheduled = date_scheduled or task.date_scheduled
        task_pool.write(cr, uid, task_id, {'date_scheduled': date_scheduled, 'state': 'scheduled'}, context)
        _logger.info("Task '%s', task.id=%s scheduled, date_scheduled='%s'" % (task.data_model, task.id, date_scheduled))        
        return True

    def submit(self, cr, uid, task_id, vals, context=None):
        task_pool = self.pool['t4.clinical.task']        
        task = task_pool.browse(cr, uid, task_id, context)              
        except_if(not task.type_id, msg="Data type is not set for this task")          
        allowed_states = ['draft','planned', 'scheduled','started']
        except_if(task.state not in allowed_states, msg="Data can't be submitted in state '%s'" % task.state)       
        
        data_vals = vals.copy()
         
        if not task.data_ref:
            data_vals.update({'task_id':task_id})
            _logger.info("Task '%s', task.id=%s data submitted: %s" % (task.data_model, task.id, str(data_vals)))
            data_id = self.create(cr, uid, data_vals, context)
            task_pool.write(cr, uid, task_id, {'data_ref': "%s,%s" % (self._name,data_id)})
        else:      
            _logger.info("Task '%s', task.id=%s data submitted: %s" % (task.data_model, task.id, str(vals)))
            self.write(cr, uid, task.data_ref.id, vals, context)
        
        self.update_task(cr, uid, task_id, context)
        return True 
    
    def update_task(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']        
        task = task_pool.browse(cr, uid, task_id, context)   
        task_vals = {}    
        location_id = self.get_task_location_id(cr, uid, task_id)
        patient_id = self.get_task_patient_id(cr, uid, task_id)
        user_ids = self.get_task_user_ids(cr, uid, task_id)    
        task_vals.update({'location_id': location_id})
        task_vals.update({'patient_id': patient_id})
        task_vals.update({'user_ids': [(6, 0, user_ids)]})
        task_pool.write(cr, uid, task_id, task_vals)
        ##print"task_vals: %s" % task_vals
        _logger.info("Task '%s', task.id=%s updated with: %s" % (task.data_model, task.id, task_vals))
        return True             
        
    def get_task_location_id(self, cr, uid, task_id, context=None):
        location_id = False
        data = self.browse_domain(cr, uid, [('task_id','=',task_id)])[0]
        if 'location_id' in self._columns.keys():
             location_id = data.location_id and data.location_id.id or False 
        return location_id

    def get_task_patient_id(self, cr, uid, task_id, context=None):
        patient_id = False
        #import pdb; pdb.set_trace()
        data = self.browse_domain(cr, uid, [('task_id','=',task_id)])[0]
        if 'patient_id' in self._columns.keys():
             patient_id = data.patient_id and data.patient_id.id or False    
        return patient_id
    
    def get_task_user_ids(self, cr, uid, task_id, context=None):
        location_pool = self.pool['t4.clinical.location']  
        user_pool = self.pool['res.users']
        task = self.pool['t4.clinical.task'].browse(cr, uid, task_id, context)   
        user_ids = []      
        location_id = self.get_task_location_id(cr, uid, task_id, context)
        location = location_pool.browse(cr, uid, location_id, context)
        if location_id:
            parent_location_ids = [location_id]
            parent_id = location.parent_id and location.parent_id.id
            while parent_id:
                parent_location_ids.append(parent_id)
                parent_location = location_pool.browse_domain(cr, uid, [('id','=',parent_id)])[0]
                parent_id = parent_location.parent_id and parent_location.parent_id.id
            for location_id in parent_location_ids:
                user_ids.extend(user_pool.search(cr, uid, [('location_ids','child_of',location_id), ('task_type_ids','=',task.type_id.id)]))    
            ##print "parent_location_ids: %s" % parent_location_ids        
        return list(set(user_ids))
    
        
#     def get_task_employee_id(self, cr, uid, task_id, context=None):
#         employee_id = False  
#         data = self.browse_domain(cr, uid, [('task_id','=',task_id)])[0]      
#         # 1. if task assigned to a user that has only 1 related employee 
#         if data.task_id.user_id and len(data.task_id.user_id.employee_ids) == 1:
#             employee_id = data.user_id.employee_ids[0].id
#         return employee_id
#         
#     
#     def get_task_employee_ids(self, cr, uid, task_id, context=None):
#         location_pool = self.pool['t4.clinical.location']
#         employee_pool = self.pool['hr.employee']        
#         employee_ids = []    
#         data = self.browse_domain(cr, uid, [('task_id','=',task_id)])[0]    
#         user_employees = data.task_id.user_id and data.task_id.user_id.employee_ids
#         user_employee_ids = user_employees and [e.id for e in data.task_id.user_id.employee_ids] or []
#         location_id = self.get_task_location_id(cr, uid, task_id, context)
#         location = location_pool.browse(cr, uid, location_id, context)
#         if location_id:
#             parent_location_ids = [location_id]
#             parent_id = location.parent_id and location.parent_id.id
#             # branch location ids
#             while parent_id:
#                 parent_location_ids.append(parent_id)
#                 parent_location = location_pool.browse_domain(cr, uid, [('id','=',parent_id)])[0]
#                 parent_id = parent_location.parent_id and parent_location.parent_id.id
#             for location_id in parent_location_ids:
#                 employee_ids.extend(employee_pool.search(cr, uid, [('location_ids','=',location_id)]))    
#             ##print "parent_location_ids: %s" % parent_location_ids
#         employee_ids.extend(user_employee_ids)        
#         return employee_ids    
    
    def get_task_browse(self, cr, uid, task_id, context=None):
        task_pool = self.pool['t4.clinical.task']
        return task_pool.browse(cr, uid, task_id, context)

    def after_create(self, cr, uid, task_id, context=None):
        return True       

# 
# class t4_clinical_task_resource(orm.Model):
#     _name = 't4.clinical.task.resource'
#     _columns = {
#         'name': fields.text('name'),
#         'category_id': fields.many2one('t4.clinical.task.resource.category', 'Category')
#     }
# 
# class t4_clinical_task_resource_category(orm.Model):
#     _name = 't4.clinical.task.resource.category'
#     _columns = {
#         'name': fields.text('name'),
#         'resource_ids': fields.one2many('t4.clinical.task.resource', 'category_id', 'Resources')
#     }    
# 
# class t4_clinical_task_resource_uom(orm.Model):
#     _name = 't4.clinical.task.resource.uom'
#     _columns = {
#         'name': fields.text('name'),
#     }    
# class t4_clinical_task_resource_uom_rate(orm.Model):
#     _name = 't4.clinical.task.resource.uom.rate'
#     _columns = {
#         'name': fields.text('name'),
#         'from_resource_id': fields.many2one('t4.clinical.task.resource', 'From Resource'),
#         'into_resource_id': fields.many2one('t4.clinical.task.resource', 'Into Resource'),
#         'rate': fields.float('Rate Ratio (into/from)')  
#            
#     }






    
class observation_test(orm.Model):
    _name = 'observation.test'
    _inherit = ['t4.clinical.task.data']    
    _columns = {
        'val1': fields.text('val1'),
        'val2': fields.text('val2')
    }   