# Part of Open eObs. See LICENSE file for full copyright and licensing details.
# -*- coding: utf-8 -*-
"""
Shows the pending :class:`activities<activity.nh_clinical_activity>` by
proximity interval.
"""
from openerp.osv import orm, fields
import logging
from openerp import tools
_logger = logging.getLogger(__name__)


class nh_clinical_workload(orm.Model):
    """
    Extends :class:`activity<activity.nh_activity>`, categorising each
    pending activity by distance from when the activity is scheduled
    for, including overdue activities.
    """

    _name = "nh.activity.workload"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Workload"
    _auto = False
    _table = "nh_activity_workload"
    _proximity_intervals = [(10, '46- minutes'),
                            (20, '45-31 minutes remain'),
                            (30, '30-16 minutes remain'),
                            (40, '15-0 minutes remain'),
                            (50, '1-15 minutes late'),
                            (60, '16+ minutes late')]
    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1,
                                       ondelete='restrict'),
        'proximity_interval': fields.selection(
            _proximity_intervals, 'Proximity Interval', readonly=True),
        'summary': fields.text('Summary'),
        'state': fields.text('State'),
        'user_id': fields.many2one('res.users', 'Assigned to'),
        'date_scheduled': fields.datetime('Scheduled Date'),
        'data_model': fields.text('Data Model'),
        'patient_other_id': fields.text('Hospital Number'),
        'nhs_number': fields.text('NHS Number'),
        'initial': fields.text('Patient Name Initial'),
        'family_name': fields.text('Patient Family Name'),
        'ward_id': fields.many2one('nh.clinical.location', 'Parent Location')
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'wardboard')
        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    with activity as (
                        select
                            activity.id as id,
                            spell.id as activity_id,
                            extract (epoch from  (now() at time zone 'UTC' -
                                coalesce(activity.date_scheduled,
                                activity.date_deadline)))::int/60 as proximity,
                            activity.summary as summary,
                            activity.state as state,
                            activity.user_id as user_id,
                            coalesce(activity.date_scheduled,
                                activity.date_deadline) as date_scheduled,
                            activity.data_model as data_model,
                            patient.other_identifier as patient_other_id,
                            patient.patient_identifier as nhs_number,
                            patient.family_name as family_name,
                            case
                                when patient.given_name is null then ''
                                else upper(substring(patient.given_name
                                    from 1 for 1))
                            end as initial,
                            ward.id as ward_id
                        from nh_activity activity
                        inner join nh_clinical_patient patient
                            on activity.patient_id = patient.id
                        inner join nh_clinical_location bed
                            on activity.location_id = bed.id
                        inner join nh_clinical_location ward
                            on bed.parent_id = ward.id
                        inner join nh_activity spell
                            on spell.data_model = 'nh.clinical.spell'
                            and spell.patient_id = activity.patient_id
                        where activity.state != 'completed'
                        and activity.state != 'cancelled'
                        and spell.state = 'started'
                        )
                        select
                            id,
                            activity_id,
                            case
                                when proximity < -46 then 10
                                when proximity between -45 and -31 then 20
                                when proximity between -30 and -16 then 30
                                when proximity between -15 and 0 then 40
                                when proximity between 1 and 15 then 50
                                when proximity > 16 then 60
                            else null end as proximity_interval,
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
                        from activity
                )
        """ % (self._table, self._table))

    def _get_groups(self, cr, uid, ids, domain, read_group_order=None,
                    access_rights_uid=None, context=None):
        pi_copy = [(pi[0], pi[1]) for pi in self._proximity_intervals]
        groups = pi_copy
        groups.reverse()
        fold = {pi[0]: False for pi in pi_copy}
        return groups, fold

    _group_by_full = {'proximity_interval': _get_groups}
