with 
activity as (
	select 
		id, 
		pos_id,
		location_id,
		patient_id,
		device_id,
		data_model,
		state  
	from t4_activity
),
ranked_activity as (
	select
		id,
		rank() over (partition by patient_id, state order by termination_seq) as rank  
	from t4_activity
)
select * from ranked_activity
