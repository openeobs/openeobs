# -*- coding: utf-8 -*-

from openerp.osv import orm, fields
from openerp.addons.t4activity.activity import except_if
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_spell(orm.Model):
    _name = 't4.clinical.spell'
    _inherit = ['t4.activity.data']
    _description = "Spell / Visit"
    
    _rec_name = 'code'
    
    def _get_transfered_user_ids(self, cr, uid, ids, field, arg, context=None):   
        res = {spell_id: False for spell_id in ids} 
        sql = """
            with 
                recursive route(level, path, parent_id, id) as (
                        select 0, id::text, parent_id, id 
                        from t4_clinical_location 
                        where parent_id is null
                    union
                        select level + 1, path||','||location.id, location.parent_id, location.id 
                        from t4_clinical_location location 
                        join route on location.parent_id = route.id
                ),
                parent_location as (
                    select 
                        id as location_id, 
                        ('{'||path||'}')::int[] as ids 
                    from route
                    order by path
                ),
                spell_transferred_locations as(
                    select 
                        spell.id as spell_id,
                        spell_activity.id as activity_id,
                        array_agg(move.from_location_id) as location_ids
                    from t4_clinical_patient_move move
                    inner join t4_activity move_activity on move.activity_id = move_activity.id 
                        and move.from_location_id is not null 
                        and move_activity.state = 'completed'
                    inner join t4_activity spell_activity on move_activity.parent_id = spell_activity.id
                    inner join t4_clinical_spell spell on spell.activity_id = spell_activity.id
                    where now() at time zone 'UTC' - move_activity.date_terminated < interval '1d'
                        and spell_activity.state = 'started'
                    group by spell_id, spell_activity.id
                )
            select
                stl.activity_id,
                stl.spell_id,
                array_agg(ulr.user_id) as user_ids
            from user_location_rel ulr
            inner join res_groups_users_rel gur on ulr.user_id = gur.uid
            inner join ir_model_access access on access.group_id = gur.gid and access.perm_responsibility = true
            inner join ir_model model on model.id = access.model_id and model.model = 't4.clinical.spell'
            inner join parent_location on parent_location.location_id = ulr.location_id
            inner join spell_transferred_locations stl on stl.location_ids && parent_location.ids
            where stl.spell_id in (%s)
            group by activity_id, stl.spell_id        
        """ % ",".join(map(str,ids))
        cr.execute(sql)
        rows = cr.dictfetchall()
        [res.update({row['spell_id']: list(set(row['user_ids']))}) for row in rows]
        return res
    
    def _transfered_user_ids_search(self, cr, uid, obj, name, args, domain=None, context=None):
        arg1, op, arg2 = args[0]
        arg2 = isinstance(arg2, (list, tuple)) and arg2 or [arg2]
        all_ids = self.search(cr, uid, [])
        spell_user_map = self._get_transfered_user_ids(cr, uid, all_ids, 'transfered_user_ids', None)
        spell_ids = [k for k, v in spell_user_map.items() if set(v or []) & set(arg2 or [])]
        
        return [('id', 'in', spell_ids)]   
     
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'location_id': fields.many2one('t4.clinical.location', 'Placement Location'),
        'pos_id': fields.many2one('t4.clinical.pos', 'Placement Location', required=True),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"),
        'ref_doctor_ids': fields.many2many('res.partner', 'ref_doctor_spell_rel', 'spell_id', 'doctor_id', "Referring Doctors"),
        'con_doctor_ids': fields.many2many('res.partner', 'con_doctor_spell_rel', 'spell_id', 'doctor_id', "Consulting Doctors"),  
        'transfered_user_ids': fields.function(_get_transfered_user_ids, fnct_search=_transfered_user_ids_search, type='many2many', relation='res.users', string="Recently Transfered Access"),      
    }
    _defaults = {
         'code': lambda s, cr, uid, c: s.pool['ir.sequence'].next_by_code(cr, uid, 't4.clinical.spell', context=c),
     }

    def create(self, cr, uid, vals, context=None):
        current_spell_id = self.search(cr, uid, [('patient_id','=',vals['patient_id']),('state','in',['started'])], context)
#         if current_spell_id:
#             import pdb; pdb.set_trace()
        if current_spell_id:
            res = current_spell_id[0]
            _logger.warn("Started spell already exists! Current spell ID=%s returned." % current_spell_id[0])
        else:        
            res = super(t4_clinical_spell, self).create(cr, uid, vals, context)
        return res

    def get_activity_user_ids(self, cr, uid, activity_id, context=None):
        cr.execute("select location_id from t4_activity where id = %s" % activity_id)
        if not cr.fetchone()[0]:
            return []
        sql = """
            with 
                recursive route(level, path, parent_id, id) as (
                        select 0, id::text, parent_id, id 
                        from t4_clinical_location 
                        where parent_id is null
                    union
                        select level + 1, path||','||location.id, location.parent_id, location.id 
                        from t4_clinical_location location 
                        join route on location.parent_id = route.id
                ),
                parent_location as (
                    select 
                        id as location_id, 
                        ('{'||path||'}')::int[] as ids 
                    from route
                    order by path
                )
            select
                activity.id as activity_id,
                array_agg(ulr.user_id) as user_ids
            from user_location_rel ulr
            inner join res_groups_users_rel gur on ulr.user_id = gur.uid
            inner join ir_model_access access on access.group_id = gur.gid and access.perm_responsibility = true
            inner join ir_model model on model.id = access.model_id and model.model = 't4.clinical.spell'
            inner join parent_location on parent_location.ids  && array[ulr.location_id]
            inner join t4_activity activity on model.model = activity.data_model 
                and activity.location_id = parent_location.location_id
                and activity.id = %s
            group by activity_id               
                """ % activity_id
        cr.execute(sql)
        #import pdb; pdb.set_trace()
        res = cr.dictfetchone()
        user_ids = list(res and set(res['user_ids']) or [])
        return user_ids
    
    