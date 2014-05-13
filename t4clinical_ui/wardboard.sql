with 
completed_ews as(
		select
			ews.id,
			spell.patient_id,
			ews.score,
			rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
		inner join t4_activity activity on ews.activity_id = activity.id
		where activity.state = 'completed'
		),
scheduled_ews as(
		select 
			spell.patient_id,
			activity.date_scheduled,
			rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
		inner join t4_activity activity on ews.activity_id = activity.id
		where activity.state = 'scheduled'
		),
completed_height as(
		select 
			spell.patient_id,
			height.height,
			rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_observation_height height on height.patient_id = spell.patient_id
		inner join t4_activity activity on height.activity_id = activity.id
		where activity.state = 'completed'
		),
completed_o2target as(
		select 
			spell.patient_id,
			level.min,
			level.max,
			rank() over (partition by spell.patient_id order by activity.date_terminated, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_o2target o2target on o2target.patient_id = spell.patient_id
		inner join t4_activity activity on o2target.activity_id = activity.id
		inner join t4_clinical_o2level level on level.id = o2target.level_id
		where activity.state = 'completed'
		)
select 
	spell.patient_id as id,
	spell.patient_id as patient_id,
	spell_activity.id as spell_activity_id,
	spell_activity.date_started as spell_date_started,	
	spell.pos_id,
	spell.code as spell_code,
	coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
	location.code as location,
	location.id as location_id,
	patient.sex,
	patient.dob,
	extract(year from age(now(), patient.dob)) as age,
	(now() - ews0.date_scheduled)::text as next_diff, 
	spell.ews_frequency as frequency,
	case
		when ews1.id is null then 'none'
		else ews1.id::text
    end as ews_score_string,	
	ews1.score as ews_score,
	case
		when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) = 0 then 'same'
        when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) > 0 then 'down'
        when ews1.id is not null and ews2.id is not null and (ews1.score - ews2.score) < 0 then 'up'
        when ews1.id is null and ews2.id is null then 'none'
        when ews1.id is not null and ews2.id is null then 'one'
        when ews1.id is null and ews2.id is not null then 'one' -- shouldn't happen. 
    end as ews_trend_string,
	ews1.score - ews2.score as ews_trend,
	height_ob.height,
	o2target_ob.min as o2target_min,
	o2target_ob.max as o2target_max,
	o2target_ob.min::text || '-' || o2target_ob.max::text as o2target_string
from t4_clinical_spell spell
inner join t4_activity spell_activity on spell_activity.id = spell.activity_id
inner join t4_clinical_patient patient on spell.patient_id = patient.id
left join t4_clinical_location location on location.id = spell.location_id
left join (select id, score, patient_id, rank from completed_ews where rank = 1) ews1 on spell.patient_id = ews1.patient_id
left join (select id, score, patient_id, rank from completed_ews where rank = 2) ews2 on spell.patient_id = ews2.patient_id
left join (select date_scheduled, patient_id, rank from scheduled_ews where rank = 1) ews0 on spell.patient_id = ews0.patient_id
left join (select height, patient_id, rank from completed_height where rank = 1) height_ob on spell.patient_id = height_ob.patient_id
left join (select min, max, patient_id, rank from completed_o2target where rank = 1) o2target_ob on spell.patient_id = o2target_ob.patient_id

where spell_activity.state = 'started'