--with
--	move_patient_date as (
--		select 
--			max(date_terminated) as max_date_terminated,
--			m.patient_id
--		from t4_clinical_patient_move m
--		inner join t4_activity a on m.activity_id = a.id
--		where a.state = 'completed'
--		group by m.patient_id
--	),
--	patient_per_location as (
--		select 
--			m.location_id,
--			count(m.patient_id) as patient_qty
--			
--		from t4_clinical_patient_move m
--		inner join t4_activity ma on m.activity_id = ma.id
--		inner join move_patient_date ppd on ma.date_terminated = ppd.max_date_terminated and m.patient_id = ppd.patient_id
--		inner join t4_activity sa on ma.parent_id = sa.id
--		where sa.state = 'started'
--		group by m.location_id
--	),
--	avalibility_map as (
--		select 
--			l.id,
--			l.code,
--			l.type,
--			l.usage,
--			coalesce(ppl.patient_qty, 0) as occupied,
--			coalesce(l.patient_capacity, 0) as capacity,
--			coalesce(l.patient_capacity, 0) - coalesce(ppl.patient_qty, 0) as available
--		from t4_clinical_location l
--		left join patient_per_location ppl on l.id = ppl.location_id
--	)
--	
--select * from avalibility_map

select distinct m.location_id from t4_activity a
inner join t4_clinical_patient_move m on a.data_model = 't4.clinical.patient.move' and m.activity_id = a.id
where a.state = 'completed'
	