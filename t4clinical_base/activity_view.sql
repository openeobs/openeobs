with 
activity as (
	select 
		--*,
		-- Dates
		date_deadline,
		case 
			when date_deadline is null then null
			else greatest(date_deadline, now() at time zone 'UTC') - least(date_deadline, now() at time zone 'UTC') 
		end as _interval_deadline_now,
		date_expiry,		
		case 
			when date_expiry is null then null
			else greatest(date_expiry, now() at time zone 'UTC') - least(date_expiry, now() at time zone 'UTC') 
		end as _interval_expiry_now,
		-- Ranks
		rank() over (partition by patient_id order by termination_seq desc) as _rank_termination_by_patient
		-- 
		
		
	from t4_activity
	where data_model = 't4.clinical.patient.observation.ews'
)

select * from activity