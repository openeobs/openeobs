# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)
from openerp import tools


class t4_clinical_workload(orm.Model):
    _name = "t4.activity.workload"
    _inherits = {'t4.activity': 'activity_id'}
    _description = "Workload"
    _auto = False
    _table = "t4_activity_workload"
    _proximity_intervals = [(10, '46- minutes'),
                           (20, '45-31 minutes remain'),
                           (30, '30-16 minutes remain'),
                           (40, '15-0 minutes remain'),
                           (50, '1-15 minutes late'),
                           (60, '16+ minutes late')]    
    _columns = {
        'activity_id': fields.many2one('t4.activity', 'Activity', required=1, ondelete='restrict'),
        'proximity_interval': fields.selection(_proximity_intervals, 'Proximity Interval', readonly=True),
        'summary': fields.text('Summary'),
        'state': fields.text('State'),
        'user_id': fields.many2one('res.users', 'Assigned to'),
        'date_scheduled': fields.datetime('Scheduled Date'),
        'data_model': fields.text('Data Model'),
        'patient_other_id': fields.text('Hospital Number')
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'wardboard')
        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        activity.id as id,
                        spell.id as activity_id,
                        case
                            when activity.date_scheduled is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_scheduled)::int/60 < -46 then 10
                            when activity.date_scheduled is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_scheduled)::int/60 between -45 and -31 then 20
                            when activity.date_scheduled is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_scheduled)::int/60 between -30 and -16 then 30
                            when activity.date_scheduled is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_scheduled)::int/60 between -15 and 0 then 40
                            when activity.date_scheduled is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_scheduled)::int/60 between 1 and 15 then 50
                            when activity.date_scheduled is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_scheduled)::int/60 > 16 then 60
                            when activity.date_deadline is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_deadline)::int/60 < -46 then 10
                            when activity.date_deadline is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_deadline)::int/60 between -45 and -31 then 20
                            when activity.date_deadline is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_deadline)::int/60 between -30 and -16 then 30
                            when activity.date_deadline is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_deadline)::int/60 between -15 and 0 then 40
                            when activity.date_deadline is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_deadline)::int/60 between 1 and 15 then 50
                            when activity.date_deadline is not null and extract (epoch from  now() at time zone 'UTC' - activity.date_deadline)::int/60 > 16 then 60
                        else null end as proximity_interval,
                        activity.summary as summary,
                        activity.state as state,
                        activity.user_id as user_id,
                        case
                            when activity.date_scheduled is not null then activity.date_scheduled
                            when activity.date_deadline is not null then activity.date_deadline
                            else null
                        end as date_scheduled,
                        activity.data_model as data_model,
                        patient.other_identifier as patient_other_id
                    from t4_activity activity
                    inner join t4_clinical_patient patient on activity.patient_id = patient.id
                    left join t4_activity spell on spell.data_model = 't4.clinical.spell' and spell.patient_id = activity.patient_id
                )
        """ % (self._table, self._table))
        
        
    def _get_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        pi_copy =  [(pi[0],pi[1]) for pi in self._proximity_intervals]
        groups = pi_copy
        groups.reverse()
        fold = {pi[0]: False for pi in pi_copy}
        return groups, fold
       
    _group_by_full = {'proximity_interval': _get_groups}  