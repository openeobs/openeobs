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
        location_parents as (
            select 
            	id as location_id, 
            	('{'||path||'}')::int[] as ids 
            from route
            order by path
        ),
        activity_user as (
	        select
	        	activity_id,
	        	array_agg(user_id) as user_ids
	        from activity_user_rel
	        group by activity_id
	    ),
	    location_children as (
	    	select
	    		location.id as location_id,
	    		array_agg(location_parents.location_id) as child_ids
	    	from t4_clinical_location location
	    	left join location_parents on location_parents.ids && array[location.id]
	    	group by location.id
	    )
	    
	    select 
	    	activity_user.activity_id,
	    	activity.location_id,
	    	location_children.child_ids,
	    	activity_user.user_ids
	    from activity_user
	    left join t4_activity activity on activity.id = activity_user.activity_id
	    left join location_children on location_children.location_id = activity.location_id