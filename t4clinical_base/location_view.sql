explain 
with
move_patient_date as (
    select 
        max(date_terminated) as max_date_terminated,
        max(termination_seq) as max_termination_seq,
        m.patient_id
    from t4_clinical_patient_move m
    inner join t4_activity a on m.activity_id = a.id
    where a.state = 'completed'
    group by m.patient_id
),

patient_per_location as (
    select 
        m.location_id,
        count(m.patient_id) as patient_qty,
        array_agg(mpd.patient_id) as patient_ids
    from t4_clinical_patient_move m
    inner join t4_activity ma on m.activity_id = ma.id
    inner join move_patient_date mpd on m.patient_id = mpd.patient_id
                                        and ma.termination_seq = mpd.max_termination_seq
    inner join t4_activity sa on sa.data_model='t4.clinical.spell' and m.patient_id = sa.patient_id
    --left join t4_activity a on a.location_id 
    where sa.state = 'started'
        group by m.location_id
),

activity as (
	select 
		location_id,
		array_agg(id) as ids
	from t4_activity
	where location_id is not null
	group by location_id
),

map as (
    select 
        l.id as location_id,
        l.code,
        l.type,
        l.usage,
        l.pos_id,
        coalesce(ppl.patient_qty, 0) as occupied,
        coalesce(l.patient_capacity, 0) as capacity,
        coalesce(l.patient_capacity, 0) - coalesce(ppl.patient_qty, 0) as available,
        ppl.patient_ids as _patient_ids,
        a.ids as _activity_ids
    from t4_clinical_location l
    left join patient_per_location ppl on l.id = ppl.location_id
	left join activity a on l.id = a.location_id
)
    
select * from map