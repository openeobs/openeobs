# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp import tools


class nh_eobs_news_report(osv.Model):
    _name = 'nh.eobs.news.report'
    _description = "NEWS Observations Cube"
    _auto = False
    _columns = {
        'user_id': fields.many2one('res.users', 'Taken By', readonly=True),
        # 'obs_type': fields.char('Type', readonly=True),
        'date_scheduled': fields.datetime('Date Scheduled', readonly=True),
        'date_terminated': fields.datetime('Date Taken', readonly=True),
        # 'location_id': fields.many2one('nh.clinical.location', 'Location',
        #                                readonly=True),
        'ward_id': fields.many2one('nh.clinical.location', 'Ward',
                                   readonly=True),
        'location_str': fields.char('Location', readonly=True),
        # 'trigger_type': fields.char('Trigger Type', readonly=True),
        'score': fields.char('Current Score', readonly=True),
        'clinical_risk': fields.char('Current Clinical Risk', readonly=True),
        'on_time': fields.integer('# On Time', readonly=True),
        'not_on_time': fields.integer('# Not On Time', readonly=True),
        'delay': fields.float('Minutes Delayed', digits=(16, 0), readonly=True,
                              group_operator="avg"),
        'minutes_early': fields.float('Minutes Early', digits=(16, 0),
                                      readonly=True, group_operator="avg"),
        'staff_type': fields.char('Staff Type', readonly=True),
        # 'partial_reason': fields.char('Reason', readonly=True),
        'previous_risk': fields.char('Previous Clinical Risk', readonly=True),
        'previous_score': fields.char('Previous Score', readonly=True),
        'trend_up': fields.integer('# Trend Up', readonly=True),
        'trend_down': fields.integer('# Trend Down', readonly=True),
        'trend_same': fields.integer('# Trend Same', readonly=True)
    }
    _order = 'date_terminated desc, location_id'

    def _select(self):
        group_array = """select array(
          select g.name
          from res_groups g
          inner join res_groups_users_rel gurel on gurel.gid = g.id
          where gurel.uid = u.id
        )
        """

        select_str = """select n.id as id,
            a.terminate_uid as user_id,
            case
                when n.partial_reason is not null then 'Partial'
                else 'Complete'
            end as obs_type,
            a.date_scheduled as date_scheduled,
            a.date_terminated as date_terminated,
            a.location_id as location_id,
            case
                when char_length(loc.name) = 5 then wloc.name||' Bed 00'||substring(loc.name from 5 for 1)
                when char_length(loc.name) = 6 then wloc.name||' Bed 0'||substring(loc.name from 5 for 2)
                else wloc.name||' '||loc.name
            end as location_str,
            case
                when t.data_model = 'nh.clinical.patient.placement'
                then 'Placement'
                else 'Observation'
            end as trigger_type,
            case
                when n.partial_reason is not null then 'Current Score: None'
                else 'Current Score: '||n.score::text
            end as score,
            case
                when n.clinical_risk = 'Current Risk: None'
                then 'Current Risk: No Risk'
                else 'Current Risk: '||n.clinical_risk
            end as clinical_risk,
            case
                when a.date_scheduled is null then 0
                when a.date_scheduled >= a.date_terminated then 1
                else 0
            end as on_time,
            case
                when a.date_scheduled is null then 0
                when a.date_scheduled < a.date_terminated then 1
                else 0
            end as not_on_time,
            case
                when a.date_scheduled is null then 0
                when a.date_scheduled >= a.date_terminated then 0
                else extract(epoch
                from (a.date_terminated - a.date_scheduled))/60
            end as delay,
            case
                when a.date_scheduled is null then 0
                when a.date_scheduled < a.date_terminated then 0
                else extract(epoch
                from (a.date_scheduled - a.date_terminated))/60
            end as minutes_early,
            case
                when (%s)::text[] @> ARRAY['NH Clinical Nurse Group']
                  then 'Nurse'
                when (%s)::text[] @> ARRAY['NH Clinical HCA Group']
                  then 'HCA'
                else 'Other'
            end as staff_type,
            case
                when n.partial_reason = 'patient_away_from_bed'
                  then 'Away From Bed'
                when n.partial_reason = 'patient_refused'
                  then 'Refused'
                when n.partial_reason = 'emergency_situation'
                  then 'Emergency'
                when n.partial_reason = 'doctors_request'
                  then 'Doctor Request'
                else 'Not Partial'
            end as partial_reason,
            w.ward_id as ward_id,
            case
                when t.data_model != 'nh.clinical.patient.observation.ews'
                  then 'Previous Risk: Unknown'
                when p.clinical_risk = 'Previous Risk: None'
                then 'Previous Risk: No Risk'
                else 'Previous Risk: '||p.clinical_risk
            end as previous_risk,
            case
                when t.data_model != 'nh.clinical.patient.observation.ews'
                  then 'Previous Score: Unknown'
                when p.partial_reason is not null then 'Previous Score: None'
                else 'Previous Score: '||p.score::text
            end as previous_score,
            case
                when t.data_model != 'nh.clinical.patient.observation.ews'
                  then 0
                when p.score < n.score then 1
                else 0
            end as trend_up,
            case
                when t.data_model != 'nh.clinical.patient.observation.ews'
                  then 0
                when p.score > n.score then 1
                else 0
            end as trend_down,
            case
                when t.data_model != 'nh.clinical.patient.observation.ews'
                  then 0
                when p.score = n.score then 1
                else 0
            end as trend_same
        """ % (group_array, group_array)
        return select_str

    def _group_by(self):
        group_by_str = """
            group by
                n.id,
                a.terminate_uid,
                obs_type,
                a.date_scheduled,
                a.date_terminated,
                a.location_id,
                location_str,
                trigger_type,
                n.score,
                n.clinical_risk,
                n.partial_reason,
                staff_type,
                w.ward_id,
                t.data_model,
                p.score,
                p.clinical_risk,
                p.partial_reason,
                on_time,
                not_on_time,
                delay,
                minutes_early,
                trend_up,
                trend_down,
                trend_same
        """
        return group_by_str

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'nh_eobs_news_report')
        cr.execute("""
                create or replace view nh_eobs_news_report as
                %s
                from nh_clinical_patient_observation_ews n
                inner join nh_activity a on n.activity_id = a.id
                inner join res_users u on a.terminate_uid = u.id
                inner join ward_locations w on w.id = a.location_id
                inner join nh_clinical_location loc on loc.id = a.location_id
                inner join nh_clinical_location wloc on wloc.id = w.ward_id
                left join nh_activity t on a.creator_id = t.id
                left join nh_clinical_patient_observation_ews p
                    on p.activity_id = t.id
                where a.state = 'completed'
                    and a.date_scheduled > current_date - interval '8 days'
                %s
        """ % (self._select(), self._group_by()))
