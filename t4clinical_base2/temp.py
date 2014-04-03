# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID
import logging        
_logger = logging.getLogger(__name__)

      
class t4_clinical_activity_recurrence(orm.Model):
    """
    To be able to track generation flow changing frequency would be 
    best through replacement of current recurrence with a new one and deactivating the old one.
    
    Missed instances are not handled at this stage.
    
    Month, Year: date_next will be the same as date_start with updated month, year.
    Month, Year: if day in [29,30,31] for months missing this days, the last day will be set
    
    date_next trigger: 
    """
    _name = 't4.clinical.activity.recurrence'
    _periods = [('minute','Minute'), ('hour', 'Hour'), ('day', 'Day'), ('month', 'Month'), ('year', 'Year')]
    _columns = {
        'name': fields.char('Name', size=256),
        'vals_activity': fields.text('activity Vals'), # init activity data
        'vals_data': fields.text('activity Data Vals'), # init data data
        'date_start': fields.datetime('Start Date', required=True),
        'date_finish': fields.datetime('Finish Date'), # may be useful to add cycles number
        'qty2gen': fields.integer('Quantity to Generate'),
        'active': fields.boolean('Is Active?'),     
        'unit': fields.selection(_periods, 'Recurrence Unit'),
        'unit_qty': fields.integer('Qty of Recurrence Units'),
        'activity_ids': fields.many2many('t4.clinical.activity', 'recurrence_activity_rel', 'recurrence_id', 'activity_id', 'Generated Activities'),
        'date_next': fields.datetime('Next Date', readonly=True), # =date_start in create 
    }
    
    _defaults = {
             'active': True
     }
    
    def create(self, cr, uid, vals, context=None):
        vals.get('date_start') and vals.update({'date_next': vals['date_start']})
        rec_id = super(t4_clinical_activity_recurrence, self).create(cr, uid, vals, context)
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
        activity_pool = self.pool['t4.clinical.activity']
        for rec in self.browse(cr, uid, ids, context):
            date_next = self.date_next(rec.date_next, rec.unit, rec.unit_qty, dt.strptime(now,"%Y-%m-%d %H:%M:%S"))
            activity_id = activity_pool.create(cr, uid, eval(str(rec.vals_activity)) or {}, context)
            rec.vals_data and activity_pool.submit(cr, uid, activity_id, eval(rec.vals_data), context)
            active = rec.qty2gen and rec.qty2gen > len(rec.activity_ids) and False or True
            rec_data = {'date_next':date_next, 'active':active, 'activity_ids':[(4,activity_id)]}
            self.write(cr, uid, ids, rec_data, context)
            _logger.debug('activity id=%s successfully created according to recurrence id=%s' % (activity_id, rec.id))
        return True   
            
