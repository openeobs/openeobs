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
			rank() over(partition by patient_id order by termination_seq desc),
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
			patient.patient_identifier,
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
select * from map
order by id