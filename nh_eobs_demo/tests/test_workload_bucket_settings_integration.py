from openerp.tests.common import SingleTransactionCase
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestWorkloadIntegration(SingleTransactionCase):

    def setUp(self):
        super(TestWorkloadIntegration, self).setUp()
        cr, uid = self.cr, self.uid
        self.user_pool = self.registry('res.users')
        self.workload_pool = self.registry('nh.activity.workload')
        self.buckets_pool = self.registry('nh.clinical.settings.workload')
        self.patient_pool = self.registry('nh.clinical.patient')
        self.activity_pool = self.registry('nh.activity')
        self.settings_pool = self.registry('nh.clinical.settings')
        self.config_pool = self.registry('nh.clinical.config.settings')
        self.location_pool = self.registry('nh.clinical.location')

        # Find activities that would show up on the workload board for ward
        # manager
        wards = self.location_pool.search(cr, uid, [['usage', '=', 'ward']])
        if not wards:
            raise ValueError('Could not find ward for test')
        ward = wards[0]
        ward_managers = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Ward Manager Group'],
            ['location_ids', 'in', [ward]]
        ])
        if not ward_managers:
            raise ValueError('Could not find ward manager for test')
        self.ward_manager = ward_managers[0]

        activities = self.workload_pool.search(cr, uid, [
            ['user_ids', 'in', ward_managers],
            ['data_model', 'not in', ['nh.clinical.spell',
                                      'nh.clinical.patient.placement']],
            ['state', 'not in', ['cancelled', 'completed']]
        ])
        if not activities:
            raise ValueError('Could not find activities for test')
        if len(activities) < 7:
            raise ValueError('Not enough activities found for test')

        # Set up datetimes for test
        remain_60 = (datetime.now() + timedelta(minutes=60)).strftime(DTF)
        remain_40 = (datetime.now() + timedelta(minutes=40)).strftime(DTF)
        remain_20 = (datetime.now() + timedelta(minutes=20)).strftime(DTF)
        remain_10 = (datetime.now() + timedelta(minutes=10)).strftime(DTF)
        remain_0 = datetime.now().strftime(DTF)
        late_10 = (datetime.now() - timedelta(minutes=10)).strftime(DTF)
        late_20 = (datetime.now() - timedelta(minutes=20)).strftime(DTF)

        # Set the activities to have the dates
        activity_60_remain = activities[0]
        self.activity_pool.write(cr, uid, activity_60_remain, {
            'date_scheduled': remain_60, 'date_deadline': remain_60})
        activity_40_remain = activities[1]
        self.activity_pool.write(cr, uid, activity_40_remain, {
            'date_scheduled': remain_40, 'date_deadline': remain_40})
        activity_20_remain = activities[2]
        self.activity_pool.write(cr, uid, activity_20_remain, {
            'date_scheduled': remain_20, 'date_deadline': remain_20})
        activity_10_remain = activities[3]
        self.activity_pool.write(cr, uid, activity_10_remain, {
            'date_scheduled': remain_10, 'date_deadline': remain_10})
        activity_0_remain = activities[4]
        self.activity_pool.write(cr, uid, activity_0_remain, {
            'date_scheduled': remain_0, 'date_deadline': remain_0})
        activity_10_late = activities[5]
        self.activity_pool.write(cr, uid, activity_10_late, {
            'date_scheduled': late_10, 'date_deadline': late_10})
        activity_20_late = activities[6]
        self.activity_pool.write(cr, uid, activity_20_late, {
            'date_scheduled': late_20, 'date_deadline': late_20})

        # Set to self so can reference later
        self.activity_60_remain = activity_60_remain
        self.activity_40_remain = activity_40_remain
        self.activity_20_remain = activity_20_remain
        self.activity_10_remain = activity_10_remain
        self.activity_0_remain = activity_0_remain
        self.activity_10_late = activity_10_late
        self.activity_20_late = activity_20_late


