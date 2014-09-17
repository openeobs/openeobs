# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID
from pprint import pprint as pp

import logging        
_logger = logging.getLogger(__name__)

"""
Currently the target for this API is:

API consists of 3 classes of methods:
    1. <object>_map
    2. get_<object>s
    3. <action>[_<action> or _activity]

    1. <object>_map:
        accepts arguments in the way of lists representing positive condition of relation to the list items
        example: api.patient_map(cr, uid, 
                                    patient_ids=patient_ids, 
                                    parent_location_ids=[env.pos_id.location_id.id], 
                                    pos_ids=[env.pos_id.id])
        currently following methods of this class exist:
            - location_map
            - patient_map
            - user_map
            - activity_map
            TODO: pos_map, device_map
    
    2. get_<object>s
        wrappers of class(1) returning either ids or browse_list depend on return_id flag value (default=False)
        arguments concept is the same as in class(1)
        currently following methods of this class exist:
            - get_activities
            - get_locations
            - get_patients
            TODO: get_users, get_poss, get_devices
            
    3. <action>[_<action> or _activity]
        actions on activities
        this class can be divided further into 3 subclasses:
            3.1 ORM actions
            3.2 single actions
            3.3 combined actions
            
            3.1 ORM actions
                this subclass represents ORM shortcuts accessible via API model
                currently following methods of this class exist:
                    - write_activity
                    - create_activity
           3.2 single actions
               activity action shortcuts accessible via API model
               currently following methods of this class exist:
                   - assign
                   - cancel
                   - complete
                   - start
                   - submit
                   - unassign
            3.3 combined actions
                combined activity action helpers
                currently following methods of this class exist:
                    - create_complete
                    - submit_complete
"""

def norm_ids(ids):
    return [int(id) for id in ids if id not in (None, False, 0)]

def ids2sql(ids):
    return ','.join(map(str, norm_ids(ids)))

def strs2sql(strs):
    norm_strs = [s for s in strs if id not in (None, False, '')]
    if not norm_strs:
        return ''
    else:
        return "'"+"','".join(norm_strs)+"'"

def list2sqlstr(lst):
    res = []
    for l in lst:
        if isinstance(l, (int, long)):
            res.append("%s" % int(l))
        elif isinstance(l, basestring):
            res.append("'%s'" % l) 
        elif l is None:
            res.append("0")
    return ",".join(res)
    
