# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import psycopg2
import logging

_logger = logging.getLogger(__name__)

def list2sqlstr(lst):
    res = []
    lst = isinstance(lst, (list, tuple)) and lst or [lst]
    for l in lst:
        if isinstance(l, (int, long)):
            res.append("%s" % int(l))
        elif isinstance(l, basestring):
            res.append("'%s'" % l) 
        elif l is None:
            res.append("0")
    return ",".join(res)

class nh_cancel_reason(orm.Model):
    """cancellation reason
    """
    _name = 'nh.cancel.reason'
    _columns = {
        'name': fields.char('Name', size=300),
        'system': fields.boolean('System/User Reason')
    }

    
class nh_activity(orm.Model):
    """ activity
    """
    _name = 'nh.activity'
    _inherit = 'nh.activity'
    
    _columns = {
        # identification
        'user_ids': fields.many2many('res.users', 'activity_user_rel', 'activity_id', 'user_id', 'Users', readonly=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', readonly=True),
        'device_id': fields.many2one('nh.clinical.device', 'Device', readonly=True),
        'location_id': fields.many2one('nh.clinical.location', 'Location', readonly=True),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', readonly=True),
        'spell_activity_id': fields.many2one('nh.activity', 'Spell Activity', readonly=True),
        'cancel_reason_id': fields.many2one('nh.cancel.reason', 'Cancellation Reason')
    }
    
 
    
class nh_activity_data(orm.AbstractModel):
    _inherit = 'nh.activity.data'
    _transitions = {
        'new': ['schedule', 'start', 'complete', 'cancel', 'submit', 'assign', 'unassign'],
        'scheduled': ['schedule', 'start', 'complete', 'cancel', 'submit', 'assign', 'unassign'],
        'started': ['complete', 'cancel', 'submit', 'assign', 'unassign'],
        'completed': ['cancel'],
        'cancelled': []
    }      
    def update_activity(self, cr, uid, activity_id, context=None):
        api = self.pool['nh.clinical.api']
        activity = api.browse(cr, uid, 'nh.activity', activity_id, context)
        activity_vals = {}
        location_id = self.get_activity_location_id(cr, uid, activity_id)
        patient_id = self.get_activity_patient_id(cr, uid, activity_id)
        device_id = self.get_activity_device_id(cr, uid, activity_id)
        pos_id = self.get_activity_pos_id(cr, uid, activity_id)

        if 'patient_id' in self._columns.keys():
            activity_vals.update({'patient_id': patient_id})

        activity_vals.update({'location_id': location_id,
                              'device_id': device_id,
                              'pos_id': pos_id})
        api.write(cr, uid, 'nh.activity', activity_id, activity_vals)
        activities = api.activity_map(cr, uid, pos_ids=[pos_id], patient_ids=[patient_id],
                         data_models=['nh.clinical.spell'], states=['started'])
        spell_activity_id = activities and activities.keys()[0] or False
        # user_ids depend on location_id, thus separate updates
        user_ids = self.get_activity_user_ids(cr, uid, activity_id)
        api.write(cr, uid, 'nh.activity', activity_id, {'user_ids': [(6, 0, user_ids)], 'spell_activity_id': spell_activity_id})
        _logger.debug(
            "activity '%s', activity.id=%s updated with: %s" % (activity.data_model, activity.id, activity_vals))
        return {}

    def get_activity_pos_id(self, cr, uid, activity_id, context=None):
        """
        Returns pos_id for activity calculated based on activity data
        Logic:
        10. If data has 'pos_id' field and it is not False, returns value of the field
        20. If get_activity_location_id() returns location_id, returns location.pos_id.id
        30. If get_activity_patient_id() returns patient_id and api_pool.get_patient_spell_activity_browse, returns spell_activity.data_ref.pos_id.id
        """
        _logger.debug("Calculating pos_id for activity.id=%s" % (activity_id))        
        pos_id = False
        api_pool = self.pool['nh.clinical.api']
        data = self.browse_domain(cr, uid, [('activity_id', '=', activity_id)])[0]
        # 10
        if 'pos_id' in self._columns.keys():
            pos_id = data.pos_id and data.pos_id.id or False
        if pos_id:
            _logger.debug("Returning self based pos_id = %s" % (pos_id))
            return pos_id
        location_id = self.get_activity_location_id(cr, uid, activity_id)
        patient_id = self.get_activity_patient_id(cr, uid, activity_id)
#         # 15
#         if data.activity_id.parent_id:
#             pos_id = data.activity_id.parent_id.pos_id.id
        # 20
        if not location_id:
            patient_map = api_pool.patient_map(cr, uid, patient_ids=[patient_id]).get(patient_id)  
            location_id = patient_map and patient_map['location_id']
            # get_patient_current_location_id(cr, uid, patient_id, context)
            if location_id:
                location = self.pool['nh.clinical.location'].browse(cr, uid, location_id, context)
                pos_id = location.pos_id and location.pos_id.id or False
                if pos_id:
                    _logger.debug("Returning location_id based pos_id = %s" % (pos_id))
                    return pos_id
        # 30
        patient_id = self.get_activity_patient_id(cr, uid, activity_id)
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, uid, patient_id, context=None)
        pos_id = spell_activity and spell_activity.data_ref.pos_id.id
        if pos_id:
            _logger.debug("Returning patient_id based pos_id = %s" % (pos_id))
        else:
            _logger.debug("Unable to calculate pos_id, returning False")
        return pos_id

    def get_activity_device_id(self, cr, uid, activity_id, context=None):       
        """
        """
        device_id = False
        data = self.browse_domain(cr, uid, [('activity_id', '=', activity_id)])[0]
        if 'device_id' in self._columns.keys():
            device_id = data.device_id and data.device_id.id or False
        return device_id

    def get_activity_location_id(self, cr, uid, activity_id, context=None):       
        """
        Returns pos_id for activity calculated based on activity data
        Logic:
        1. If activity_data has 'location_id' field and it is not False, returns value of the field
        2. 
        """
        location_id = False
        data = self.browse_domain(cr, uid, [('activity_id', '=', activity_id)])[0]
        if 'location_id' in self._columns.keys():
            location_id = data.location_id and data.location_id.id or False
        if not location_id:
            location_id = data.activity_id.patient_id.current_location_id.id
        if not location_id:
            location_id = data.activity_id.spell_activity_id and data.activity_id.spell_activity_id.location_id.id or False
        if not location_id:
            location_id = data.activity_id.parent_id and data.activity_id.parent_id.location_id.id or False
        print "location_id: %s" % location_id
        return location_id

    def get_activity_patient_id(self, cr, uid, activity_id, context=None):
        patient_id = False
        # import pdb; pdb.set_trace()
        data = self.browse_domain(cr, uid, [('activity_id', '=', activity_id)])[0]
        if 'patient_id' in self._columns.keys():
            patient_id = data.patient_id and data.patient_id.id or False
        return patient_id
    
    def get_activity_user_ids(self, cr, uid, activity_id, context=None):

        cr.execute("select location_id from nh_activity where id = %s" % activity_id)
        if not cr.fetchone()[0]:
            return []
        sql = """
                select 
                    activity_id,
                    array_agg(user_id) as user_ids
                from     
                    (select distinct on (activity.id, ulr.user_id)
                        activity.id as activity_id,
                        ulr.user_id
                    from user_location_rel ulr
                    inner join res_groups_users_rel gur on ulr.user_id = gur.uid
                    inner join ir_model_access access on access.group_id = gur.gid and access.perm_responsibility = true
                    inner join ir_model model on model.id = access.model_id
                    inner join nh_activity activity on model.model = activity.data_model 
                        and activity.location_id = ulr.location_id
                        and activity.id = {activity_id}) data
                group by activity_id                
                """.format(activity_id=activity_id)
        cr.execute(sql)
        #import pdb; pdb.set_trace()
        res = cr.dictfetchone()
        user_ids = list(res and set(res['user_ids']) or [])
        #print "ACTIVITY DATA get_activity_user_ids user_ids: %s " % user_ids
        return user_ids




