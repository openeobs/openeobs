with
    move_patient_date as (
        select 
            max(date_terminated) as max_date_terminated,
            m.patient_id
        from t4_clinical_patient_move m
        inner join t4_activity a on m.activity_id = a.id
        where a.state = 'completed'
        group by m.patient_id
    ),
    patient_location as (
        select distinct
            m.patient_id,
            m.location_id,
            l.pos_id
        from t4_clinical_patient_move m
        inner join t4_clinical_location l on l.id = m.location_id
        inner join t4_activity ma on m.activity_id = ma.id
        inner join move_patient_date ppd on ma.date_terminated = ppd.max_date_terminated and m.patient_id = ppd.patient_id
        inner join t4_activity sa on ma.parent_id = sa.id
        where sa.state = 'started'
    )
select * from patient_location