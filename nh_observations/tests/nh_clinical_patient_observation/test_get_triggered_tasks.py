# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetTriggeredTasks(TransactionCase):

    def setUp(self):
        super(TestGetTriggeredTasks, self).setUp()
        self.activity_model = self.env['nh.activity']
        self.obs_model = self.env['nh.clinical.patient.observation']
        self.api_model = self.env['nh.clinical.api']

        self.activities = self.activity_model.new({})

        self.notification = self.activity_model.new({})
        self.notification.data_model = 'nh.clinical.patient.notification'
        self.notification.state = 'new'

        self.notification_2 = self.activity_model.new({})
        self.notification_2.data_model = 'nh.clinical.patient.notification'
        self.notification_2.state = 'new'

        self.observation = self.activity_model.new({})
        self.observation.data_model = 'nh.clinical.patient.observation'
        self.observation.state = 'new'

        # Make it a recordset.
        self.activities._ids = (
            self.notification.id,
            self.notification_2.id,
            self.observation.id
        )

        def mock_activity_search(*args, **kwargs):
            context = self.env.context

            if context and context.get('test'):
                if context.get('test') == 'no_triggered_activities':
                    activities = self.activity_model.new({})
                    activities._ids = ()
                    self.activities = activities
                    return self.activities
                elif context.get('test') == 'triggered_activities':
                    return self.activities
            return mock_activity_search.origin(*args, **kwargs)

        def mock_get_last_obs_activity(*args, **kwargs):
            activity = self.activity_model.new({})
            activity.data_ref = self.obs
            return activity

        def mock_activity_read(*args, **kwargs):
            return self.activities

        self.activity_model._patch_method('search', mock_activity_search)
        self.activity_model._patch_method('read', mock_activity_read)
        self.obs_model._patch_method('get_last_obs_activity',
                                     mock_get_last_obs_activity)
        self.api_model._patch_method('check_activity_access',
                                     lambda a, b: True)  # Always return True

        self.obs = self.obs_model.new({})

    def test_no_triggered_tasks_returns_nothing(self):
        self.env.context = {'test': 'no_triggered_activities'}
        actual = self.obs.get_triggered_tasks()

        self.assertEqual(0, len(actual))

    def test_triggered_tasks_returns_list_of_records(self):
        self.env.context = {'test': 'triggered_activities'}
        actual = self.obs.get_triggered_tasks()

        self.assertTrue(actual)

    def test_triggered_obs_not_included(self):
        self.env.context = {'test': 'triggered_activities'}

        actual = self.obs.get_triggered_tasks()
        self.activities._ids = (
            self.notification,
            self.notification_2
        )
        expected = self.activities

        self.assertEqual(expected, actual)

    def tearDown(self):
        self.activity_model._revert_method('search')
        self.activity_model._revert_method('read')
        self.obs_model._revert_method('get_last_obs_activity')
        self.api_model._revert_method('check_activity_access')
        super(TestGetTriggeredTasks, self).tearDown()
