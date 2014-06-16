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
    }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'wardboard')
        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        id,
                        id as activity_id,
                        case
                            when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 < -46 then 10
                            when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 between -45 and -31 then 20
                            when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 between -30 and -16 then 30
                            when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 between -15 and 0 then 40
                            when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 between 1 and 15 then 50
                            when extract (epoch from  now() at time zone 'UTC' - date_scheduled)::int/60 > 16 then 60
                        else null end as proximity_interval
                    from t4_activity
                )
        """ % (self._table, self._table))
        
        
    def _get_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        pi_copy =  [(pi[0],pi[1]) for pi in self._proximity_intervals]
        groups = pi_copy
        fold = {pi[0]: False for pi in pi_copy}
        return groups, fold
       
    _group_by_full = {'proximity_interval': _get_groups}  