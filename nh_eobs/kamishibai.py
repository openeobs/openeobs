# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging
_logger = logging.getLogger(__name__)


class nh_clinical_kamishibai(orm.Model):
    _name = "nh.clinical.kamishibai"

    _auto = False
    _table = "nh_clinical_kamishibai"
    _kamishibai_columns = [['snapshot', 'Snapshot'], ['s1', 'Current Shift'], ['s2', 'Last Shift'], ['s3', 'Previous Shift']]

    _columns = {
        'kamishibai_column': fields.selection(_kamishibai_columns, 'Kamishibai Column'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'spell_activity_id': fields.many2one('nh.activity', 'Spell Activity'),
        'location_id': fields.many2one('nh.clinical.location', 'Location'),
        'ward_id': fields.many2one('nh.clinical.location', 'Ward'),
        'location_full_name': fields.related('location_id', 'full_name', type='char', size=150, string='Location Name'),
        'start': fields.datetime('Shift Start'),
        'end': fields.datetime('Shift End'),
        'status': fields.char('Status', size=10)
    }

    _order = 'ward_id asc, location_id asc, patient_id asc'

    def _get_kc_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        res = [['snapshot', 'Snapshot'], ['s1', 'Current Shift'], ['s2', 'Last Shift'], ['s3', 'Previous Shift']]
        fold = {r[0]: False for r in res}
        return res, fold

    _group_by_full = {
        'kamishibai_column': _get_kc_groups,
    }

    def init(self, cr):
        cr.execute("""


drop view if exists nh_clinical_kamishibai;

create or replace view
created_activities as(
    with recursive created_act(id, parent_id, creator_id, data_model, date_scheduled, date_terminated, created) as (
        select
            a.id,
            a.parent_id,
            a.creator_id,
            a.data_model,
            a.date_scheduled,
            a.date_terminated,
            ARRAY[a.id] as created
        from nh_activity as a
        where a.data_model = 'nh.clinical.patient.observation.ews' and a.state != 'cancelled'

        union all

        select
            c.id,
            c.parent_id,
            c.creator_id,
            c.data_model,
            c.date_scheduled,
            c.date_terminated,
            ca.created || ARRAY[c.id] as created
        from created_act as ca, nh_activity as c
        where c.creator_id = ca.id and c.data_model != 'nh.clinical.patient.observation.ews' and c.state != 'cancelled')
    select
        id,
        parent_id,
        creator_id,
        data_model,
        date_scheduled,
        date_terminated,
        case
            when date_scheduled is null then 'n/a'
            when date_terminated is null and date_scheduled >= now() at time zone 'UTC' then 'ok'
            when date_terminated is null and date_scheduled < now() at time zone 'UTC' then 'overdue'
            when date_terminated <= date_scheduled then 'ok'
            when date_terminated >= date_scheduled then 'overdue'
            else 'n/a'
        end as status,
        created
    from created_act
);

create or replace view
snapshot_status as(
    select
        spell.id as spell_id,
        array_agg(case
            when activity.date_scheduled is null then 'n/a'
            when activity.date_terminated is null and activity.date_scheduled >= now() at time zone 'UTC' then 'ok'
            when activity.date_terminated is null and activity.date_scheduled < now() at time zone 'UTC' then 'overdue'
            when activity.date_terminated <= activity.date_scheduled then 'ok'
            when activity.date_terminated >= activity.date_scheduled then 'overdue'
            else 'n/a'
        end) as status
    from nh_activity activity
    inner join nh_activity spell on spell.id = activity.parent_id
    where activity.state != 'completed' and activity.state != 'cancelled' and spell.state = 'started' and activity.data_model = 'nh.clinical.patient.observation.ews'
    group by spell_id
);

create or replace view
shift_status as(
    select
        timespan.id as timespan_id,
        array_agg(case
            when ca.date_scheduled is null then 'n/a'
            when ca.date_terminated is null and ca.date_scheduled > timespan.end then 'n/a'
            when ca.date_terminated is null and ca.date_scheduled < now() at time zone 'UTC' then 'overdue'
            when ca.date_terminated is null then 'ok'
            when ca.date_scheduled < timespan.start and ca.date_terminated < timespan.start then 'n/a'
            when ca.date_scheduled > timespan.end and ca.date_terminated > timespan.end then 'n/a'
            when ca.date_scheduled >= timespan.start and ca.date_scheduled <= timespan.end and ca.date_terminated > ca.date_scheduled then 'overdue'
            when ca.date_scheduled >= timespan.start and ca.date_scheduled <= timespan.end and ca.date_terminated <= ca.date_scheduled then 'ok'
            when ca.date_terminated >= timespan.start and ca.date_terminated <= timespan.end and ca.date_terminated > ca.date_scheduled then 'overdue'
            when ca.date_terminated >= timespan.start and ca.date_terminated <= timespan.end and ca.date_terminated <= ca.date_scheduled then 'ok'
            else 'n/a'
        end) as status
    from nh_clinical_spell_timespan timespan
    inner join nh_activity spell_activity on spell_activity.id = timespan.spell_activity_id
    inner join nh_clinical_spell spell on spell.activity_id = timespan.spell_activity_id
    inner join nh_clinical_shift shift on shift.id = timespan.shift_id
    left join created_activities ca on ca.parent_id = spell_activity.id
    where shift.position != '4' and shift.position != '0'
    group by timespan_id
);

create or replace view
nh_clinical_kamishibai as(
select
    k.kamishibai_column,
    k.id,
    k.patient_id,
    k.spell_activity_id,
    k.location_id,
    k.ward_id,
    k.start,
    k.end,
    k.status
from (

    select
        'snapshot' as kamishibai_column,
        '0' || patient.id::TEXT as id,
        spell.patient_id as patient_id,
        spell_activity.id as spell_activity_id,
        location.id as location_id,
        wlocation.ward_id as ward_id,
        null as start,
        null as end,
        case
            when 'overdue' = any(snapshot.status) then 'overdue'
            when 'ok' = any(snapshot.status) then 'ok'
            else 'n/a'
        end as status

    from nh_clinical_spell spell
    inner join nh_activity spell_activity on spell_activity.id = spell.activity_id
    inner join nh_clinical_patient patient on spell.patient_id = patient.id
    left join snapshot_status snapshot on snapshot.spell_id = spell_activity.id
    left join nh_clinical_location location on location.id = spell.location_id
    left join ward_locations wlocation on wlocation.id = location.id
    where spell_activity.state = 'started'

    union

    select
        case
            when shift.position = '1' then 's1'
            when shift.position = '2' then 's2'
            when shift.position = '3' then 's3'
            else null
        end as kamishibai_column,
        timespan.id::TEXT as id,
        spell.patient_id as patient_id,
        spell_activity.id as spell_activity_id,
        location.id as location_id,
        wlocation.id as ward_id,
        timespan.start as start,
        timespan.end as end,
        case
            when 'overdue' = any(ss.status) then 'overdue'
            when 'ok' = any(ss.status) then 'ok'
            else 'n/a'
        end as status

    from nh_clinical_spell_timespan timespan
    inner join nh_activity spell_activity on spell_activity.id = timespan.spell_activity_id
    inner join nh_clinical_spell spell on spell.activity_id = timespan.spell_activity_id
    inner join nh_clinical_patient patient on patient.id = spell.patient_id
    inner join nh_clinical_shift shift on shift.id = timespan.shift_id
    inner join nh_clinical_shift_pattern pattern on pattern.id = shift.pattern_id
    inner join nh_clinical_location wlocation on wlocation.id = pattern.location_id
    left join nh_clinical_location location on location.id = spell.location_id
    left join shift_status ss on ss.timespan_id = timespan.id
    where shift.position != '4' and shift.position != '0'
    ) as k

);

select * from nh_clinical_kamishibai
order by ward_id, location_id;
        """)