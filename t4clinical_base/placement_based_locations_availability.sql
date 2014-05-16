with
	placement_patient_date as (
		select 
			max(date_terminated) as max_date_terminated,
			p.patient_id
		from t4_clinical_patient_placement p
		inner join t4_activity a on p.activity_id = a.id
		where a.state = 'completed'
		group by p.patient_id
	)

select 
	p.location_id,
	count(p.patient_id) as patient_qty
	
from t4_clinical_patient_placement p
inner join t4_activity pa on p.activity_id = pa.id
inner join placement_patient_date ppd on pa.date_terminated = ppd.max_date_terminated and p.patient_id = ppd.patient_id
inner join t4_activity sa on pa.parent_id = sa.id
where sa.state = 'started'
group by p.location_id