class t4_clinical_api(orm.AbstractModel):
    _name = 't4.clinical.api'

    def search(self, cr, uid, model, args, offset=0, limit=None, order=None, context=None, count=False):
        model_pool = self.pool[model]
        return model_pool.search(cr, uid, args, offset, limit, order, context, count)
    
    def create(self, cr, uid, model, values, context=None):
        model_pool = self.pool[model]
        return model_pool.create(cr, uid, values, context)
        
    def browse(self, cr, uid, model, ids, context=None):
        model_pool = self.pool[model]
        return model_pool.browse(cr, uid, ids, context)

    def write(self, cr, uid, model, ids, values, context=None):
        model_pool = self.pool[model]
        return model_pool.write(cr, uid, ids, values, context)
    
    def get_activity(self, cr, uid, activity_id, return_id=False):
        activity_pool = self.pool['t4.activity']
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id)
                
    def create_activity(self, cr, uid, data_model, vals_activity, vals_data, return_id=False):
        activity_pool = self.pool['t4.activity']
        data_pool = self.pool[data_model]        
        activity_id = data_pool.create_activity(cr, uid, vals_activity, vals_data)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id)        

    def write_activity(self, cr, uid, activity_id, vals_activity, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.write(cr, uid, activity_id, vals_activity)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id) 

    def create_complete(self, cr, uid, data_model, activity_vals={}, data_vals={}, return_id=False):
        data_pool = self.pool[data_model]
        activity_pool = self.pool['t4.activity']
        activity_id = data_pool.create_activity(cr, uid, activity_vals, data_vals)
        activity_pool.complete(cr, uid, activity_id)       
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id)

    def submit_complete(self, cr, uid, activity_id, data_vals={}, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.submit(cr, uid, activity_id, data_vals)
        activity_pool.complete(cr, uid, activity_id)       
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id)

    def schedule(self, cr, uid, activity_id, date_scheduled, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.schedule(cr, uid, activity_id, date_scheduled)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id)     
            
    def start(self, cr, uid, activity_id, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.start(cr, uid, activity_id)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id)       
    
    def complete(self, cr, uid, activity_id, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.complete(cr, uid, activity_id)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id) 
    
    def cancel(self, cr, uid, activity_id, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.cancel(cr, uid, activity_id)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id) 

    def submit(self, cr, uid, activity_id, vals_data, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.submit(cr, uid, activity_id, vals_data)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id) 
    
    def assign(self, cr, uid, activity_id, user_id, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.assign(cr, uid, activity_id, user_id)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id) 
    
    def unassign(self, cr, uid, activity_id, return_id=False):
        activity_pool = self.pool['t4.activity']
        activity_pool.unassign(cr, uid, activity_id)        
        if return_id:
            return activity_id
        else:
            return activity_pool.browse(cr, uid, activity_id) 

    def activity_info(self, cr, uid, activity_id, context={}):
        """
            activity diagnostic info
        """
        res = {}
        activity_pool = self.pool['t4.activity']
        activity = activity_pool.browse(cr, uid, activity_id, {})
        res['activity'] = activity_pool.read(cr,uid,activity_id, [])
        res['data'] = self.pool[activity.data_model].read(cr,uid,activity.data_ref.id, [])
        res['parents'] = {}
        while True:
            parent = activity.parent_id
            if not parent: break
            activity = activity = activity_pool.browse(cr, uid, parent.id, context)
            res['parents'].update({parent.data_model: parent})
        res['creators'] = {}
        activity = activity_pool.browse(cr, uid, activity_id, context)
        while True:
            creator = activity.creator_id
            if not creator: break
            activity = activity_pool.browse(cr, uid, creator.id, context)
            res['creators'].update({creator.data_model: creator}) 
        from pprint import pprint as pp
        pp(res)
        return res       

    def get_patients(self, cr, uid, patient_ids=[], pos_ids=[], location_ids=[], parent_location_ids=[], return_id=False):
        patient_ids = self.patient_map(self, cr, uid, 
                                       patient_ids=patient_ids, 
                                       pos_ids=pos_ids,
                                       location_ids=location_ids,
                                       parent_location_ids=parent_location_ids).keys()
        if return_id:
            return patient_ids
        else:
            return self.pool['t4.clinical.patient'].brpwse(cr, uid, patient_ids)

    def patient_map(self, cr, uid, patient_ids=[], pos_ids=[], location_ids=[], parent_location_ids=[]):  
        """
        Arguments and Return Parameters may be extended at later stages
        Returns:
            Description: user data, real and calculated parameters
            Format: {id: {id, ..., other params}}
            Parameters:
                id: t4.clinical.patient field
                location_id: patient's current location 
                pos_id: patient's current pos
                ...
                TODO:
                    route: {sequence: location_id, ...}
                    spell_activity_id
        Arguments:
           pos_ids=[], patient_ids=[]: unlimited lists of values semantically corresponding to the parameter name
           ...
           TODO:
               route_location_ids=[]: location ids that patient's route crosses
        """
        #assert all([isinstance(id, (int, long)) and id not in (False, True) for id in patient_ids])
