        select 
            m.patient_id,
            m.location_id,
            a.termination_seq,
            l.code,
            a.date_terminated
        from t4_activity a
        inner join t4_clinical_location l on l.id = a.location_id
        inner join t4_clinical_patient p on p.id = a.patient_id
        inner join t4_clinical_patient_move m on m.activity_id = a.id
        where data_model = 't4.clinical.patient.move'
        order by patient_id, termination_seq desc