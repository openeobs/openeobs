from openerp.tests.common import SingleTransactionCase
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import re


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
        self.sql_pool = self.registry('nh.clinical.sql')

        # Find activities that would show up on the workload board for ward
        # manager
        wards = self.location_pool.search(cr, uid, [['usage', '=', 'ward']])
        if not wards:
            raise ValueError('Could not find ward for test')
        ward = wards[0]
        shift_coordinators = self.user_pool.search(cr, uid, [
            ['groups_id.name', '=', 'NH Clinical Shift Coordinator Group'],
            ['location_ids', 'in', [ward]]
        ])
        if not shift_coordinators:
            raise ValueError('Could not find shift coordinator for test')
        self.shift_coordinator = shift_coordinators[0]

        activities = self.workload_pool.search(cr, uid, [
            ['user_ids', 'in', shift_coordinators],
            ['data_model', 'not in', ['nh.clinical.spell',
                                      'nh.clinical.patient.placement']],
            ['state', 'not in', ['cancelled', 'completed']]
        ])
        if not activities:
            raise ValueError('Could not find activities for test')
        if len(activities) < 7:
            raise ValueError('Not enough activities found for test')

        # Get buckets for test
        workload_buckets = self.settings_pool.read(
            cr, uid, 1, ['workload_bucket_period'])\
            .get('workload_bucket_period')
        buckets = self.buckets_pool.read(cr, uid, workload_buckets)
        if len(buckets) < 6:
            raise ValueError('Buckets not set correctly')

        pattern = re.compile(self.sql_pool.WORKLOAD_BUCKET_EXTRACT)
        self.activities = []
        for index, bucket in enumerate(buckets):
            period = bucket.get('name')
            match = pattern.match(period).groups()
            mins = int(match[0])
            if mins == 0:
                self.zero_mins = index + 1
            mins += 2
            if match[2] == 'late':
                dt = (datetime.now() - timedelta(minutes=mins)).strftime(DTF)
            else:
                dt = (datetime.now() + timedelta(minutes=mins)).strftime(DTF)
            activity = activities[index]
            self.activity_pool.write(cr, uid, activity, {
                'date_scheduled': dt, 'date_deadline': dt})
            self.activities.append(activity)

        # Set up datetimes for test
        remain_0 = datetime.now().strftime(DTF)
        # Set the activities to have the dates
        activity_0_remain = activities[len(buckets)]
        self.activity_pool.write(cr, uid, activity_0_remain, {
            'date_scheduled': remain_0, 'date_deadline': remain_0})
        self.activities.append(activity_0_remain)


class TestWorkloadInitial(TestWorkloadIntegration):

    def test_initial_board(self):
        cr, uid = self.cr, self.uid
        workload = self.workload_pool.read(cr, uid, self.activities)
        for index, activity in enumerate(workload):
            if index != len(self.activities) - 1:
                self.assertEqual(activity.get('proximity_interval'), index + 1)
            else:
                self.assertEqual(activity.get('proximity_interval'),
                                 self.zero_mins)

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