#         patient_ids = [id for id in patient_ids  if id not in (False, True)]
#         pos_ids = [id for id in pos_ids  if id not in (False, True)]
        where_list = []
        if patient_ids: where_list.append("id in (%s)" % ','.join([str(int(id)) for id in patient_ids]))
        if pos_ids: where_list.append("pos_id in (%s)" % ','.join([str(int(id)) for id in pos_ids]))
        if location_ids: where_list.append("location_id in (%s)" % ','.join([str(int(id)) for id in location_ids]))
        if parent_location_ids: where_list.append("parent_location_ids && array[%s]" % ','.join([str(int(id)) for id in parent_location_ids]))
        where_clause = where_list and "where %s" % " and ".join(where_list) or ""
        print where_clause     
        sql = """
with
    location_hierarchy  as (
        with recursive location_path(level,path,parent_id,id) as (
            select 0, id::text, parent_id, id from t4_clinical_location where parent_id is null
                union
            select level + 1, path||','||l.id, l.parent_id, l.id from t4_clinical_location l join location_path on l.parent_id = location_path.id
        )
        select id, ('{'||path||'}')::int[] as parent_ids 
        from location_path
        order by path
    ),

    activity_parent_child_hierarchy  as (
        with recursive activity_path(level,path,parent_id,id) as (
            select 0, id::text, parent_id, id from t4_activity where parent_id is null
                union
            select level + 1, path||','||a.id, a.parent_id, a.id from t4_activity a join activity_path on a.parent_id = activity_path.id
        )    
        select id, ('{'||path||'}')::int[] as parent_ids 
        from activity_path
        order by path
    ),
    move_activity as (
        select 
            a.id,
            rank() over(partition by patient_id order by sequence desc),
            patient_id,
            location_id,
            pos_id,
            h.parent_ids
        from t4_activity a 
        inner join activity_parent_child_hierarchy h on h.id = a.id
        where data_model = 't4.clinical.patient.move' and state = 'completed'
    ),
    spell_activity as (
        select 
            patient_id,
            state,
            array_agg(id) as ids,
            max(id) as max_id
            
        from t4_activity
        where data_model = 't4.clinical.spell'
        group by patient_id, state
    )  ,
    map as (
        select 
            patient.id,
            patient.family_name,
            patient.given_name,
            patient.middle_names,
            patient.other_identifier,
            patient.gender,
            patient.dob::text,
            extract(year from age(now(), patient.dob)) as age,
            move_activity.location_id,
            location_hierarchy.parent_ids as parent_location_ids,
            spell_activity.max_id as spell_activity_id,
            previous_spell_activity.ids as previous_spell_activity_ids,
            pos.id as pos_id
        from t4_clinical_patient patient
        left join spell_activity on spell_activity.patient_id = patient.id and spell_activity.state = 'started'
        left join spell_activity previous_spell_activity on previous_spell_activity.patient_id = patient.id and previous_spell_activity.state != 'started'
        left join move_activity on move_activity.patient_id = patient.id and move_activity.rank = 1 and move_activity.parent_ids && array[spell_activity.max_id]
        left join t4_clinical_pos pos on pos.id = move_activity.pos_id
        left join location_hierarchy on location_hierarchy.id = move_activity.location_id
    )

             select * from map %s""" % where_clause
        cr.execute(sql)
        res = {r['id']: r for r in cr.dictfetchall()}
        #import pdb; pdb.set_trace()
        return res

    def get_adt_users(self, cr, uid, pos_ids=[], return_id=False):
        user_ids = self.user_map(cr, uid, pos_ids=pos_ids, group_xmlids=['group_t4clinical_adt']).keys()
        if return_id:
            return user_ids
        else:
            return self.pool['res.users'].browse(cr, uid, user_ids)

    def get_users(self, cr, uid, user_ids=[], group_xmlids=[], assigned_activity_ids=[], pos_ids=[], return_id=False):

        user_ids = self.user_map(cr, uid, user_ids=user_ids, group_xmlids=group_xmlids, 
                                     assigned_activity_ids=assigned_activity_ids, pos_ids=pos_ids).keys()
        if return_id:
            return user_ids
        else:
            return self.pool['res.users'].browse(cr, uid, user_ids)
    
    def user_map(self, cr,uid, user_ids=[], group_xmlids=[], assigned_activity_ids=[], pos_ids=[]):
        """
        Arguments and Return Parameters may be extended at later stages
        Returns:
            Description: user data, real and calculated parameters
            Format: {id: {id, ..., other params}}
            Parameters:
                id, login: res.users fields
                group_xmlids: user's groups xml ids 
                assigned_activity_ids: ids of activities assigned to the user
                ...
                TODO:
                    responsible_activity_ids
                    
        Arguments:
           user_ids=[], group_xmlids=[], assigned_activity_ids=[]: unlimited lists of values semantically corresponding to the parameter name
           ...
           TODO: 
               responsible_activity_ids
           
                   
        returns:
        {user_id: {group_xmlids, assigned_activity_ids, responsible_activity_ids}}
        """
        where_list = []
        if assigned_activity_ids: where_list.append("assigned_activity_ids && array[%s]" % list2sqlstr(assigned_activity_ids))
        if user_ids: where_list.append("user_id in (%s)" % list2sqlstr(user_ids))
        if pos_ids: where_list.append("pos_id in (%s)" % list2sqlstr(pos_ids))
        if group_xmlids: where_list.append("group_xmlids && array['%s']" % "','".join(group_xmlids))
        where_clause = where_list and "where %s" % " and ".join(where_list) or ""       
        sql = """
            with 
            groups as (
                    select 
                        gur.uid as user_id, 
                        array_agg(imd.name::text) as group_xmlids 
                    from res_groups_users_rel gur
                    inner join res_groups g on g.id = gur.gid
                    inner join ir_model_data imd on imd.res_id = g.id and imd.model = 'res.groups'
                    group by gur.uid 
            ), 
            assigned_activity as(
                    select 
                        a.user_id,
                        array_agg(a.id) as assigned_activity_ids
                    from t4_activity a
                    where user_id is not null
                    group by a.user_id
            ),
            map as (
                    select 
                        u.id as user_id,
                        u.login as login,
                        g.group_xmlids,
                        aa.assigned_activity_ids,
                        u.pos_id
                    from res_users u
                    left join groups g on g.user_id = u.id
                    left join assigned_activity aa on aa.user_id = u.id
            )
            select * from map
            {where_clause}
        """.format(where_clause=where_clause)
        cr.execute(sql)
        res = {r['user_id']: r for r in cr.dictfetchall()}
        return res
    
    def get_location_ids(self, cr, uid, location_ids=[], types=[], usages=[], codes=[], pos_ids=[],
                                  occupied_range=[], capacity_range=[], available_range=[]):    
        location_ids = self.location_map(cr, uid, pos_ids=pos_ids,
                                  location_ids=location_ids, types=types, usages=usages, codes=codes,
                                  occupied_range=occupied_range, capacity_range=capacity_range, 
                                  available_range=available_range).keys()
        return location_ids

    def get_locations(self, cr, uid, 
                                  location_ids=[], types=[], usages=[], codes=[], pos_ids=[],
                                  occupied_range=[], capacity_range=[], available_range=[], return_id=False):
        location_ids = self.location_map(cr, uid, pos_ids=pos_ids,
                                  location_ids=location_ids, types=types, usages=usages, codes=codes,
                                  occupied_range=occupied_range, capacity_range=capacity_range, 
                                  available_range=available_range).keys()
        if return_id:
            return location_ids
        else:
            return self.pool['t4.clinical.location'].browse(cr, uid, location_ids)

    def activity_rank_map(self, cr, uid, 
                        partition_by="patient_id, state", partition_order="sequence desc", rank_order="desc",
                        ranks=[],
                        activity_ids=[], pos_ids=[], location_ids=[], patient_ids=[],
                        device_ids=[], data_models=[], states=[]):
        where_list = []
        if activity_ids: where_list.append("id in (%s)" % list2sqlstr(activity_ids))
        if pos_ids: where_list.append("pos_id in (%s)" % ','.join([str(int(id)) for id in pos_ids]))    
        if location_ids: where_list.append("location_id in (%s)" % ','.join([str(int(id)) for id in location_ids])) 
        if patient_ids: where_list.append("patient_id in (%s)" % ','.join([str(int(id)) for id in patient_ids]))
        if device_ids: where_list.append("device_id in (%s)" % ','.join([str(int(id)) for id in device_ids]))
        if data_models: where_list.append("data_model in ('%s')" % "','".join(data_models))
        if states: where_list.append("state in ('%s')" % "','".join(states))
        if ranks: where_list.append("rank in (%s)" % ','.join([str(int(r)) for r in ranks]))
        
        args = {
          "partition_by": partition_by,
          "where": where_list and "where %s" % " and ".join(where_list) or "",
          "partition_order": partition_order
        }
        sql = """
            with 
            activity as (
                select 
                    id, 
                    pos_id,
                    location_id,
                    patient_id,
                    device_id,
                    data_model,
                    state,
                    rank() over (partition by {partition_by} order by {partition_order}) as rank
                from t4_activity
            )
            select * from activity
            {where}
            """.format(**args)
        print sql
        cr.execute(sql)
        res = {r['id']: r['rank'] for r in cr.dictfetchall()}
        return res 

    def activity_map(self, cr, uid, activity_ids=[], creator_ids=[],
                       pos_ids=[], location_ids=[], patient_ids=[],
                       device_ids=[], data_models=[], states=[]):
        """
        Arguments and Return Parameters may be extended at later stages
        Returns:
            Description: user data, real and calculated parameters
            Format: {id: {id, ..., other params}}
            Parameters:
                id, all real fields of t4.activity: t4.clinical.patient field
                ...
                TODO:
                    ...
                    
        Arguments:
           activity_ids=[],
           pos_ids=[], location_ids=[], patient_ids=[],
           device_ids=[], data_models=[], states=[]: unlimited lists of values semantically corresponding to the parameter name
           ...
           TODO:
               ...
        """
        where_list = []
        if activity_ids: where_list.append("id in (%s)" % ','.join([str(int(id)) for id in activity_ids]))
        if creator_ids: where_list.append("creator_id in (%s)" % ','.join([str(int(id)) for id in creator_ids]))
        if pos_ids: where_list.append("pos_id in (%s)" % ','.join([str(int(id)) for id in pos_ids]))    
        if location_ids: where_list.append("location_id in (%s)" % ','.join([str(int(id)) for id in location_ids])) 
        if patient_ids: where_list.append("patient_id in (%s)" % ','.join([str(int(id)) for id in patient_ids]))
        if device_ids: where_list.append("device_id in (%s)" % ','.join([str(int(id)) for id in device_ids]))
        if data_models: where_list.append("data_model in ('%s')" % "','".join(data_models))
        if states: where_list.append("state in ('%s')" % "','".join(states))
        where_clause = where_list and "where %s" % " and ".join(where_list) or ""
        sql = """
        select
            *
        from t4_activity
        
        %s""" % where_clause
        cr.execute(sql)
        #print sql
        res = {r['id']: r for r in cr.dictfetchall()}
        return res
    
    def get_activities(self, cr, uid, activity_ids=[],
                       pos_ids=[], location_ids=[], patient_ids=[],
                       device_ids=[], data_models=[], states=[], 
                       return_id=False):

        activity_ids = self.activity_map(cr, uid, pos_ids=pos_ids, location_ids=location_ids, 
                                             patient_ids=patient_ids, device_ids=device_ids, 
                                             data_models=data_models, states=states).keys()
        
        if return_id:
            return location_ids
        else:
            return self.pool['t4.activity'].browse(cr, uid, activity_ids)
    
    def get_activity_data(self, cr, uid, activity_id):
        activity = self.pool['t4.activity'].browse(cr, uid, activity_id)
        data_pool = self.pool[activity.data_model]
        data = data_pool.read(cr, uid, activity.data_ref.id, [])
        for field_name, field in data_pool._columns.items():
            if field._type == 'many2one' and data.get(field_name):
                data[field_name] = data[field_name][0]
        del data['id']
        return data
        
        
    def location_map(self, cr, uid, location_ids=[], types=[], usages=[], codes=[], pos_ids=[],
                                    patient_ids=[], occupied_range=[], capacity_range=[], available_range=[], debug=True):  
        """
        Arguments and Return Parameters may be extended at later stages
        Returns:
            Description: location data, real and calculated parameters
            Format: {id: {id, code, type, usage, occupied, capacity, available, ..., other params}}
            Parameters:
                id, code, type, usage, occupied, capacity: t4.clinical.location fields
                occupied: calculated as 'patients found as moved in and not moved out'
                available: calculated as 'location capacity' - 'patients found as moved in and not moved out'
                patient_ids: calculated as 'ids of patients found as moved in and not moved out'
                
        Arguments:
           location_ids=[], types=[], usages=[], 
           codes=[], pos_ids=[], patient_ids=[]: unlimited lists of values semantically corresponding to the parameter name
           occupied_range=[], capacity_range=[], available_range=[]: min,max ranges of corresponding values
        """
        # assertions needed because string is taken as list too, and passing string we may end up with:
        # "where field in (s,t,r,i,n,g)" and may miss some results
