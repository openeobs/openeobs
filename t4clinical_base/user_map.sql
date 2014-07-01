--with pre_map as(
--		
--		select 
--			u.id user_id,
--			array_agg(imd.name::text) group_xmlids,
--			array_agg(aa.id) assigned_activity_ids,
--			array_agg(ra.id) responsible_activity_ids
--		from res_users u
--		left join res_groups_users_rel gur on u.id = gur.uid
--		left join res_groups g on g.id = gur.gid
--		left join ir_model_data imd on imd.res_id = g.id and imd.model = 'res.groups'
--		left join t4_activity aa on aa.user_id = u.id -- assigned
--		left join activity_user_rel aur on aur.user_id = u.id
--		left join t4_activity ra on ra.user_id = u.id -- responsible
--		group by u.id
--),
--map as(
--	select 
--		user_id,
--		(select array_agg(g) from unnest(group_xmlids) g where g is not null) as group_xmlids,
--		(select array_agg(aa) from unnest(assigned_activity_ids) aa where aa is not null) as assigned_activity_ids,
--		(select array_agg(ra) from unnest(responsible_activity_ids) ra where ra is not null) as responsible_activity_ids
--	from pre_map
--)
--select * from map 
--where group_xmlids && array['group_t4clinical_nurse']

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
)
select 
    u.id user_id,
    u.login,
    g.group_xmlids,
    aa.assigned_activity_ids
from res_users u
left join groups g on g.user_id = u.id
left join assigned_activity aa on aa.user_id = u.id