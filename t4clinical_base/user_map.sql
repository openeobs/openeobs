select 
	u.id,
	array_agg(imd.name)
from res_users u
left join res_groups_users_rel gur on u.id = gur.uid
left join res_groups g on g.id = gur.gid
left join ir_model_data imd on imd.res_id = g.id and imd.model = 'res.groups'
left join t4_activity aa on aa.user_id = u.id -- assigned
left join activity_user_rel aur on aur.user_id = u.id
left join t4_activity ar on ar.user_id = u.id -- responsible
group by u.id