class TestWorkloadInitial(TestWorkloadIntegration):

    def test_initial_board(self):
        cr, uid = self.cr, self.uid
        workload = self.workload_pool.read(cr, uid, [
            self.activity_60_remain,
            self.activity_40_remain,
            self.activity_20_remain,
            self.activity_10_remain,
            self.activity_0_remain,
            self.activity_10_late,
            self.activity_20_late
        ])
        self.assertEqual(workload[0].get('proximity_interval'), 1)
        self.assertEqual(workload[1].get('proximity_interval'), 2)
        self.assertEqual(workload[2].get('proximity_interval'), 3)
        self.assertEqual(workload[3].get('proximity_interval'), 4)
        self.assertEqual(workload[4].get('proximity_interval'), 4)
        self.assertEqual(workload[5].get('proximity_interval'), 5)
        self.assertEqual(workload[6].get('proximity_interval'), 6)

# class TestWorkloadChanged(TestWorkloadIntegration):
#
#     def setUp(self):
#         super(TestWorkloadChanged, self).setUp()
#         cr, uid = self.cr, self.uid
#
#         bucket_ids = self.buckets_pool.search(cr, uid, [
#             ['name', 'in', [
#                 '0-15 minutes remain',
#                 '1-15 minutes late',
#                 '16+ minutes late'
#             ]]
#         ])
#         bucket_to_change = self.buckets_pool.search(cr, uid, [
#             ['name', '=', '46+ minutes remain']
#         ])
#         self.buckets_pool.write(cr, uid, bucket_to_change,
#                                 {
#               'name': '16+ minutes remain', 'sequence': 1})
#         self.buckets_pool.write(cr, uid, bucket_ids[0],
#                                 {'sequence': 2})
#         self.buckets_pool.write(cr, uid, bucket_ids[1],
#                                 {'sequence': 3})
#         self.buckets_pool.write(cr, uid, bucket_ids[2],
#                                 {'sequence': 4})
#         self.buckets = bucket_to_change + bucket_ids
#         self.settings_pool.write(cr, uid, 1, {
#             'workload_bucket_period': [[6, 0, self.buckets]]})
#
#     def test_init_method(self):
#         self.workload_pool.init(self.cr)
#         workload = self.workload_pool.read(self.cr, self.uid, [
#             self.activity_60_remain,
#             self.activity_40_remain,
#             self.activity_20_remain,
#             self.activity_10_remain,
#             self.activity_0_remain,
#             self.activity_10_late,
#             self.activity_20_late
#         ])
#         self.assertEqual(workload[0].get('proximity_interval'), 1)
#         self.assertEqual(workload[1].get('proximity_interval'), 1)
#         self.assertEqual(workload[2].get('proximity_interval'), 1)
#         self.assertEqual(workload[3].get('proximity_interval'), 2)
#         self.assertEqual(workload[4].get('proximity_interval'), 2)
#         self.assertEqual(workload[5].get('proximity_interval'), 3)
#         self.assertEqual(workload[6].get('proximity_interval'), 4)
#
#     def test_refresh_method(self):
#         cr, uid = self.cr, self.uid
#         buckets = [b.get('name') for b in
#                    self.workload_pool.read(cr, uid, self.buckets)]
#         self.config_pool.refresh_workload_view(cr, buckets)
#         workload = self.workload_pool.read(cr, uid, [
#             self.activity_60_remain,
#             self.activity_40_remain,
#             self.activity_20_remain,
#             self.activity_10_remain,
#             self.activity_0_remain,
#             self.activity_10_late,
#             self.activity_20_late
#         ])
#         self.assertEqual(workload[0].get('proximity_interval'), 1)
#         self.assertEqual(workload[1].get('proximity_interval'), 1)
#         self.assertEqual(workload[2].get('proximity_interval'), 1)
#         self.assertEqual(workload[3].get('proximity_interval'), 2)
#         self.assertEqual(workload[4].get('proximity_interval'), 2)
#         self.assertEqual(workload[5].get('proximity_interval'), 3)
#         self.assertEqual(workload[6].get('proximity_interval'), 4)