#         if debug:
#             assert isinstance(location_ids, (list, tuple)) and all([isinstance(i,(int, long)) for i in location_ids]), \
#                 "type = %s, items: %s" % (type(location_ids).__name__, location_ids)
#             assert isinstance(types, (list, tuple)) and all([isinstance(i,(basestring)) for i in types]), \
#                 "type = %s, items: %s" % (type(types).__name__, types)
#             assert isinstance(usages, (list, tuple)) and all([isinstance(i,(basestring)) for i in usages]), \
#                 "type = %s, items: %s" % (type(usages).__name__, usages)            
#             assert isinstance(codes, (list, tuple)) and all([isinstance(i,(basestring)) for i in codes]), \
#                 "type = %s, items: %s" % (type(codes).__name__, codes)  
#             assert isinstance(pos_ids, (list, tuple)) and all([isinstance(i,(int, long)) for i in pos_ids]), \
#                 "type = %s, items: %s" % (type(pos_ids).__name__, pos_ids)   
#             assert isinstance(patient_ids, (list, tuple)) and all([isinstance(i,(int, long)) for i in patient_ids]), \
#                 "type = %s, items: %s" % (type(patient_ids).__name__, patient_ids)   
#             assert isinstance(occupied_range, (list, tuple)) \
#                 and all([isinstance(i,(int, long)) and i>=0 for i in occupied_range]) and len(occupied_range) in [0, 2], \
#                 "type = %s, items: %s" % (type(occupied_range).__name__, occupied_range)      
#             assert isinstance(capacity_range, (list, tuple)) \
#                 and all([isinstance(i,(int, long)) and i>=0 for i in capacity_range]) and len(capacity_range) in [0, 2], \
#                 "type = %s, items: %s" % (type(capacity_range).__name__, capacity_range)                 
#             assert isinstance(available_range, (list, tuple)) \
#                 and all([isinstance(i,(int, long)) and i>=0 for i in available_range]) and len(available_range) in [0, 2], \
#                 "type = %s, items: %s" % (type(available_range).__name__, available_range)                 
                           
        #print "api: map args: location_ids: %s, available_range: %s, usages: %s" % (location_ids,available_range,usages)
        
        where_list = []
        if location_ids: where_list.append("location_id in (%s)" % list2sqlstr(location_ids))
        if patient_ids: where_list.append("patient_ids && array[%s]" % list2sqlstr(patient_ids))
        if pos_ids: where_list.append("pos_id in (%s)" % list2sqlstr(pos_ids))
        if types: where_list.append("type in (%s)" % list2sqlstr(types))
        if usages: where_list.append("usage in (%s)" % list2sqlstr(usages))
        if codes: where_list.append("code in (%s)" % list2sqlstr(codes))                       
        if occupied_range: where_list.append("occupied between %s and %s" % (occupied_range[0], occupied_range[1]))
        if capacity_range: where_list.append("capacity between %s and %s" % (capacity_range[0], capacity_range[1]))
        if available_range: where_list.append("available between %s and %s" % (available_range[0], available_range[1]))
