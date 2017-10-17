from openerp.osv import orm
import re


class NHEobsSQL(orm.AbstractModel):

    _name = 'nh.clinical.sql'

    WORKLOAD_BUCKET_EXTRACT = \
        r'^(\d+)[-|+]{1}(\d+)?\sminutes\s([late|remain]+)$'

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
    WHERE now() AT TIME ZONE 'UTC' - {table}.date_terminated <
      INTERVAL '{time}'
    AND activity.rank = 1 AND activity.state = '{state}'
    GROUP BY activity.spell_id"""

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
    LEFT JOIN pbp pbp ON pbp.spell_id = spell.id
    LEFT JOIN param ON param.spell_id = spell.id
    ORDER BY location.name"""

    workload_skeleton = """
    WITH activity AS (
        SELECT
            activity.id AS id,
            spell.id AS activity_id,
            extract (EPOCH FROM (coalesce(activity.date_scheduled,
                activity.date_deadline) - now() AT TIME ZONE 'UTC'))::INT/60
            AS proximity,
            activity.summary AS summary,
            activity.state AS state,
            activity.user_id AS user_id,
            coalesce(activity.date_scheduled,
                activity.date_deadline) AS date_scheduled,
            activity.data_model AS data_model,
            patient.other_identifier AS patient_other_id,
            patient.patient_identifier AS nhs_number,
            patient.family_name AS family_name,
            CASE
                WHEN patient.given_name IS NULL THEN ''
                ELSE upper(substring(patient.given_name FROM 1 FOR 1))
            END AS initial,
            ward.id AS ward_id
        FROM nh_activity activity
        INNER JOIN nh_clinical_patient patient
            ON activity.patient_id = patient.id
        INNER JOIN nh_clinical_location bed
            ON activity.location_id = bed.id
        INNER JOIN nh_clinical_location ward
            ON bed.parent_id = ward.id
        INNER JOIN nh_activity spell
            ON spell.data_model = 'nh.clinical.spell'
            AND spell.patient_id = activity.patient_id
        WHERE activity.state != 'completed'
        AND activity.state != 'cancelled'
        AND spell.state = 'started')
    SELECT
        id,
        activity_id,
        {proximity_interval},
        summary,
        state,
        user_id,
        date_scheduled,
        data_model,
        patient_other_id,
        nhs_number,
        ward_id,
        family_name,
        initial
    FROM activity"""

    def get_discharge_transfer_sql(self, table, location_row, interval, state):
        return self.discharge_transfer_skeleton.format(
            table=table, location_row=location_row, time=interval, state=state)

    def get_last_discharge_users(self, interval):
        return self.get_discharge_transfer_sql(
            table='discharge', location_row='location_id', interval=interval,
            state='completed')

    def get_last_transfer_users(self, interval):
        return self.get_discharge_transfer_sql(
            table='transfer', location_row='origin_loc_id', interval=interval,
            state='started')

    def get_wardboard(self, interval):
        return self.wardboard_skeleton.format(time=interval)

    def generate_workload_cases(self, workload):
        settings = self.pool['nh.clinical.settings']
        buckets = [b_obj.get('name') for b_obj in workload]
        buckets_valid = settings.validate_workload_buckets(buckets)
        if isinstance(buckets_valid, str):
            raise ValueError(buckets_valid)
        cases = []
        extract_pattern = re.compile(self.WORKLOAD_BUCKET_EXTRACT)
        for bucket in workload:
            index = bucket.get('sequence')
            name = bucket.get('name')
            bucket_elements = extract_pattern.match(name).groups()
            start = bucket_elements[0]
            start_int = 0
            end = bucket_elements[1]
            end_int = 0
            period = bucket_elements[2]
            if start:
                start_int = int(start)
            if end:
                end_int = int(end)
            if period == 'late':
                start_int *= -1
                if end:
                    end_int *= -1
            if start and end:
                if period == 'late':
                    cases.append(
                        'WHEN proximity BETWEEN {end} '
                        'AND {start} THEN {index}'.format(
                            start=start_int, end=end_int, index=index))
                else:
                    cases.append(
                        'WHEN proximity BETWEEN {start} '
                        'AND {end} THEN {index}'.format(
                            start=start_int, end=end_int, index=index))
            else:
                if period == 'late':
                    cases.append(
                        'WHEN proximity < {start} THEN {index}'.format(
                            start=start_int, index=index))
                else:
                    cases.append(
                        'WHEN proximity > {start} THEN {index}'.format(
                            start=start_int, index=index))
        return cases

    def get_workload(self, settings):
        if not settings:
            proximity_interval = '10 AS proximity_interval'
        else:
            bucket_cases = self.generate_workload_cases(settings)
            case_sql = ' '.join(bucket_cases)
            proximity_interval = \
                'CASE {cases} ELSE NULL END AS proximity_interval'.format(
                    cases=case_sql)
        return self.workload_skeleton.format(
            proximity_interval=proximity_interval)

    collect_activities_skeleton = """
    select distinct activity.id,
            activity.summary,
            patient.id as patient_id,
            ews1.clinical_risk,
            case
                when activity.date_scheduled is not null then
                activity.date_scheduled::text
                when activity.create_date is not null then
                activity.create_date::text
                else ''
            end as deadline,
            case
                when activity.date_scheduled is not null then
                  case when greatest(
                    now() at time zone 'UTC', activity.date_scheduled) !=
                    activity.date_scheduled
                    then 'overdue: ' else '' end ||
                  case when extract(days from (greatest(
                    now() at time zone 'UTC', activity.date_scheduled) -
                    least(now() at time zone 'UTC',
                    activity.date_scheduled))) > 0
                    then extract(days from (greatest(
                      now() at time zone 'UTC', activity.date_scheduled) -
                      least(now() at time zone 'UTC', activity.date_scheduled)
                      )) || ' day(s) '
                  else '' end ||
                  to_char(justify_hours(greatest(now() at time zone 'UTC',
                  activity.date_scheduled) - least(now() at time zone 'UTC',
                  activity.date_scheduled)), 'HH24:MI') || ' hours'
                when activity.create_date is not null then
                  case when greatest(now() at time zone 'UTC',
                    activity.create_date) != activity.create_date
                    then 'overdue: ' else '' end ||
                  case when extract(days from (greatest(now() at time zone
                    'UTC', activity.create_date) - least(now() at time zone
                    'UTC', activity.create_date))) > 0
                    then extract(days from (greatest(now() at time zone 'UTC',
                      activity.create_date) - least(now() at time zone 'UTC',
                      activity.create_date))) || ' day(s) '
                  else '' end ||
                  to_char(justify_hours(greatest(now() at time zone 'UTC',
                  activity.create_date) - least(now() at time zone 'UTC',
                  activity.create_date)), 'HH24:MI') || ' hours'
                else to_char((interval '0s'), 'HH24:MI') || ' hours'
            end as deadline_time,
            coalesce(patient.family_name, '') || ', ' ||
              coalesce(patient.given_name, '') || ' ' ||
              coalesce(patient.middle_names,'') as full_name,
            location.name as location,
            location_parent.name as parent_location,
            case
                when ews1.score is not null then ews1.score::text
                else ''
            end as ews_score,
            case
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) = 0 then 'same'
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) > 0 then 'up'
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) < 0 then 'down'
                when ews1.id is null and ews2.id is null then 'none'
                when ews1.id is not null and ews2.id is null then 'first'
                when ews1.id is null and ews2.id is not null then 'no latest'
            end as ews_trend,
            case
                when position('notification' in activity.data_model)::bool
                  then true
                else false
            end as notification
        from nh_activity activity
        inner join nh_activity spell_activity
        on spell_activity.id = activity.parent_id
        inner join nh_clinical_patient patient
          on patient.id = activity.patient_id
        inner join nh_clinical_location location
          on location.id = spell_activity.location_id
        inner join nh_clinical_location location_parent
          on location_parent.id = location.parent_id
        left join ews1 on ews1.spell_activity_id = spell_activity.id
        left join ews2 on ews2.spell_activity_id = spell_activity.id
        where activity.id in ({activity_ids})
        and spell_activity.state = 'started'
        order by deadline asc, activity.id desc
    """

    def get_collect_activities_sql(self, activity_ids_sql):
        return self.collect_activities_skeleton.format(
            activity_ids=activity_ids_sql)

    collect_patients_skeleton = """
    select distinct activity.id,
            patient.id,
            patient.dob,
            patient.gender,
            patient.sex,
            patient.other_identifier,
            case char_length(patient.patient_identifier) = 10
                when true then substring(patient.patient_identifier from 1
                  for 3) || ' ' || substring(patient.patient_identifier from 4
                  for 3) || ' ' || substring(patient.patient_identifier from 7
                  for 4)
                else patient.patient_identifier
            end as patient_identifier,
            coalesce(patient.family_name, '') || ', ' ||
              coalesce(patient.given_name, '') || ' ' ||
              coalesce(patient.middle_names,'') as full_name,
            case
                when ews0.date_scheduled is not null then
                  case when greatest(now() at time zone 'UTC',
                    ews0.date_scheduled) != ews0.date_scheduled
                    then 'overdue: ' else '' end ||
                  case when extract(days from (greatest(now() at time zone
                    'UTC', ews0.date_scheduled) - least(now() at time zone
                    'UTC', ews0.date_scheduled))) > 0
                    then extract(days from (greatest(now() at time zone 'UTC',
                      ews0.date_scheduled) - least(now() at time zone 'UTC',
                      ews0.date_scheduled))) || ' day(s) '
                    else '' end ||
                  to_char(justify_hours(greatest(now() at time zone 'UTC',
                    ews0.date_scheduled) - least(now() at time zone 'UTC',
                    ews0.date_scheduled)), 'HH24:MI') || ' hours'
                else to_char((interval '0s'), 'HH24:MI') || ' hours'
            end as next_ews_time,
            location.name as location,
            location_parent.name as parent_location,
            case
                when ews1.score is not null then ews1.score::text
                else ''
            end as ews_score,
            ews1.clinical_risk,
            case
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) = 0 then 'same'
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) > 0 then 'up'
                when ews1.id is not null and ews2.id is not null and
                  (ews1.score - ews2.score) < 0 then 'down'
                when ews1.id is null and ews2.id is null then 'none'
                when ews1.id is not null and ews2.id is null then 'first'
                when ews1.id is null and ews2.id is not null then 'no latest'
            end as ews_trend,
            case
                when ews0.frequency is not null then ews0.frequency
                else 0
            end as frequency
        from nh_activity activity
        inner join nh_clinical_patient patient
          on patient.id = activity.patient_id
        inner join nh_clinical_location location
          on location.id = activity.location_id
        inner join nh_clinical_location location_parent
          on location_parent.id = location.parent_id
        left join ews1 on ews1.spell_activity_id = activity.id
        left join ews2 on ews2.spell_activity_id = activity.id
        left join ews0 on ews0.spell_activity_id = activity.id
        where activity.state = 'started' and activity.data_model =
          'nh.clinical.spell' and activity.id in ({spell_ids})
        order by location
    """

    def get_collect_patients_sql(self, spell_ids):
        return self.collect_patients_skeleton.format(spell_ids=spell_ids)

    wb_transfer_ranked_skeleton = """
    select *
    from (
        select
            spell.id as spell_id,
            activity.*,
            split_part(activity.data_ref, ',', 2)::int as data_id,
            rank() over (partition by spell.id, activity.data_model,
                activity.state order by activity.sequence desc)
    from nh_clinical_spell spell
    inner join nh_activity activity
        on activity.spell_activity_id = spell.activity_id
        and activity.data_model = 'nh.clinical.patient.transfer') sub_query
    where rank = 1
    """

    def get_wb_transfer_ranked_sql(self):
        return self.wb_transfer_ranked_skeleton
