with pre_map as(
		
		select 
			u.id user_id,
			array_agg(imd.name::text) group_xmlids,
			array_agg(aa.id) assigned_activity_ids,
			array_agg(ra.id) responsible_activity_ids
		from res_users u
		left join res_groups_users_rel gur on u.id = gur.uid
		left join res_groups g on g.id = gur.gid
		left join ir_model_data imd on imd.res_id = g.id and imd.model = 'res.groups'
		left join t4_activity aa on aa.user_id = u.id -- assigned
		left join activity_user_rel aur on aur.user_id = u.id
		left join t4_activity ra on ra.user_id = u.id -- responsible
		group by u.id
),
map as(
	select 
		user_id,
		(select array_agg(g) from unnest(group_xmlids) g where g is not null) as group_xmlids,
		(select array_agg(aa) from unnest(assigned_activity_ids) aa where aa is not null) as assigned_activity_ids,
		(select array_agg(ra) from unnest(responsible_activity_ids) ra where ra is not null) as responsible_activity_ids
	from pre_map
)
select * from map 
where group_xmlids && array['group_t4clinical_nurse']