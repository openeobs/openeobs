from openerp.osv import orm


class RefusedObservationsSQL(orm.AbstractModel):

    _inherit = 'nh.clinical.sql'
    _name = 'nh.clinical.sql'

    ews_activities_skeleton = """
    SELECT  ews.id AS ews_id,
            activity.id AS id,
            activity.data_ref,
            activity.data_model,
            ews.partial_reason,
            activity.spell_activity_id,
            activity.creator_id,
            activity.state,
            activity.summary,
            activity.date_terminated,
            activity.sequence
    FROM nh_activity as activity
    INNER JOIN nh_clinical_patient_observation_ews as ews
    ON split_part(activity.data_ref, ',', 2)::int = ews.id
    WHERE activity.data_model = 'nh.clinical.patient.observation.ews'
    """

    refused_ews_skeleton = """
    WITH RECURSIVE refused_ews_tree AS (
        --Select the fields we want to use from the original table
        SELECT  id,
                ews_id,
                creator_id,
                data_model,
                data_ref,
                spell_activity_id,
                state,
                ARRAY[id] as activity_ids,
                partial_reason,
                ARRAY[partial_reason] as partial_tree,
                id as first_activity_id,
                id as last_activity_id,
                true as refused,
                sequence
        FROM ews_activities
        --Make sure we only get EWS
        WHERE partial_reason = 'refused'
        AND state = 'completed'
        --Join the two tables
        UNION ALL
        --Select the same table but join it with parent row (via creator_id)
        SELECT  child_act.id,
                child_act.ews_id,
                child_act.creator_id,
                child_act.data_model,
                child_act.data_ref,
                child_act.spell_activity_id,
                child_act.state,
                array_append(act.activity_ids, child_act.id) AS activity_ids,
                child_act.partial_reason,
                array_append(act.partial_tree, child_act.partial_reason)
                  AS partial_tree,
                activity_ids[1] AS first_activity_id,
                child_act.id AS last_activity_id,
                NOT array_to_string(
                  array_cat(
                    partial_tree,
                    ARRAY[child_act.partial_reason]
                  ), ', ') <> array_to_string(
                  array_cat(
                    partial_tree,
                    ARRAY[child_act.partial_reason]
                  ), ', ', '(null)')
                AS refused,
                act.sequence
        FROM ews_activities as child_act
        INNER JOIN refused_ews_tree as act
        ON (child_act.creator_id = act.id)
        WHERE child_act.state = 'completed'
    )

    SELECT  *,
    row_number() over(
      partition by spell_activity_id
      ORDER BY spell_activity_id ASC,
      first_activity_id DESC,
      last_activity_id DESC
    ) AS rank
    FROM refused_ews_tree
    """

    refused_last_ews_skeleton = """
    SELECT  refused.id,
            refused.ews_id,
            refused.refused,
            acts.spell_id,
            acts.spell_activity_id,
            acts.date_terminated
    from refused_ews_activities AS refused
    RIGHT OUTER JOIN wb_activity_ranked AS acts
    ON acts.id = refused.id AND refused.rank = 1
    WHERE acts.rank = 1
    AND acts.state = 'completed'
    AND acts.data_model = 'nh.clinical.patient.observation.ews'
    """

    def get_ews_activities(self):
        return self.ews_activities_skeleton

    def get_refused_ews_activities(self):
        return self.refused_ews_skeleton

    def get_refused_last_ews(self):
        return self.refused_last_ews_skeleton

    def get_refused_wardboard(self, interval):
        """
        Override wardboard SQL view to include acuity index
        :param interval: Time interval used for recently transferred /
        discharged
        :return: SQL statement used in nh_eobs.init()
        """
        wardboard = self.get_wardboard(interval)
        wardboard = wardboard.replace(
            'ORDER BY ews_acts.sequence DESC '
            'LIMIT 1'
            ') '
            'THEN \'NoScore\' ',
            'ORDER BY ews_acts.sequence DESC '
            'LIMIT 1'
            ') '
            'THEN \'NoScore\' '
            'WHEN refused_last_ews.refused = true '
            'AND coalesce(refused_last_ews.date_terminated '
            '>= spell.move_date, TRUE) '
            'THEN \'Refused\' '
        )
        return wardboard.replace(
            'LEFT JOIN param ON param.spell_id = spell.id',
            'LEFT JOIN param ON param.spell_id = spell.id '
            'LEFT JOIN refused_last_ews '
            'ON refused_last_ews.spell_id = spell.id'
        )

    def get_collect_activities_sql(self, activity_ids_sql):
        sql = self.collect_activities_skeleton.replace(
            'left join ews1 on ews1.spell_activity_id = spell_activity.id',
            'left join ews1 on ews1.spell_activity_id = spell_activity.id '
            'LEFT JOIN nh_clinical_spell AS spell '
            'ON spell.activity_id = spell_activity.id '
            'LEFT JOIN last_finished_pme AS pme ON pme.spell_id = spell.id '
            'LEFT JOIN refused_last_ews '
            'ON refused_last_ews.spell_activity_id = spell_activity.id '
            'AND coalesce(refused_last_ews.date_terminated '
            '>= spell.move_date, TRUE) '
            'AND coalesce(refused_last_ews.date_terminated >= '
            'pme.activity_date_terminated, TRUE) '
        )
        sql = sql.replace(
            'end as deadline_time,',
            'end as deadline_time, '
            'refused_last_ews.refused AS refusal_in_effect, '
        )
        return sql.format(activity_ids=activity_ids_sql)

    def get_collect_patients_sql(self, spell_ids):
        sql = self.collect_patients_skeleton.replace(
            'left join ews0 on ews0.spell_activity_id = activity.id',
            'left join ews0 on ews0.spell_activity_id = activity.id '
            'LEFT JOIN nh_clinical_spell AS spell '
            'ON spell.activity_id = activity.id '
            'LEFT JOIN last_finished_pme AS pme ON pme.spell_id = spell.id '
            'LEFT JOIN refused_last_ews '
            'ON refused_last_ews.spell_activity_id = activity.id '
            'AND coalesce(refused_last_ews.date_terminated '
            '>= spell.move_date, TRUE) '
            'AND coalesce(refused_last_ews.date_terminated >= '
            'pme.activity_date_terminated, TRUE) '
            'AND (spell.obs_stop <> TRUE OR spell.obs_stop IS NULL) '
        )
        sql = sql.replace(
            'patient.other_identifier,',
            'patient.other_identifier, '
            'refused_last_ews.refused AS refusal_in_effect,'
        )
        return sql.format(spell_ids=spell_ids)

    refused_chain_count_skeleton = """
    SELECT  (
                with reasons (reason) as (
   		            select unnest(partial_tree)
	            )
	            select count(*)
	            from reasons
	            where reason = 'refused'
	        ) as count,
       	    first_activity_id as activity_id,
       	    spell_activity_id
    FROM (
        SELECT *,
        row_number() over(
            partition by last_activity_id
            ORDER BY
            last_activity_id DESC,
            first_activity_id ASC
        ) AS last_activity_rank,
        row_number() over(
            partition by first_activity_id
            ORDER BY
            last_activity_id DESC,
            first_activity_id ASC
        ) AS first_activity_rank
        FROM refused_ews_activities
        WHERE NOT array_to_string(partial_tree, ',', 'null') LIKE '%null%'
    ) AS refused_ews
    WHERE last_activity_rank = 1
    AND first_activity_rank = 1
    """

    def get_refused_chain_count_sql(self):
        return self.refused_chain_count_skeleton

    refused_review_chain_skeleton = """
    SELECT 	rchain.count,
        rchain.spell_activity_id,
        review_activity.state as review_state,
        review_activity.date_terminated as review_date_terminated,
        review_activity.terminate_uid as review_terminate_uid,
        freq_activity.state as freq_state,
        freq_activity.date_terminated as freq_date_terminated,
       	freq_activity.terminate_uid as freq_terminate_uid
    FROM refused_chain_count AS rchain
    LEFT JOIN nh_activity AS review_activity
    ON review_activity.creator_id = rchain.activity_id
    AND review_activity.data_model = 'nh.clinical.notification.clinical_review'
    LEFT JOIN nh_activity AS freq_activity
    ON freq_activity.creator_id = review_activity.id
    AND freq_activity.data_model =
    'nh.clinical.notification.clinical_review_frequency'
    """

    def get_refused_review_chain_sql(self):
        return self.refused_review_chain_skeleton
