# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
_logger = logging.getLogger(__name__)
from openerp.addons.nh_activity.activity import except_if
from openerp import SUPERUSER_ID


class nh_clinical_kamishibai(orm.Model):
    _name = "nh.clinical.kamishibai"

    _auto = False
    _table = "nh_clinical_kamishibai"
    _kamishibai_columns = [['snapshot', 'Snapshot'], ['s1', 'Current Shift'], ['s2', 'Last Shift'], ['s3', 'Previous Shift']]

    def _get_kamishibai_multi(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        activity_pool = self.pool['nh.activity']
        shift_pool = self.pool['nh.clinical.shift.pattern']
        for k_id in ids:
            kamishibai = self.browse(cr, uid, k_id, context=context)
            status = 'n/a'
            if kamishibai.kamishibai_column == 'snapshot':
                latest_ews_ids = activity_pool.search(cr, uid, [
                    ['parent_id', '=', kamishibai.spell_activity_id.id],
                    ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                    ['state', 'not in', ['completed', 'cancelled']]], context=context)
                if not latest_ews_ids:
                    res[k_id] = {
                        'status': status,
                        'shift1_label': 'N/A',
                        'shift2_label': 'N/A',
                        'shift3_label': 'N/A'
                    }
                    continue
                current_loop_ids = activity_pool.get_recursive_created_ids(cr, uid, latest_ews_ids[0], context=context)
                status = 'ok'
                for a in activity_pool.browse(cr, uid, current_loop_ids, context=context):
                    if a.date_scheduled and a.date_terminated:
                        if dt.strptime(a.date_terminated, dtf) > dt.strptime(a.date_scheduled, dtf):
                            status = 'overdue'
                    elif a.date_scheduled and dt.now() > dt.strptime(a.date_scheduled, dtf):
                        status = 'overdue'
                res[k_id] = {
                    'status': status,
                    'shift1_label': 'N/A',
                    'shift2_label': 'N/A',
                    'shift3_label': 'N/A'
                }
            else:
                status = 'n/a'
                if not kamishibai.ward_id.shift_pattern_ids:
                    res[k_id] = {
                        'status': status,
                        'shift1_label': 'N/A',
                        'shift2_label': 'N/A',
                        'shift3_label': 'N/A'
                    }
                    continue
                shift1 = False
                shift2 = False
                shift3 = False
                diff = 1440
                diff2 = 1440
                diff3 = 1440
                n = dt.now()
                now = dt(year=n.year, month=n.month, day=n.day, hour=n.hour, minute=n.minute, second=0)
                for ds in kamishibai.ward_id.shift_pattern_ids:
                    distance = shift_pool.distance(cr, uid, ds.id, now, context=context)
                    if not distance:
                        shift1 = ds
                        continue
                    # if not shift1:
                    #     diff = distance
                    #     shift1 = ds
                    # else:
                    if distance < diff:
                        diff = distance
                        # shift1 = ds
                if not shift1:
                    res[k_id] = {
                        'status': status,
                        'shift1_label': 'N/A',
                        'shift2_label': 'N/A',
                        'shift3_label': 'N/A'
                    }
                    continue
                shift1_start = now - td(minutes=diff)
                shift1_end = shift1_start + td(minutes=shift1.duration)
                # shift1_end = now - td(minutes=diff)
                # shift1_start = shift1_end - td(minutes=shift1.duration)
                if len(kamishibai.ward_id.shift_pattern_ids) > 1:
                    for ds in kamishibai.ward_id.shift_pattern_ids:
                        distance = shift_pool.distance(cr, uid, ds.id, shift1_start, context=context)
                        if not shift2:
                            diff2 = distance
                            shift2 = ds
                        else:
                            if distance < diff2:
                                diff2 = distance
                                shift2 = ds
                else:
                    diff2 = 1440-shift1.duration
                    shift2 = shift1
                shift2_end = shift1_start - td(minutes=diff2)
                shift2_start = shift2_end - td(minutes=shift2.duration)
                if len(kamishibai.ward_id.shift_pattern_ids) > 2:
                    for ds in kamishibai.ward_id.shift_pattern_ids:
                        distance = shift_pool.distance(cr, uid, ds.id, shift2_start, context=context)
                        if not shift3:
                            diff3 = distance
                            shift3 = ds
                        else:
                            if distance < diff3:
                                diff3 = distance
                                shift3 = ds
                else:
                    diff3 = 1440-shift1.duration
                    shift3 = shift1
                shift3_end = shift2_start - td(minutes=diff3)
                shift3_start = shift3_end - td(minutes=shift3.duration)
                res[k_id] = {
                    'shift1_label': shift1_start.strftime(dtf) + '--' + shift1_end.strftime(dtf),
                    'shift2_label': shift2_start.strftime(dtf) + '--' + shift2_end.strftime(dtf),
                    'shift3_label': shift3_start.strftime(dtf) + '--' + shift3_end.strftime(dtf)
                }
                if kamishibai.kamishibai_column == 's1':
                    shift1_ews_ids = activity_pool.search(cr, uid, [
                        ['parent_id', '=', kamishibai.spell_activity_id.id],
                        ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                        ['date_scheduled', '>=', shift1_start.strftime(dtf)], ['date_scheduled', '<=', shift1_end.strftime(dtf)]], context=context)
                    shift1_ews_ids += activity_pool.search(cr, uid, [
                        ['parent_id', '=', kamishibai.spell_activity_id.id],
                        ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                        ['date_scheduled', '<', shift1_start.strftime(dtf)], '|',
                        ['date_terminated', '=', False],
                        ['date_terminated', '>=', shift1_start.strftime(dtf)]], context=context)
                    if not shift1_ews_ids:
                        res[k_id]['status'] = 'ok'
                        continue
                    current_loop_ids = []
                    for ews_id in shift1_ews_ids:
                        current_loop_ids += activity_pool.get_recursive_created_ids(cr, uid, ews_id, context=context)
                    status = 'ok'
                    for a in activity_pool.browse(cr, uid, current_loop_ids, context=context):
                        if a.date_scheduled and a.date_terminated:
                            if dt.strptime(a.date_terminated, dtf) > dt.strptime(a.date_scheduled, dtf):
                                status = 'overdue'
                        elif a.date_scheduled and dt.now() > dt.strptime(a.date_scheduled, dtf):
                            status = 'overdue'
                        elif a.date_scheduled:
                            status = 'n/a'
                    res[k_id]['status'] = status
                elif kamishibai.kamishibai_column == 's2':
                    shift2_ews_ids = activity_pool.search(cr, uid, [
                        ['parent_id', '=', kamishibai.spell_activity_id.id],
                        ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                        ['date_scheduled', '>=', shift2_start.strftime(dtf)], ['date_scheduled', '<=', shift2_end.strftime(dtf)]], context=context)
                    shift2_ews_ids += activity_pool.search(cr, uid, [
                        ['parent_id', '=', kamishibai.spell_activity_id.id],
                        ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                        ['date_scheduled', '<', shift2_start.strftime(dtf)], '|',
                        ['date_terminated', '=', False],
                        ['date_terminated', '>=', shift2_start.strftime(dtf)]], context=context)
                    if not shift2_ews_ids:
                        res[k_id]['status'] = 'ok'
                        continue
                    current_loop_ids = []
                    for ews_id in shift2_ews_ids:
                        current_loop_ids += activity_pool.get_recursive_created_ids(cr, uid, ews_id, context=context)
                    status = 'ok'
                    for a in activity_pool.browse(cr, uid, current_loop_ids, context=context):
                        if a.date_scheduled and a.date_terminated:
                            if dt.strptime(a.date_terminated, dtf) > dt.strptime(a.date_scheduled, dtf):
                                status = 'overdue'
                        elif a.date_scheduled and dt.now() > dt.strptime(a.date_scheduled, dtf):
                            status = 'overdue'
                        elif a.date_scheduled:
                            status = 'n/a'
                    res[k_id]['status'] = status
                else:
                    shift3_ews_ids = activity_pool.search(cr, uid, [
                        ['parent_id', '=', kamishibai.spell_activity_id.id],
                        ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                        ['date_scheduled', '>=', shift3_start.strftime(dtf)], ['date_scheduled', '<=', shift3_end.strftime(dtf)]], context=context)
                    shift3_ews_ids += activity_pool.search(cr, uid, [
                        ['parent_id', '=', kamishibai.spell_activity_id.id],
                        ['data_model', '=', 'nh.clinical.patient.observation.ews'],
                        ['date_scheduled', '<', shift3_start.strftime(dtf)], '|',
                        ['date_terminated', '=', False],
                        ['date_terminated', '>=', shift3_start.strftime(dtf)]], context=context)
                    if not shift3_ews_ids:
                        res[k_id]['status'] = 'ok'
                        continue
                    current_loop_ids = []
                    for ews_id in shift3_ews_ids:
                        current_loop_ids += activity_pool.get_recursive_created_ids(cr, uid, ews_id, context=context)
                    status = 'ok'
                    for a in activity_pool.browse(cr, uid, current_loop_ids, context=context):
                        if a.date_scheduled and a.date_terminated:
                            if dt.strptime(a.date_terminated, dtf) > dt.strptime(a.date_scheduled, dtf):
                                status = 'overdue'
                        elif a.date_scheduled and dt.now() > dt.strptime(a.date_scheduled, dtf):
                            status = 'overdue'
                        elif a.date_scheduled:
                            status = 'n/a'
                    res[k_id]['status'] = status
        return res

    _columns = {
        'kamishibai_column': fields.selection(_kamishibai_columns, 'Kamishibai Column'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'spell_activity_id': fields.many2one('nh.activity', 'Spell Activity'),
        'location_id': fields.many2one('nh.clinical.location', 'Location'),
        'ward_id': fields.many2one('nh.clinical.location', 'Ward'),
        'location_full_name': fields.related('location_id', 'full_name', type='char', size=150, string='Location Name'),
        'status': fields.char('Status', size=5),
        'start': fields.datetime('Shift Start'),
        'end': fields.datetime('Shift End')
    }

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
ward_locations as(
    with recursive ward_loc(id, parent_id, path, ward_id) as (
        select lc.id, lc.parent_id, ARRAY[lc.id] as path, lc.id as ward_id
        from nh_clinical_location as lc
        where lc.usage = 'ward'
        union all
        select l.id, l.parent_id, w.path || ARRAY[l.id] as path, w.path[1] as ward_id
        from ward_loc as w, nh_clinical_location as l
        where l.parent_id = w.id)
    select * from ward_loc
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
    'n/a' as status,
    k.start,
    k.end
from (

    select
        'snapshot' as kamishibai_column,
        'S' || patient.id::TEXT as id,
        spell.patient_id as patient_id,
        spell_activity.id as spell_activity_id,
        location.id as location_id,
        wlocation.ward_id as ward_id,
        null as start,
        null as end

    from nh_clinical_spell spell
    inner join nh_activity spell_activity on spell_activity.id = spell.activity_id
    inner join nh_clinical_patient patient on spell.patient_id = patient.id
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
        timespan.end as end

    from nh_clinical_spell_timespan timespan
    inner join nh_activity spell_activity on spell_activity.id = timespan.spell_activity_id
    inner join nh_clinical_spell spell on spell.activity_id = timespan.spell_activity_id
    inner join nh_clinical_patient patient on patient.id = spell.patient_id
    inner join nh_clinical_shift shift on shift.id = timespan.shift_id
    inner join nh_clinical_shift_pattern pattern on pattern.id = shift.pattern_id
    inner join nh_clinical_location wlocation on wlocation.id = pattern.location_id
    left join nh_clinical_location location on location.id = spell.location_id
    where shift.position != '4' and shift.position != '0'
    ) as k

);

select * from nh_clinical_kamishibai;
        """)