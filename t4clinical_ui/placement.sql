select
    activity.id as id,
    activity.id as activity_id,
    activity.location_id as location_id,
    activity.patient_id as patient_id,
    activity.pos_id as pos_id,
    patient.other_identifier as hospital_number
from t4_activity activity
inner join t4_clinical_patient patient on activity.patient_id = patient.id
where activity.data_model = 't4.clinical.patient.placement' and activity.state not in ('completed','cancelled')