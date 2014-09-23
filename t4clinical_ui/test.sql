
-- iso-user
--select
--	ulr.user_id,
--	array_agg(activity.id) as activity_ids
--from user_location_rel ulr
--inner join res_groups_users_rel gur on ulr.user_id = gur.uid
--inner join ir_model_access access on access.group_id = gur.gid and access.perm_responsibility = true
--inner join ir_model model on model.id = access.model_id
--inner join t4_activity activity on model.model = activity.data_model and activity.location_id = ulr.location_id
--group by ulr.user_id

-- iso-activity
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
	inner join t4_activity activity on model.model = activity.data_model and activity.location_id = ulr.location_id) data
group by activity_id

-- link-pairs
--delete from activity_user_rel where 1=1;
--insert into activity_user_rel
--select distinct on (activity.id, ulr.user_id)
--		activity.id as activity_id,
--		ulr.user_id
--from user_location_rel ulr
--inner join res_groups_users_rel gur on ulr.user_id = gur.uid
--inner join ir_model_access access on access.group_id = gur.gid and access.perm_responsibility = true
--inner join ir_model model on model.id = access.model_id
--inner join t4_activity activity on model.model = activity.data_model and activity.location_id = ulr.location_id

	





--    with 
--        recursive route(level, path, parent_id, id) as (
--                select 0, id::text, parent_id, id 
--                from t4_clinical_location 
--                where parent_id is null
--            union
--                select level + 1, path||','||location.id, location.parent_id, location.id 
--                from t4_clinical_location location 
--                join route on location.parent_id = route.id
--        ),
--        location_parents as (
--            select 
--            	id as location_id, 
--            	('{'||path||'}')::int[] as ids 
--            from route
--            order by path
--        ),
--        user_access as (
--	        select
--	        	u.id as user_id,
--	        	array_agg(access.model_id) as model_ids -- can be responsible for
--	        from res_users u
--	        inner join res_groups_users_rel gur on u.id = gur.uid
--
--	        inner join ir_model_access access on access.group_id = gur.gid and access.perm_responsibility = true
--	        group by u.id
--	    ),
--	    
--	    user_location as (
--	    	select
--	    		ulr.user_id,
--	    		array_agg(ulr.location_id) as location_ids
--	    	from user_location_rel ulr
--	    	group by ulr.user_id
--	    ),
--	    
--	   user_location_parents_map as (
--		   select distinct
--		   		user_location.user_id,
--		   		parent_location_id
--		   from user_location
--		   inner join location_parents on user_location.location_ids && array[location_parents.location_id]
--		   inner join unnest(location_parents.ids) as parent_location_id on array[parent_location_id] && location_parents.ids
--	   ),
--	   user_location_parents as (
--	   		select
--	   			user_id,
--	    		array_agg(parent_location_id) as ids
--	    	from user_location_parents_map
--	    	group by user_id
--	    ),
--	    user_activity as (
--	        select
--	        	user_location.user_id,
--	        	array_agg(activity.id) as activity_ids
--	        from user_location
--	        inner join user_access on user_location.user_id = user_access.user_id
--	        inner join t4_activity activity on array[activity.location_id] && user_location.location_ids
--	        inner join ir_model model on model.model = activity.data_model and array[model.id] && user_access.model_ids
--
--	        group by user_location.user_id	    	
--	    ),
--	    user_parent_location_activity as(
--	    	select
--	    		user_location_parents.user_id,
--	    		array_agg(activity.id) as ids
--	    	from user_location_parents
--	    	inner join user_location on user_location_parents.user_id = user_location.user_id
--	    	inner join t4_activity activity on ((array[activity.location_id] && user_location_parents.ids
--	    		and not strpos(activity.data_model, 'notification')::boolean
--	    		and not strpos(activity.data_model, 'observation')::boolean)
--	    		or
--	    		array[activity.location_id] && user_location.location_ids)
--	    	group by user_location_parents.user_id
--	    )
--	    
--select
--	user_access.user_id,
--	user_location.location_ids,
--	user_location_parents.ids as parent_location_ids,
--	user_activity.activity_ids,
--	user_parent_location_activity.ids as parent_location_activity_ids
--from user_access
--inner join user_location on user_location.user_id = user_access.user_id
--inner join user_activity on user_activity.user_id = user_access.user_id
--inner join user_location_parents on user_location_parents.user_id = user_access.user_id
--inner join user_parent_location_activity on user_parent_location_activity.user_id = user_access.user_id
