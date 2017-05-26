from openerp.osv import orm


class WardDashboardSQL(orm.AbstractModel):

    _inherit = 'nh.clinical.sql'
    _name = 'nh.clinical.sql'

    ward_dashboard_reason_view_skeleton = """
        SELECT
        ward_locations.ward_id AS location_id,
        count(spell.patient_id),
        obs_stop.reason
        FROM nh_clinical_spell AS spell
        LEFT JOIN nh_clinical_location AS location
        ON spell.location_id = location.id
        AND location.usage = 'bed'
        LEFT JOIN wdb_ward_locations AS ward_locations
        ON location.id = ward_locations.id
        LEFT JOIN nh_clinical_pme_obs_stop AS obs_stop
        ON spell.id = obs_stop.spell
        LEFT JOIN nh_activity AS activity
        ON obs_stop.activity_id = activity.id
        AND activity.state = 'started'
        WHERE obs_stop.reason IS NOT NULL
        AND activity.state IS NOT NULL
        GROUP BY ward_locations.ward_id, obs_stop.reason"""

    ward_dashboard_reason_count_skeleton = """
        select * from wdb_reasons where reason = {reason}"""

    def get_ward_dashboard_reason_view(self):
        return self.ward_dashboard_reason_view_skeleton

    def get_ward_dashboard_reason_count(self, cr, reason):
        reason_model = \
            self.pool['nh.clinical.patient_monitoring_exception.reason']
        reason_id = reason_model.search(cr, 1, [['display_text', '=', reason]])
        if reason_id:
            reason_id = reason_id[0]
        else:
            raise ValueError('Could not find reason for ward '
                             'dashboard reason count - ' + reason)
        return self.ward_dashboard_reason_count_skeleton.format(
            reason=reason_id
        )

    ward_dashboard_workload_skeleton = """
        SELECT
        ward_locations.ward_id AS location_id,
        count(spell.patient_id)
        FROM nh_clinical_spell AS spell
        INNER JOIN nh_clinical_location AS location
        ON location.id = spell.location_id
        INNER JOIN wdb_ward_locations AS ward_locations
        ON ward_locations.id = location.id
        GROUP BY ward_locations.ward_id"""

    ward_dashboard_bed_count_skeleton = """
        SELECT
        ward_locations.ward_id AS location_id,
        count(loc.id)
        FROM nh_clinical_location AS loc
        INNER JOIN wdb_ward_locations AS ward_locations
        ON ward_locations.id = loc.id
        WHERE loc.usage = 'bed'
        GROUP BY ward_locations.ward_id
        """

    ward_dashboard_capacity_skeleton = """
        SELECT
        bed_count.location_id,
        (bed_count.count - workload.count) AS count
        FROM wdb_bed_count AS bed_count
        INNER JOIN wdb_workload_count AS workload
        ON bed_count.location_id = workload.location_id
        """

    ward_dashboard_obs_stop_skeleton = \
        ward_dashboard_workload_skeleton.replace(
            'ON location.id = spell.location_id',
            'ON location.id = spell.location_id '
            'AND location.usage = \'bed\''
        ).replace(
            'count(spell.patient_id)',
            'SUM(CASE WHEN spell.obs_stop = \'t\' THEN 1 ELSE 0 END) AS count'
        )

    ward_dashboard_on_ward_skeleton = """
        SELECT
        avail.location_id,
        (avail.patients_in_bed - obs_stop.count) AS count
        FROM loc_availability AS avail
        INNER JOIN wdb_obs_stop_count AS obs_stop
        ON avail.location_id = obs_stop.location_id
        """

    ward_dashboard_refused_obs_count_skeleton = """
        SELECT  ward_beds.location_id,
                coalesce(
                  sum(
                    CASE WHEN spell.refusing_obs = TRUE THEN 1 ELSE 0 END),0)
                AS count
          FROM nh_clinical_spell AS spell
          LEFT JOIN ward_beds
          ON spell.location_id = ANY(bed_ids)
        GROUP BY ward_beds.location_id
        """

    ward_dashboard_skeleton = """
        -- Create Ward Dashboard
        SELECT
            location.id AS id,
            location.id AS location_id,
            lwp.waiting_patients,
            avail.patients_in_bed,
            avail.free_beds,
            clu1.related_users AS related_hcas,
            clu2.related_users AS related_nurses,
            clu3.related_users AS related_doctors,
            rpc.high_risk_patients,
            rpc.med_risk_patients,
            rpc.low_risk_patients,
            rpc.no_risk_patients,
            rpc.noscore_patients,
            CASE
                WHEN rpc.high_risk_patients > 0 THEN 2
                WHEN rpc.med_risk_patients > 0 THEN 3
                WHEN rpc.low_risk_patients > 0 THEN 4
                WHEN rpc.no_risk_patients > 0 THEN 0
                WHEN rpc.noscore_patients > 0 THEN 7
                ELSE 7
            END AS kanban_color,
            awol.count AS awol_count,
            acute_ed.count AS acute_hospital_ed_count,
            extended_leave.count AS extended_leave_count,
            capacity.count AS capacity_count,
            workload.count AS workload_count,
            on_ward.count AS on_ward_count,
            refused_obs.count AS refused_obs_count
        FROM nh_clinical_location AS location
        LEFT JOIN loc_waiting_patients AS lwp
            ON lwp.location_id = location.id
        LEFT JOIN wdb_awol_count AS awol ON awol.location_id = location.id
        LEFT JOIN wdb_acute_hospital_ed_count AS acute_ed
            ON acute_ed.location_id = location.id
        LEFT JOIN wdb_extended_leave_count AS extended_leave
            ON extended_leave.location_id = location.id
        LEFT JOIN wdb_capacity_count AS capacity
            ON capacity.location_id = location.id
        LEFT JOIN wdb_workload_count AS workload
            ON workload.location_id = location.id
        LEFT JOIN wdb_on_ward_count AS on_ward
            ON on_ward.location_id = location.id
        LEFT JOIN wdb_refused_obs_count AS refused_obs
            ON refused_obs.location_id = location.id
        LEFT JOIN loc_availability AS avail
            ON avail.location_id = location.id
        LEFT JOIN child_loc_users AS clu1
            ON clu1.location_id = location.id
            AND clu1.group_name = 'NH Clinical HCA Group'
        LEFT JOIN child_loc_users AS clu2
            ON clu2.location_id = location.id
            AND clu2.group_name = 'NH Clinical Nurse Group'
        LEFT JOIN child_loc_users AS clu3
            ON clu3.location_id = location.id
            AND clu3.group_name = 'NH Clinical Doctor Group'
        LEFT JOIN loc_risk_patients_count AS rpc
            ON rpc.location_id = location.id
        WHERE location.usage = 'ward'
        """

    last_finished_obs_stop_for_spell_skeleton = """
        SELECT
        activity.id AS id,
        spell.activity_id AS spell_activity_id,
        spell.id AS spell_id,
        activity.date_terminated AS activity_date_terminated,
        activity.state as activity_state
        FROM nh_clinical_spell AS spell
        JOIN (
          SELECT DISTINCT ON (spell_activity_id) * FROM nh_activity
          WHERE data_model = 'nh.clinical.pme.obs_stop'
          AND state = ANY('{cancelled, completed}')
          ORDER BY spell_activity_id, date_terminated DESC
        ) AS activity
        ON activity.spell_activity_id = spell.activity_id
        """

    def get_wardboard(self, interval):
        """
        Override wardboard SQL view to include acuity index
        :param interval: Time interval used for recently transferred /
        discharged
        :return: SQL statement used in nh_eobs.init()
        """
        return self.wardboard_skeleton.replace(
            'spell.move_date,',
            'spell.move_date, '
            'spell.rapid_tranq AS rapid_tranq, '
            'CASE '
            'WHEN spell.obs_stop = \'t\' THEN \'ObsStop\' '
            'WHEN '
            '( '
            'SELECT activity_date_terminated '
            'FROM last_finished_obs_stop '
            'WHERE spell_id = spell.id '
            ') >= ( '
            'SELECT ews_acts.date_terminated '
            'FROM ews_activities as ews_acts '
            'WHERE ews_acts.spell_activity_id = spell.activity_id '
            'AND ews_acts.state = \'completed\' '
            'AND (ews_acts.partial_reason IS NULL '
            'OR ews_acts.partial_reason = \'refused\') '
            'ORDER BY ews_acts.sequence DESC '
            'LIMIT 1'
            ') '
            'THEN \'NoScore\' '
            'WHEN '
            '( '
            'SELECT ews_acts.date_terminated '
            'FROM ews_activities as ews_acts '
            'WHERE ews_acts.spell_activity_id = spell.activity_id '
            'AND ews_acts.state = \'completed\' '
            'AND (ews_acts.partial_reason IS NULL '
            'OR ews_acts.partial_reason = \'refused\') '
            'ORDER BY ews_acts.sequence DESC '
            'LIMIT 1'
            ') <= ( '
            'SELECT date_terminated '
            'FROM wb_transfer_ranked AS transfer '
            'WHERE transfer.spell_id = spell.id '
            'AND transfer.rank = 1 '
            'LIMIT 1 '
            ') '
            'THEN \'NoScore\' '
            'ELSE '
            'CASE '
            'WHEN ews1.id IS NULL THEN \'NoScore\' '
            'ELSE ews1.clinical_risk '
            'END '
            'END AS acuity_index,').format(time=interval)

    def get_ward_dashboard_workload(self):
        return self.ward_dashboard_workload_skeleton

    def get_ward_dashboard_bed_count(self):
        return self.ward_dashboard_bed_count_skeleton

    def get_ward_dashboard_capacity_count(self):
        return self.ward_dashboard_capacity_skeleton

    def get_ward_dashboard_obs_stop_count(self):
        return self.ward_dashboard_obs_stop_skeleton

    def get_ward_dashboard_on_ward_count(self):
        return self.ward_dashboard_on_ward_skeleton

    def get_ward_dashboard_refused_obs_count(self):
        return self.ward_dashboard_refused_obs_count_skeleton

    def get_ward_dashboard(self):
        return self.ward_dashboard_skeleton

    def get_last_finished_obs_stop(self):
        return self.last_finished_obs_stop_for_spell_skeleton