#         if data_models: where_list.append("data_model in ('%s')" % "','".join(data_models))
#         if states: where_list.append("state in ('%s')" % "','".join(states))        
        where_clause = where_list and "where %s" % " and ".join(where_list) or ""
        #print where_clause     
        sql = """
            with
                move_patient_date as (
                    select 
                        max(a.date_terminated) as max_date_terminated,
                        max(sequence) as max_sequence,
                        m.patient_id
                    from t4_clinical_patient_move m
                    inner join t4_activity a on m.activity_id = a.id
                    where a.state = 'completed'
                    group by m.patient_id
                ),
                patient_per_location as (
                    select 
                        m.location_id,
                        count(m.patient_id) as patient_qty,
                        array_agg(mpd.patient_id) as patient_ids
                    from t4_clinical_patient_move m
                    inner join t4_activity ma on m.activity_id = ma.id
                    inner join move_patient_date mpd on m.patient_id = mpd.patient_id
                                                        and ma.sequence = mpd.max_sequence
                    inner join t4_activity sa on sa.data_model='t4.clinical.spell' and m.patient_id = sa.patient_id
                    --left join t4_activity a on a.location_id 
                    where sa.state = 'started'
                    group by m.location_id
                ),
                map as (
                    select 
                        l.id as location_id,
                        l.code,
                        l.type,
                        l.usage,
                        l.pos_id,
                        ppl.patient_qty as occupied,
                        l.patient_capacity as capacity,
                        coalesce(l.patient_capacity, 0) - coalesce(ppl.patient_qty, 0) as available,
                        ppl.patient_ids as patient_ids
                    from t4_clinical_location l
                    left join patient_per_location ppl on l.id = ppl.location_id
                )
                
            select * from map %s """ % where_clause
        cr.execute(sql)
        res = {location['location_id']: location for location in cr.dictfetchall()}
        return res
        
