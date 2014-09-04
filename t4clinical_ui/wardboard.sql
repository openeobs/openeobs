drop view if exists t4_clinical_wardboard;
drop view if exists wb_activity_ranked;
drop view if exists wb_activity_latest;
drop view if exists wb_activity_data;
create or replace view 
-- activity per spell, data_model, state
wb_activity_ranked as(
        select 
            spell.id as spell_id,
			activity.*,
			split_part(activity.data_ref, ',', 2)::int as data_id,
            rank() over (partition by spell.id, activity.data_model, activity.state order by activity.sequence desc)
        from t4_clinical_spell spell
        inner join t4_activity activity on activity.patient_id = spell.patient_id
);

create or replace view 
wb_activity_latest as(
	with 
	max_sequence as(
        select 
            spell.id as spell_id,
			activity.data_model,
			activity.state,
			max(activity.sequence) as sequence
        from t4_clinical_spell spell
        inner join t4_activity activity on activity.patient_id = spell.patient_id
        group by spell_id, activity.data_model, activity.state
    )
    select 
    	max_sequence.spell_id,
    	activity.state,
    	activity.data_model,
    	activity.id
    from t4_activity activity
    inner join max_sequence on max_sequence.data_model = activity.data_model
    	 and max_sequence.state = activity.state
    	 and max_sequence.sequence = activity.sequence
);

create or replace view 
-- activity data ids per spell/pateint_id, data_model, state
wb_activity_data as(
        select 
            spell.id as spell_id,
            spell.patient_id,
            activity.data_model, 
            activity.state,
			array_agg(split_part(activity.data_ref, ',', 2)::int) as ids
        from t4_clinical_spell spell
        inner join t4_activity activity on activity.patient_id = spell.patient_id
        group by spell_id, spell.patient_id, activity.data_model, activity.state
); 


create or replace view
t4_clinical_wardboard as(
	with 
	ews as(
	        select 
	        	activity.patient_id,
	            activity.spell_id,
	            activity.state, 
	            activity.date_scheduled,
	        	ews.id,
	        	ews.score,
	            ews.frequency,
	            ews.clinical_risk,
	            case when activity.date_scheduled >= now() then '' else 'overdue: ' end as next_diff_polarity,
	            case activity.date_scheduled is null
	                when false then justify_hours(greatest(now(),activity.date_scheduled) - least(now(),activity.date_scheduled)) 
	                else interval '0s' 
	            end as next_diff_interval,
	            activity.rank
	        from wb_activity_ranked activity
	        inner join t4_clinical_patient_observation_ews ews on activity.data_id = ews.id 
	        	and activity.data_model = 't4.clinical.patient.observation.ews'
	),	
	cosulting_doctors as(
	        select 
	            spell.id as spell_id,
	            array_to_string(array_agg(doctor.name), ' / ') as names    
	        from t4_clinical_spell spell
	        inner join con_doctor_spell_rel on con_doctor_spell_rel.spell_id = spell.id
	        inner join res_partner doctor on con_doctor_spell_rel.doctor_id = doctor.id
	        group by spell.id
	        ),
	        
	param as(
			select distinct on (activity.spell_id)
				activity.spell_id,
				mrsa.mrsa,
				diabetes.diabetes,
				pbpm.pbp_monitoring,
				wm.weight_monitoring,
				height.height,
				o2target_level.id as o2target_level_id
			from wb_activity_latest activity
			left join t4_clinical_patient_mrsa mrsa on activity.id = mrsa.activity_id and activity.state = 'completed' and activity.data_model ilike '%mrsa%'
			left join t4_clinical_patient_diabetes diabetes on activity.id = diabetes.activity_id and activity.state = 'completed' and activity.data_model ilike '%diabetes%'
			left join t4_clinical_patient_pbp_monitoring pbpm on activity.id = pbpm.activity_id and activity.state = 'completed' and activity.data_model ilike '%pbp_monitoring%'
			left join t4_clinical_patient_weight_monitoring wm on activity.id = wm.activity_id and activity.state = 'completed' and activity.data_model ilike '%weight_monitoring%'
			left join t4_clinical_patient_observation_height height on activity.id = height.activity_id and activity.state = 'completed' and activity.data_model ilike '%observation.height%'
			left join t4_clinical_patient_o2target o2target on activity.id = o2target.activity_id and activity.state = 'completed' and activity.data_model ilike '%o2target%'
			left join t4_clinical_o2level o2target_level on o2target_level.id = o2target.level_id	
			)
	
	select 
	    spell.id as id,
	    spell.patient_id as patient_id,
	    spell_activity.id as spell_activity_id,
	    spell_activity.date_started as spell_date_started,
	    spell_activity.date_terminated as spell_date_terminated,
	    spell.pos_id,
	    spell.code as spell_code,
	    patient.family_name,
	    patient.given_name,
	    patient.middle_names,
	    coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
	    location.code as location,
	    location.id as location_id,
	    location.parent_id as ward_id,
	    patient.sex,
	    patient.dob,
	    patient.other_identifier as hospital_number,
	    patient.patient_identifier as nhs_number,
	    extract(year from age(now(), patient.dob)) as age,
	    case
	        when extract(day from ews0.next_diff_interval) = 0 then ews0.next_diff_polarity || to_char(ews0.next_diff_interval, 'HH24:MI')
	        else ews0.next_diff_polarity || extract(day from ews0.next_diff_interval) || ' day(s) ' || to_char(ews0.next_diff_interval, 'HH24:MI')
	    end as next_diff,
	    case ews0.frequency < 60
	        when true then ews0.frequency || ' min(s)'
	        else ews0.frequency/60 || ' hour(s) ' || ews0.frequency - ews0.frequency/60*60 || ' min(s)'
	    end as frequency,
	    case when ews1.id is null then 'none' else ews1.score::text end as ews_score_string,    
	    ews1.score as ews_score,
	    case
	        when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) = 0 then 'same'
	        when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) > 0 then 'down'
	        when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) < 0 then 'up'
	        when ews1.id is null and ews2.id is null then 'none'
	        when ews1.id is not null and ews2.id is null then 'first'
	        when ews1.id is null and ews2.id is not null then 'no latest' -- shouldn't happen. 
	    end as ews_trend_string,
	    case when ews1.id is null then 'NoScore' else ews1.clinical_risk end as clinical_risk,
	    ews1.score - ews2.score as ews_trend,
	    param.height,
	    param.o2target_level_id as o2target,
	    case when param.mrsa then 'yes' else 'no' end as mrsa,
	    case when param.diabetes then 'yes' else 'no' end as diabetes,
	    case when param.pbp_monitoring then 'yes' else 'no' end as pbp_monitoring,
	    case when param.weight_monitoring then 'yes' else 'no' end as weight_monitoring,
	    cosulting_doctors.names as consultant_names
	    
	from t4_clinical_spell spell
	inner join t4_activity spell_activity on spell_activity.id = spell.activity_id
	inner join t4_clinical_patient patient on spell.patient_id = patient.id
	left join t4_clinical_location location on location.id = spell.location_id
	left join ews ews1 on spell.id = ews1.spell_id and ews1.rank = 1 and ews1.state = 'completed'
	left join ews ews2 on spell.id = ews2.spell_id and ews2.rank = 2 and ews1.state = 'completed'
	left join ews ews0 on spell.id = ews0.spell_id and ews0.rank = 1 and ews1.state = 'shceduled'	
	left join cosulting_doctors on cosulting_doctors.spell_id = spell.id
	inner join param on param.spell_id = spell.id

	where spell_activity.state = 'started'
);

select * from t4_clinical_wardboard;

