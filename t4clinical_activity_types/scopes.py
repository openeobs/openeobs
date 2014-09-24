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
    _columns = {
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
        'location_id': fields.many2one('t4.clinical.location', 'Placement Location'),
        'pos_id': fields.many2one('t4.clinical.pos', 'Placement Location', required=True),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"),
        'ref_doctor_ids': fields.many2many('res.partner', 'ref_doctor_spell_rel', 'spell_id', 'doctor_id', "Referring Doctors"),
        'con_doctor_ids': fields.many2many('res.partner', 'con_doctor_spell_rel', 'spell_id', 'doctor_id', "Consulting Doctors"),        
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
        user_ids = res and res['user_ids'] or []
        print "SPELL DATA get_activity_user_ids user_ids: %s " % user_ids
        return user_ids
    
    