#     def get_not_palced_patient_ids(self, cr, uid, location_id=None, context=None):
#         # all current patients
#         spell_domain = [('state','=','started')]
#         spell_pool = self.pool['t4.clinical.spell']
#         spell_ids = spell_pool.search(cr, uid, spell_domain)
#         spell_patient_ids = [s.patient_id.id for s in spell_pool.browse(cr, uid, spell_ids, context)]
#         # placed current patients
#         placement_domain = [('activity_id.parent_id.state','=','started'),('state','=','completed')]
#         location_id and  placement_domain.append(('activity_id.location_id','child_of',location_id))
#         placement_pool = self.pool['t4.clinical.patient.placement']
#         placement_ids = placement_pool.search(cr, uid, placement_domain)
#         placed_patient_ids = [p.patient_id.id for p in placement_pool.browse(cr, uid, placement_ids, context)]       
#         patient_ids = set(spell_patient_ids) - set(placed_patient_ids)
#         #import pdb; pdb.set_trace()
#         return list(patient_ids)

    def get_patient_spell_activity_id(self, cr, uid, patient_id, pos_id=None, context=None):
        domain = {'patient_ids': [patient_id],
                  'states': ['started'],
                  'data_models': ['t4.clinical.spell']}
        pos_id and domain.update({'pos_ids': [pos_id]})
        spell_activity_id = self.activity_map(cr, uid, **domain).keys()
        if not spell_activity_id:
            return False
        if len(spell_activity_id) > 1:
            _logger.warn("For patient_id=%s found more than 1 started spell_activity_ids: %s " % (patient_id, spell_activity_id))
        return spell_activity_id[0]


    def get_patient_spell_activity_browse(self, cr, uid, patient_id, pos_id=None, context=None):
        spell_activity_id = self.get_patient_spell_activity_id(cr, uid, patient_id, pos_id, context)
        if not spell_activity_id:
            return False
        return self.pool['t4.activity'].browse(cr, uid, spell_activity_id, context)
    
    def get_device_session_activity_id(self, cr, uid, device_id, context=None):
        api = self.pool['t4.clinical.api']
        domain = {'device_ids': [device_id],
                  'states': ['started'],
                  'data_models': ['t4.clinical.device.session']}
        session_activity_id = api.activity_map(cr, uid, **domain).keys()
        if not session_activity_id:
            return False
        if len(session_activity_id) > 1:
            _logger.warn("For device_id=%s found more than 1 started device session activity_ids: %s " 
                         % (device_id, session_activity_id))
        return session_activity_id[0]

