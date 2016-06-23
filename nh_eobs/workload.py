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

    def _proximity_intervals(self, cr, uid, context=None):
        settings_pool = self.pool['nh.clinical.settings']

        workload_pool = self.pool['nh.clinical.settings.workload']
        bucket_ids = settings_pool.get_setting(cr, uid,
                                               'workload_bucket_period')
        buckets = workload_pool.read(cr, uid, bucket_ids)
        pi_copy = [(pi.get('sequence'), pi.get('name')) for pi in buckets]
        return pi_copy

    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1,
                                       ondelete='restrict'),
        'proximity_interval': fields.selection(
            _proximity_intervals, method=True, readonly=True,
            string='Proximity Interval'),
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
        sql_pool = self.pool['nh.clinical.sql']
        settings_pool = self.pool['nh.clinical.settings']
        workload_pool = self.pool['nh.clinical.settings.workload']
        bucket_ids = settings_pool.get_setting(cr, 1, 'workload_bucket_period')
        buckets = workload_pool.read(cr, 1, bucket_ids)
        view = sql_pool.get_workload(buckets)
        tools.drop_view_if_exists(cr, self._table)
        cr.execute(
            """create or replace view {table} as ({workload})""".format(
                table=self._table, workload=view))

    def _get_groups(self, cr, uid, ids, domain, read_group_order=None,
                    access_rights_uid=None, context=None):
        settings_pool = self.pool['nh.clinical.settings']
        workload_pool = self.pool['nh.clinical.settings.workload']
        bucket_ids = settings_pool.get_setting(cr, uid,
                                               'workload_bucket_period')
        buckets = workload_pool.read(cr, uid, bucket_ids)
        groups = [(pi.get('sequence'), pi.get('name')) for pi in buckets]
        fold = {pi[0]: False for pi in groups}
        groups.reverse()
        return groups, fold

    _group_by_full = {'proximity_interval': _get_groups}
