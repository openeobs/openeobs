--drop view if exists user_activity_locations;
--create or replace view 
--activity_user_locations as(
    with 
        recursive t(level,path,parent_id,id) as (
                select 0,id::text,parent_id,id 
                from t4_clinical_location 
                where parent_id is null
            union
                select level + 1, path||','||location.id, location.parent_id, location.id 
                from t4_clinical_location location 
                join t on location.parent_id = t.id
        ),
        location as (
            select id, ('{'||path||'}')::int[] as parent_ids 
            from t 
            order by path
        )
	select distinct on (user_id, location.id) 
		location.id as location_id,
		location.parent_ids as parent_location_ids,
		activity.id as activity_id,
		ulr.user_id
	from location
	inner join t4_activity activity on activity.location_id = location.id
	inner join user_location_rel ulr on array[ulr.location_id] && location.parent_ids
--);	

--			delete from activity_user_rel where activity_id in (select activity_id from user_activity_locations)

--        	insert into activity_user_rel select activity_id, user_id from user_activity_locations