#     def get_patient_current_location_browse(self, cr, uid, patient_id, context=None):
#         move_pool = self.pool['t4.clinical.patient.move']
#         move_domain = [('patient_id','=',patient_id), ('state','=','completed')]
#         # sort parameter includes 'id' to resolve situation with equal values in 'date_terminated'
#         move = move_pool.browse_domain(cr, uid, move_domain, limit=1, order="date_terminated desc, id desc", context=context)
#         location_id = move and move[0].location_id or False
#         return location_id
# 
#     def get_patient_current_location_id(self, cr, uid, patient_id, context=None):
#         res = self.get_patient_current_location_browse(cr, uid, patient_id, context)
#         res = res and res.id
#         return res

#     def get_patient_placement_location_browse(self, cr, uid, patient_id, context=None):
#         placement_pool = self.pool['t4.clinical.patient.placement']
#         placement_domain = [('patient_id','=',patient_id), ('state','=','completed')]
#         placement = placement_pool.browse_domain(cr, uid, placement_domain, limit=1, order="date_terminated desc, id desc", context=context)
#         placement = placement and placement[0]
#         res = placement and placement.location_id or False
#         return res    
#     
#     def get_patient_placement_location_id(self, cr, uid, patient_id, context=None):
#         res = self.get_patient_placement_location_browse(cr, uid, patient_id, context)
#         res = res and res.id
#         return res    