class nh_clinical_activity_access(orm.Model):    
    _name = 'nh.clinical.activity.access'
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'location_ids_text': fields.text('Location IDS Text'),
        'parent_location_ids_text': fields.text('Parent Location IDS Text'),
        'location_activity_ids_text': fields.text('Activity IDS Text'),
        'parent_location_activity_ids_text': fields.text('Parent Location Activity IDS Text'),      
                }
    def init(self, cr):
         
        cr.execute("""  
            drop view if exists nh_clinical_activity_access;
            create or replace view 
            nh_clinical_activity_access as(
    with 
        recursive route(level, path, parent_id, id) as (
                select 0, id::text, parent_id, id 
                from nh_clinical_location 
                where parent_id is null
            union
                select level + 1, path||','||location.id, location.parent_id, location.id 
                from nh_clinical_location location 
                join route on location.parent_id = route.id
        ),
        location_parents as (
            select 
                id as location_id, 
                ('{'||path||'}')::int[] as ids 
            from route
            order by path
        ),
        user_access as (
            select
                u.id as user_id,
                array_agg(access.model_id) as model_ids -- can be responsible for
            from res_users u
            inner join res_groups_users_rel gur on u.id = gur.uid

            inner join ir_model_access access on access.group_id = gur.gid and access.perm_responsibility = true
            group by u.id
        ),
        
        user_location as (
            select
                ulr.user_id,
                array_agg(ulr.location_id) as location_ids
            from user_location_rel ulr
            group by ulr.user_id
        ),
        
       user_location_parents_map as (
           select distinct
                   user_location.user_id,
                   parent_location_id
           from user_location
           inner join location_parents on user_location.location_ids && array[location_parents.location_id]
           inner join unnest(location_parents.ids) as parent_location_id on array[parent_location_id] && location_parents.ids
       ),
       user_location_parents as (
               select
                   user_id,
                array_agg(parent_location_id) as ids
            from user_location_parents_map
            group by user_id
        ),
        user_activity as (
            select
                user_location.user_id,
                array_agg(activity.id) as activity_ids
            from user_location
            inner join user_access on user_location.user_id = user_access.user_id
            inner join nh_activity activity on array[activity.location_id] && user_location.location_ids
            inner join ir_model model on model.model = activity.data_model and array[model.id] && user_access.model_ids

            group by user_location.user_id            
        ),
        user_parent_location_activity as(
            select
                user_location_parents.user_id,
                array_agg(activity.id) as ids
            from user_location_parents
            inner join nh_activity activity on array[activity.location_id] && user_location_parents.ids
            group by user_location_parents.user_id
        )
        
select
    user_access.user_id as id,
    user_access.user_id,
    user_location.location_ids::text as location_ids_text,
    user_location_parents.ids::text as parent_location_ids_text,
    user_activity.activity_ids::text as location_activity_ids_text,
    user_parent_location_activity.ids::text as parent_location_activity_ids_text,
    user_location.location_ids as location_ids,
    user_location_parents.ids as parent_location_ids,
    user_activity.activity_ids as location_activity_ids,
    user_parent_location_activity.ids as parent_location_activity_ids
from user_access
inner join user_location on user_location.user_id = user_access.user_id
inner join user_activity on user_activity.user_id = user_access.user_id
inner join user_location_parents on user_location_parents.user_id = user_access.user_id
inner join user_parent_location_activity on user_parent_location_activity.user_id = user_access.user_id
            );                 
        """)






