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
			ews.frequency,
			case when activity.date_scheduled >= now() then '' else 'overdue: ' end as next_diff_polarity,
			case activity.date_scheduled is null
				when false then justify_hours(greatest(now(),activity.date_scheduled) - least(now(),activity.date_scheduled)) 
				else interval '0s' 
			end as next_diff_interval,
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
completed_diabetes as(
		select
			diabetes.id,
			spell.patient_id,
			diabetes.diabetes,
			rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_diabetes diabetes on diabetes.patient_id = spell.patient_id
		inner join t4_activity activity on diabetes.activity_id = activity.id
		where activity.state = 'completed'
		),
completed_pbp_monitoring as(
		select
			pbpm.id,
			spell.patient_id,
			pbpm.pbp_monitoring,
			rank() over (partition by spell.patient_id order by activity.date_terminated desc, activity.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_pbp_monitoring pbpm on pbpm.patient_id = spell.patient_id
		inner join t4_activity activity on pbpm.activity_id = activity.id
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
			level.id,
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
	spell_activity.date_terminated as spell_date_terminated,
	spell.pos_id,
	spell.code as spell_code,
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
        when ews1.id is not null and ews2.id is null then 'first'
        when ews1.id is null and ews2.id is not null then 'no latest' -- shouldn't happen. 
    end as ews_trend_string,
    case
        when ews1.id is null then 'NoScore'
        else ews1.clinical_risk
    end as clinical_risk,
	ews1.score - ews2.score as ews_trend,
	height_ob.height,
	o2target_ob.id as o2target,
	case
	    when mrsa.mrsa then 'yes'
	    when mrsa.mrsa is null then 'no'
	    else 'no'
	end as mrsa,
	case
	    when diabetes.diabetes then 'yes'
	    when diabetes.diabetes is null then 'no'
	    else 'no'
	end as diabetes,
	case
	    when pbpm.pbp_monitoring then 'yes'
	    when pbpm.pbp_monitoring is null then 'no'
	    else 'no'
	end as pbp_monitoring,
	cosulting_doctors.names as consultant_names
from t4_clinical_spell spell
inner join t4_activity spell_activity on spell_activity.id = spell.activity_id
inner join t4_clinical_patient patient on spell.patient_id = patient.id
left join t4_clinical_location location on location.id = spell.location_id
left join completed_ews ews1 on spell.patient_id = ews1.patient_id and ews1.rank = 1
left join completed_ews ews2 on spell.patient_id = ews2.patient_id and ews2.rank = 2
left join scheduled_ews ews0 on spell.patient_id = ews0.patient_id and ews0.rank = 1
left join completed_mrsa mrsa on spell.patient_id = mrsa.patient_id and mrsa.rank = 1 
left join completed_diabetes diabetes on spell.patient_id = diabetes.patient_id and diabetes.rank = 1
left join completed_pbp_monitoring pbpm on spell.patient_id = pbpm.patient_id and pbpm.rank = 1
left join completed_height height_ob on spell.patient_id = height_ob.patient_id and height_ob.rank = 1
left join completed_o2target o2target_ob on spell.patient_id = o2target_ob.patient_id and o2target_ob.rank = 1
left join cosulting_doctors on cosulting_doctors.spell_id = spell.id
where spell_activity.state = 'started'