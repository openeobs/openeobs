with 
completed_ews as(
		select 
			spell.patient_id,
			ews.score,
			rank() over (partition by spell.patient_id order by task.date_terminated, task.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
		inner join t4_clinical_task task on ews.task_id = task.id
		where task.state = 'completed'
		),
scheduled_ews as(
		select 
			spell.patient_id,
			task.date_scheduled,
			rank() over (partition by spell.patient_id order by task.date_terminated, task.id desc)
		from t4_clinical_spell spell
		left join t4_clinical_patient_observation_ews ews on ews.patient_id = spell.patient_id
		inner join t4_clinical_task task on ews.task_id = task.id
		where task.state = 'scheduled'
		)		
select 
	spell.patient_id as id,
	coalesce(patient.family_name, '') || ', ' || coalesce(patient.given_name, '') || ' ' || coalesce(patient.middle_names,'') as full_name,
	location.code as location,
	patient.dob,
	extract(year from age(now(), patient.dob)) as age,
	patient.gender,
	patient.sex,
	patient.other_identifier,
	trigger.unit_qty,
	trigger.unit,
	ews0.date_scheduled,
	ews1.score as score1, 
	ews2.score as score2
from t4_clinical_spell spell
inner join t4_clinical_patient patient on spell.patient_id = patient.id
left join t4_clinical_location location on location.id = spell.location_id -- FIXME spell.location update on placement.complete
left join (select score, patient_id, rank from completed_ews where rank = 1) ews1 on spell.patient_id = ews1.patient_id
left join (select score, patient_id, rank from completed_ews where rank = 2) ews2 on spell.patient_id = ews2.patient_id
left join t4_clinical_patient_task_trigger trigger on trigger.patient_id = patient.id and data_model = 't4.clinical.patient.obsevation.ews'
left join (select date_scheduled, patient_id, rank from scheduled_ews where rank = 1) ews0 on spell.patient_id = ews0.patient_id