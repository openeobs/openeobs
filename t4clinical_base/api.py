# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID
from pprint import pprint as pp

import logging        
_logger = logging.getLogger(__name__)

    
class t4_clinical_api(orm.AbstractModel):
    _name = 't4.clinical.api'
    
    def get_activity(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        return activity_pool.browse(cr, uid, activity_id)
                
    def create_activity(self, cr, uid, data_model, vals_activity, vals_data):
        activity_pool = self.pool['t4.activity']
        data_pool = self.pool[data_model]        
        activity_id = data_pool.create_activity(cr, uid, vals_activity, vals_data)        
        return activity_pool.browse(cr, uid, activity_id)        

    def write_activity(self, cr, uid, activity_id, vals_activity):
        activity_pool = self.pool['t4.activity']
        activity_pool.write(cr, uid, activity_id, vals_activity)        
        return activity_pool.browse(cr, uid, activity_id) 

    def create_complete(self, cr, uid, data_model, activity_vals={}, data_vals={}):
        data_pool = self.pool[data_model]
        activity_pool = self.pool['t4.activity']
        activity_id = data_pool.create_activity(cr, uid, activity_vals, data_vals)
        activity_pool.complete(cr, uid, activity_id)       
        return activity_pool.browse(cr, uid, activity_id)

    def submit_complete(self, cr, uid, activity_id, data_vals={}):
        activity_pool = self.pool['t4.activity']
        activity_pool.submit(cr, uid, activity_id, data_vals)
        activity_pool.complete(cr, uid, activity_id)       
        return activity_pool.browse(cr, uid, activity_id)

    def schedule(self, cr, uid, activity_id, date_scheduled):
        activity_pool = self.pool['t4.activity']
        activity_pool.schedule(cr, uid, activity_id, date_scheduled)        
        return activity_pool.browse(cr, uid, activity_id)     
            
    def start(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity_pool.start(cr, uid, activity_id)        
        return activity_pool.browse(cr, uid, activity_id)       
    
    def complete(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity_pool.complete(cr, uid, activity_id)        
        return activity_pool.browse(cr, uid, activity_id) 
    
    def cancel(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity_pool.cancel(cr, uid, activity_id)        
        return activity_pool.browse(cr, uid, activity_id) 

    def submit(self, cr, uid, activity_id, vals_data):
        activity_pool = self.pool['t4.activity']
        activity_pool.submit(cr, uid, activity_id, vals_data)        
        return activity_pool.browse(cr, uid, activity_id) 
    
    def assign(self, cr, uid, activity_id, user_id):
        activity_pool = self.pool['t4.activity']
        activity_pool.assign(cr, uid, activity_id, user_id)        
        return activity_pool.browse(cr, uid, activity_id) 
    
    def unassign(self, cr, uid, activity_id):
        activity_pool = self.pool['t4.activity']
        activity_pool.unassign(cr, uid, activity_id)        
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

    def patient_map(self, cr, uid, ids=[], types=[], usages=[], codes=[]):  
        """
        returns:
        {patient_id: {location_id, ...}}
        """
        print "api: map args: ids: %s, available_range: %s, usages: %s" % (ids,available_range,usages)
        where_list = []
        ids and where_list.append("patient_id in (%s)" % ','.join([str(id) for id in ids]))
        types and where_list.append("type in ('%s')" % "','".join(types))
        usages and where_list.append("usage in ('%s')" % "','".join(usages))
        codes and where_list.append("code in ('%s')" % "','".join(codes))
        where_clause = where_list and "where %s" % " and ".join(where_list) or ""
        print where_clause     
        sql = """
            with
                move_patient_date as (
                    select 
                        max(date_terminated) as max_date_terminated,
                        m.patient_id
                    from t4_clinical_patient_move m
                    inner join t4_activity a on m.activity_id = a.id
                    where a.state = 'completed'
                    group by m.patient_id
                ),
                patient_location as (
                    select distinct
                        m.patient_id,
                        m.location_id
                    from t4_clinical_patient_move m
                    inner join t4_activity ma on m.activity_id = ma.id
                    inner join move_patient_date ppd on ma.date_terminated = ppd.max_date_terminated and m.patient_id = ppd.patient_id
                    inner join t4_activity sa on ma.parent_id = sa.id
                    where sa.state = 'started'
                )
            select * from patient_location %s """ % where_clause
        cr.execute(sql)
        res = {r['patient_id']: r['location_id'] for r in cr.dictfetchall()}
        return res
    
    def user_map(self, cr,uid, user_ids=[], group_xmlids=[], assigned_activity_ids=[]):
        """
        returns:
        {user_id: {group_xmlids, assigned_activity_ids, responsible_activity_ids}}
        """
        where_list = []
        if assigned_activity_ids: where_list.append("assigned_activity_ids in (%s)" % ','.join([str(id) for id in assigned_activity_ids]))
        if user_ids: where_list.append("user_id in (%s)" % ','.join([str(id) for id in user_ids]))
        if group_xmlids: where_list.append("group_xmlids && array['%s']" % "','".join(group_xmlids))
        where_clause = where_list and "where %s" % " and ".join(where_list) or ""       
        sql = """
            with pre_map as(
                    select 
                        u.id user_id,
                        u.login,
                        array_agg(imd.name::text) as group_xmlids,
                        array_agg(aa.id) as assigned_activity_ids,
                        array_agg(ra.id) as responsible_activity_ids
                    from res_users u
                    left join res_groups_users_rel gur on u.id = gur.uid
                    left join res_groups g on g.id = gur.gid
                    left join ir_model_data imd on imd.res_id = g.id and imd.model = 'res.groups'
                    left join t4_activity aa on aa.user_id = u.id -- assigned
                    left join activity_user_rel aur on aur.user_id = u.id
                    left join t4_activity ra on ra.user_id = u.id -- responsible
                    group by u.id, u.login
            ),
            map as(
                select 
                    user_id,
                    login,
                    (select array_agg(g) from unnest(group_xmlids) g where g is not null) as group_xmlids,
                    (select array_agg(aa) from unnest(assigned_activity_ids) aa where aa is not null) as assigned_activity_ids,
                    (select array_agg(ra) from unnest(responsible_activity_ids) ra where ra is not null) as responsible_activity_ids
                from pre_map
            )  
            select * from map
            {where_clause}
        """.format(where_clause=where_clause)
        cr.execute(sql)
        res = cr.dictfetchall()
        res = {r['user_id']: r for r in res}
        #pp(res)
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
                                  occupied_range=[], capacity_range=[], available_range=[]):
        location_ids = self.get_location_ids(cr, uid, pos_ids=pos_ids,
                                  location_ids=location_ids, types=types, usages=usages, codes=codes,
                                  occupied_range=occupied_range, capacity_range=capacity_range, 
                                  available_range=available_range)
        return self.pool['t4.clinical.location'].browse(cr, uid, location_ids)     

    def get_activity_ids(self, cr, uid, activity_ids=[],
                       pos_ids=[], location_ids=[], patient_ids=[],
                       device_ids=[], data_models=[], states=[]):
        """
        returns browse list of t4.activity 
        """
        where_list = []
        if activity_ids: where_list.append("id in (%s)" % ','.join([str(id) for id in activity_ids]))
        if pos_ids: where_list.append("pos_id in (%s)" % ','.join([str(id) for id in pos_ids]))    
        if location_ids: where_list.append("location_id in (%s)" % ','.join([str(id) for id in location_ids])) 
        if patient_ids: where_list.append("patient_id in (%s)" % ','.join([str(id) for id in patient_ids]))
        if device_ids: where_list.append("device_id in (%s)" % ','.join([str(id) for id in device_ids]))
        if data_models: where_list.append("data_model in ('%s')" % "','".join(data_models))
        if states: where_list.append("state in ('%s')" % "','".join(states))
        where_clause = where_list and "where %s" % " and ".join(where_list) or ""
        sql = "select id from t4_activity %s" % where_clause
        cr.execute(sql)
        activity_ids = [r['id'] for r in cr.dictfetchall()]
        return activity_ids
    
    def get_activities(self, cr, uid, activity_ids=[],
                       pos_ids=[], location_ids=[], patient_ids=[],
                       device_ids=[], data_models=[], states=[]):
        activity_ids = self.get_activity_ids(cr, uid, pos_ids=pos_ids, location_ids=location_ids, 
                                             patient_ids=patient_ids, device_ids=device_ids, 
                                             data_models=data_models, states=states)
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
                
#     def patient_route_map(self, cr, uid, patient_ids=[]):
#         """
#         {patient_id: [{location_id, termination_seq, location_code, date_terminated}, ... ]
#         """
#         where_list = []
#         if patient_ids: where_list.append("id in (%s)" % ','.join([str(id) for id in patient_ids]))          
#         where_clause = where_list and "where %s" % " and ".join(where_list) or ""
#         sql = """
#         select 
#             m.patient_id,
#             m.location_id,
#             a.termination_seq,
#             l.code,
#             a.date_terminated
#         from t4_activity a
#         inner join t4_clinical_location l on l.id = a.location_id
#         inner join t4_clinical_patient p on p.id = a.patient_id
#         inner join t4_clinical_patient_move m on m.activity_id = a.id
#         {where clause} and data_model = 't4.clinical.patient.move' 
#         """.format(where_clause=where_clause)
#         
#         # not finished. 
        
        
    def location_map(self, cr, uid, location_ids=[], types=[], usages=[], codes=[], pos_ids=[],
                                    patient_ids=[], 
                                    occupied_range=[], capacity_range=[], available_range=[]):  
        """
        returns dict of dicts for location model of format:
        {id: {id, code, type, usage, occupied, capacity, available}}
        """
        #print "api: map args: location_ids: %s, available_range: %s, usages: %s" % (location_ids,available_range,usages)
        where_list = []
        if location_ids: where_list.append("location_id in (%s)" % ','.join([str(id) for id in location_ids]))
        if patient_ids: where_list.append("patinet_ids && array[%s]" % ','.join([str(id) for id in patient_ids]))
        if pos_ids: where_list.append("pos_id in (%s)" % ','.join([str(id) for id in pos_ids]))
        if types: where_list.append("type in ('%s')" % "','".join([str(t) for t in types]))
        if usages: where_list.append("usage in ('%s')" % "','".join([str(u) for u in usages]))
        if codes: where_list.append("code in ('%s')" % "','".join([str(c) for c in codes]))                       
        if occupied_range: where_list.append("occupied between %s and %s" % (occupied_range[0], occupied_range[1]))
        if capacity_range: where_list.append("capacity between %s and %s" % (capacity_range[0], capacity_range[1]))
        if available_range: where_list.append("available between %s and %s" % (available_range[0], available_range[1]))
        where_clause = where_list and "where %s" % " and ".join(where_list) or ""
        #print where_clause     
        sql = """
            with
                move_patient_date as (
                    select 
                        max(date_terminated) as max_date_terminated,
                        max(termination_seq) as max_termination_seq,
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
                                                        and ma.termination_seq = mpd.max_termination_seq
                    inner join t4_activity sa on sa.data_model='t4.clinical.spell' and m.patient_id = sa.patient_id
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
                        coalesce(ppl.patient_qty, 0) as occupied,
                        coalesce(l.patient_capacity, 0) as capacity,
                        coalesce(l.patient_capacity, 0) - coalesce(ppl.patient_qty, 0) as available,
                        ppl.patient_ids
                    from t4_clinical_location l
                    left join patient_per_location ppl on l.id = ppl.location_id
                )
                
            select * from map %s """ % where_clause
        cr.execute(sql)
        res = {location['location_id']: location for location in cr.dictfetchall()}
        return res
        
    def get_not_palced_patient_ids(self, cr, uid, location_id=None, context=None):
        # all current patients
        spell_domain = [('state','=','started')]
        spell_pool = self.pool['t4.clinical.spell']
        spell_ids = spell_pool.search(cr, uid, spell_domain)
        spell_patient_ids = [s.patient_id.id for s in spell_pool.browse(cr, uid, spell_ids, context)]
        # placed current patients
        placement_domain = [('activity_id.parent_id.state','=','started'),('state','=','completed')]
        location_id and  placement_domain.append(('activity_id.location_id','child_of',location_id))
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_ids = placement_pool.search(cr, uid, placement_domain)
        placed_patient_ids = [p.patient_id.id for p in placement_pool.browse(cr, uid, placement_ids, context)]       
        patient_ids = set(spell_patient_ids) - set(placed_patient_ids)
        #import pdb; pdb.set_trace()
        return list(patient_ids)

    def get_patient_spell_activity_id(self, cr, uid, patient_id, pos_id=None, context=None):
        activity_pool = self.pool['t4.activity']
        domain = [('patient_id', '=', patient_id),
                  ('state', '=', 'started'),
                  ('data_model', '=', 't4.clinical.spell')]
        if pos_id:
            domain.append(('pos_id', '=', pos_id))
        spell_activity_id = activity_pool.search(cr, uid, domain, context=context)
        if not spell_activity_id:
            return False
        if len(spell_activity_id) > 1:
            _logger.warn("For patient_id=%s found more than 1 started spell_activity_ids: %s " % (patient_id, spell_activity_id))
        return spell_activity_id[0]

    def get_patient_last_spell_activity_id(self, cr, uid, patient_id, pos_id=None, context=None):
        activity_pool = self.pool['t4.activity']
        domain = [('patient_id', '=', patient_id),
                  ('state', '=', 'completed'),
                  ('data_model', '=', 't4.clinical.spell')]
        if pos_id:
            domain.append(('pos_id', '=', pos_id))
        spell_activity_id = activity_pool.search(cr, uid, domain, order='date_terminated desc', context=context)
        if not spell_activity_id:
            return False
        return spell_activity_id[0]

    def get_patient_spell_activity_browse(self, cr, uid, patient_id, pos_id=None, context=None):
        spell_activity_id = self.get_patient_spell_activity_id(cr, uid, patient_id, pos_id, context)
        if not spell_activity_id:
            return False
        return self.pool['t4.activity'].browse(cr, uid, spell_activity_id, context)
    
    def get_device_session_activity_id(self, cr, uid, device_id, context=None):
        activity_pool = self.pool['t4.activity']
        domain = [('device_id', '=', device_id),
                  ('state', '=', 'started'),
                  ('data_model', '=', 't4.clinical.device.session')]
        session_activity_id = activity_pool.search(cr, uid, domain)
        if not session_activity_id:
            return False
        if len(session_activity_id) > 1:
            _logger.warn("For device_id=%s found more than 1 started device session activity_ids: %s " 
                         % (device_id, session_activity_id))
        return session_activity_id[0]

    def get_patient_current_location_browse(self, cr, uid, patient_id, context=None):
        move_pool = self.pool['t4.clinical.patient.move']
        move_domain = [('patient_id','=',patient_id), ('state','=','completed')]
        # sort parameter includes 'id' to resolve situation with equal values in 'date_terminated'
        move = move_pool.browse_domain(cr, uid, move_domain, limit=1, order="date_terminated desc, id desc", context=context)
        location_id = move and move[0].location_id or False
        return location_id

    def get_patient_current_location_id(self, cr, uid, patient_id, context=None):
        res = self.get_patient_current_location_browse(cr, uid, patient_id, context)
        res = res and res.id
        return res

    def get_patient_placement_location_browse(self, cr, uid, patient_id, context=None):
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_domain = [('patient_id','=',patient_id), ('state','=','completed')]
        placement = placement_pool.browse_domain(cr, uid, placement_domain, limit=1, order="date_terminated desc, id desc", context=context)
        placement = placement and placement[0]
        res = placement and placement.location_id or False
        return res    
    
    def get_patient_placement_location_id(self, cr, uid, patient_id, context=None):
        res = self.get_patient_placement_location_browse(cr, uid, patient_id, context)
        res = res and res.id
        return res    


class t4_clinical_api_adt(orm.AbstractModel):
    _name = 't4.clinical.api.adt'

    
class t4_clinical_api_frontend(orm.AbstractModel):
    _name = 't4.clinical.api.frontend'