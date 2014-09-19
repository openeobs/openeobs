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
            location_user as (
                select
                    ulr.location_id,
                    array_agg(ulr.user_id) as user_ids
                from user_location_rel ulr
                group by ulr.location_id
            ),
            location_activity as (
                select
                    location_id,
                    array_agg(activity.id) as activity_ids
                from t4_activity activity
                group by location_id            
            )
            select 
                location_user.location_id,
                location_activity.activity_ids,
                location_user.user_ids,
                location_parents.ids as parent_ids
            from location_user
            inner join location_parents on location_parents.location_id = location_user.location_id
            inner join location_activity on location_activity.location_id = location_user.location_id