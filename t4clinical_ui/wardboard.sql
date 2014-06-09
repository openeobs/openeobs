with 
completed_ews as(
		select
			ews.id,
			spell.patient_id,
			ews.score,
			ews.clinical_risk,
			rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
		inner join t4_activity activity on ews.activity_id = activity.id
		where activity.state = 'completed'
		),
scheduled_ews as(
		select 
			spell.patient_id,
			activity.date_scheduled,
			ews.frequency
			rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
		inner join t4_activity activity on ews.activity_id = activity.id
		where activity.state = 'scheduled'
		),
completed_mrsa as(
		select
			mrsa.id,
			spell.patient_id,
			mrsa.mrsa,
			rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_mrsa mrsa on mrsa.patient_id = spell.patient_id
		inner join t4_activity activity on mrsa.activity_id = activity.id
		where activity.state = 'completed'
		),
completed_height as(
		select 
			spell.patient_id,
			height.height,
			rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
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
			rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_o2target o2target on o2target.patient_id = spell.patient_id
		inner join t4_activity activity on o2target.activity_id = activity.id
		inner join t4_clinical_o2level level on level.id = o2target.level_id
		where activity.state = 'completed'
		),
cosulting_doctors as(
		select 
			spell.id as spell_id,
			array_to_string(array_agg(doctor.name), ' / ') as names	
		from t4_clinical_spell spell
		inner join con_doctor_spell_rel on con_doctor_spell_rel.spell_id = spell.id
		inner join res_partner doctor on con_doctor_spell_rel.doctor_id = doctor.id
		group by spell.id
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
	location.parent_id as ward_id,
	patient.sex,
	patient.dob,
	extract(year from age(now(), patient.dob)) as age,
	case
		when extract('epoch' from (now() - ews0.date_scheduled)) > 0 then
			coalesce( nullif( extract('day' from (now() - ews0.date_scheduled))::text || ' day(s) ','0 day(s) '),'' ) ||
			to_char((now() - ews0.date_scheduled), 'HH24:MI')
		else
			'overdue: ' ||
			coalesce( nullif( extract('day' from (now() - ews0.date_scheduled))::text || ' day(s) ','0 day(s) '),'' ) ||
			to_char(now() - ews0.date_scheduled, 'HH24:MI')			
		end as next_diff,
	ews0.frequency as frequency,
	case
		when ews1.id is null then 'none'
		else ews1.score::text
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
    case
        when ews1.id is null then 'None'
        else ews1.clinical_risk
    end as clinical_risk,
	ews1.score - ews2.score as ews_trend,
	height_ob.height,
	o2target_ob.min as o2target_min,
	o2target_ob.max as o2target_max,
	o2target_ob.min::text || '-' || o2target_ob.max::text as o2target_string,
	mrsa.mrsa,
	cosulting_doctors.names as consultant_names
from t4_clinical_spell spell
inner join t4_activity spell_activity on spell_activity.id = spell.activity_id
inner join t4_clinical_patient patient on spell.patient_id = patient.id
left join t4_clinical_location location on location.id = spell.location_id
left join (select id, score, patient_id, rank, clinical_risk from completed_ews where rank = 1) ews1 on spell.patient_id = ews1.patient_id
left join (select id, score, patient_id, rank from completed_ews where rank = 2) ews2 on spell.patient_id = ews2.patient_id
left join (select date_scheduled, patient_id, frequency, rank from scheduled_ews where rank = 1) ews0 on spell.patient_id = ews0.patient_id
left join (select id, mrsa, patient_id, rank from completed_mrsa where rank = 1) mrsa on spell.patient_id = mrsa.patient_id
left join (select height, patient_id, rank from completed_height where rank = 1) height_ob on spell.patient_id = height_ob.patient_id
left join (select min, max, patient_id, rank from completed_o2target where rank = 1) o2target_ob on spell.patient_id = o2target_ob.patient_id
left join cosulting_doctors on cosulting_doctors.spell_id = spell.id
where spell_activity.state = 'started'