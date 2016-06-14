discharge_transfer_skeleton = """
SELECT
    activity.spell_id AS spell_id,
    array_agg(DISTINCT users.id) AS user_ids,
    array_agg(DISTINCT users2.id) AS ward_user_ids
FROM wb_spell_ranked activity
INNER JOIN wb_{table}_ranked {table}
    ON {table}.parent_id = activity.id
    AND {table}.rank = 1 AND {table}.state = 'completed'
INNER JOIN nh_clinical_patient_{table} {table}_data
    ON {table}_data.id = {table}.data_id
INNER JOIN nh_clinical_location location
    ON location.id = {table}_data.{location_row}
INNER JOIN ward_locations wl ON wl.id = location.id
LEFT JOIN user_location_rel ulrel ON ulrel.location_id = location.id
LEFT JOIN res_users users ON users.id = ulrel.user_id
LEFT JOIN user_location_rel ulrel2 ON ulrel2.location_id = wl.ward_id
LEFT JOIN res_users users2 ON users2.id = ulrel2.user_id
WHERE now() AT TIME ZONE 'UTC' - {table}.date_terminated < INTERVAL '{time}'
AND activity.rank = 1 AND activity.state = '{state}'
GROUP BY activity.spell_id
"""

wardboard_skeleton = """
SELECT DISTINCT
    spell.id AS id,
    spell.patient_id AS patient_id,
    spell_activity.id AS spell_activity_id,
    spell_activity.date_started AS spell_date_started,
    spell_activity.date_terminated AS spell_date_terminated,
    spell.pos_id,
    spell.code AS spell_code,
    spell_activity.state AS spell_state,
    CASE
        WHEN extract(days FROM justify_hours(now() AT TIME ZONE 'UTC'
            - spell_activity.date_started)) > 0 THEN extract(days FROM
            justify_hours(now() AT TIME ZONE 'UTC' -
            spell_activity.date_started)) || ' day(s) '
        ELSE ''
    END || to_char(justify_hours(now() AT TIME ZONE 'UTC' -
        spell_activity.date_started), 'HH24:MI') time_since_admission,
    spell.move_date,
    patient.family_name,
    patient.given_name,
    patient.middle_names,
    CASE
        WHEN patient.given_name IS NULL THEN ''
        ELSE upper(substring(patient.given_name FROM 1 FOR 1))
    END AS initial,
    coalesce(patient.family_name, '') || ', ' ||
        coalesce(patient.given_name, '') || ' ' ||
        coalesce(patient.middle_names,'') AS full_name,
    location.name AS location,
    location.id AS location_id,
    wlocation.ward_id AS ward_id,
    patient.sex,
    patient.dob,
    patient.other_identifier AS hospital_number,
    CASE char_length(patient.patient_identifier) = 10
        WHEN TRUE THEN substring(patient.patient_identifier FROM 1 FOR 3)
            || ' ' || substring(patient.patient_identifier FROM 4 FOR 3) ||
            ' ' || substring(patient.patient_identifier FROM 7 FOR 4)
        ELSE patient.patient_identifier
    END AS nhs_number,
    extract(year FROM age(now(), patient.dob)) AS age,
    ews0.next_diff_polarity ||
    CASE
        WHEN ews0.date_scheduled IS NOT NULL THEN
          CASE WHEN extract(days FROM (greatest(now() AT TIME ZONE 'UTC',
            ews0.date_scheduled) - least(now() AT TIME ZONE 'UTC',
            ews0.date_scheduled))) > 0
            THEN extract(days FROM (greatest(now() AT TIME ZONE 'UTC',
                ews0.date_scheduled) - least(now() AT TIME ZONE 'UTC',
                ews0.date_scheduled))) || ' day(s) '
            ELSE '' END ||
          to_char(justify_hours(greatest(now() AT TIME ZONE 'UTC',
            ews0.date_scheduled) - least(now() AT TIME ZONE 'UTC',
            ews0.date_scheduled)), 'HH24:MI') || ' hours'
        ELSE to_char((INTERVAL '0s'), 'HH24:MI')
    END AS next_diff,
    CASE ews0.frequency < 60
        WHEN true THEN ews0.frequency || ' min(s)'
        ELSE ews0.frequency/60 || ' hour(s) ' || ews0.frequency -
            ews0.frequency/60*60 || ' min(s)'
    END AS frequency,
    ews0.date_scheduled,
    CASE WHEN ews1.id IS NULL THEN 'none' ELSE ews1.score::text END
        AS ews_score_string,
    ews1.score AS ews_score,
    CASE
        WHEN ews1.id IS NOT NULL AND ews2.id IS NOT NULL
            AND (ews1.score - ews2.score) = 0 THEN 'same'
        WHEN ews1.id IS NOT NULL AND ews2.id IS NOT NULL
            AND (ews1.score - ews2.score) > 0 THEN 'up'
        WHEN ews1.id IS NOT NULL AND ews2.id IS NOT NULL
            AND (ews1.score - ews2.score) < 0 THEN 'down'
        WHEN ews1.id IS NULL AND ews2.id IS NULL THEN 'none'
        WHEN ews1.id IS NOT NULL AND ews2.id IS NULL THEN 'first'
        WHEN ews1.id IS NULL AND ews2.id IS NOT NULL THEN 'no latest'
    END AS ews_trend_string,
    CASE WHEN ews1.id IS NULL THEN 'NoScore' ELSE ews1.clinical_risk END
        AS clinical_risk,
    ews1.score - ews2.score AS ews_trend,
    param.height,
    param.o2target_level_id AS o2target,
    CASE WHEN param.mrsa THEN 'yes' ELSE 'no' END AS mrsa,
    CASE WHEN param.diabetes THEN 'yes' ELSE 'no' END AS diabetes,
    CASE WHEN pbp.status THEN 'yes' ELSE 'no' END AS pbp_monitoring,
    CASE WHEN weight.status THEN 'yes' ELSE 'no' END AS weight_monitoring,
    CASE WHEN param.status THEN 'yes' ELSE 'no' END AS palliative_care,
    CASE
        WHEN param.post_surgery AND param.post_surgery_date > now() -
            INTERVAL '4h' THEN 'yes'
        ELSE 'no'
    END AS post_surgery,
    CASE
        WHEN param.critical_care AND param.critical_care_date > now() -
            INTERVAL '24h' THEN 'yes'
        ELSE 'no'
    END AS critical_care,
    param.uotarget_vol,
    param.uotarget_unit,
    consulting_doctors.names AS consultant_names,
    CASE
        WHEN spell_activity.date_terminated > now() - INTERVAL '{time}'
            AND spell_activity.state = 'completed' THEN true
        ELSE false
    END AS recently_discharged

FROM nh_clinical_spell spell
INNER JOIN nh_activity spell_activity
    ON spell_activity.id = spell.activity_id
INNER JOIN nh_clinical_patient patient ON spell.patient_id = patient.id
LEFT JOIN nh_clinical_location location ON location.id = spell.location_id
LEFT JOIN ews1 ON spell.id = ews1.spell_id
LEFT JOIN ews2 ON spell.id = ews2.spell_id
LEFT JOIN ews0 ON spell.id = ews0.spell_id
LEFT JOIN ward_locations wlocation ON wlocation.id = location.id
LEFT JOIN consulting_doctors ON consulting_doctors.spell_id = spell.id
LEFT JOIN weight ON weight.spell_id = spell.id
LEFT JOIN pbp pbp ON pbp.spell_id = spell.id
LEFT JOIN param ON param.spell_id = spell.id
ORDER BY location.name
"""


def get_discharge_transfer_sql(table, location_row, interval, state):
    return discharge_transfer_skeleton.format(
        table=table, location_row=location_row, time=interval, state=state)


def get_last_discharge_users(interval):
    return get_discharge_transfer_sql(
        table='discharge', location_row='location_id', interval=interval,
        state='completed')


def get_last_transfer_users(interval):
    return get_discharge_transfer_sql(
        table='transfer', location_row='origin_loc_id', interval=interval,
        state='started')


def get_wardboard(interval):
    return wardboard_skeleton.format(time=interval)
