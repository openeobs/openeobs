from openerp.tests.common import SingleTransactionCase


class TestObsReportGetTriggeredActionIds(SingleTransactionCase):

    times_called = 0

    @classmethod
    def setUpClass(cls):
        super(TestObsReportGetTriggeredActionIds, cls).setUpClass()
        cr, uid, registry = cls.cr, cls.uid, cls.registry
        r_model = registry('ir.actions.report.xml')
        domain = [('report_name', 'like', 'observation_report')]
        r = r_model.browse(cr, uid, r_model.search(cr, uid, domain))
        cls.report_model = 'report.%s' % r.report_name
        try:
            cls.report_pool = registry(cls.report_model)
        except KeyError:
            cls.failureException('Unable to load Observation Report')

    def setUp(self):
        # Set up the report
        super(TestObsReportGetTriggeredActionIds, self).setUp()
        registry = self.registry
        self.times_called = 0

        def mock_activity_search(*args, **kwargs):
            creator_id = args[3][0][2]
            if creator_id == '1_triggered_action':
                return ['triggered_action']
            if creator_id == '2_triggered_actions':
                return ['triggered_action_1', 'triggered_action_2']
            if creator_id == '1_triggered_action_a':
                return ['1_triggered_action_1']
            if creator_id == '1_triggered_action_1':
                return ['triggered_action_2']
            if creator_id == '1_triggered_action_b':
                return ['2_triggered_actions', 'triggered_action_3']
            return []

        def mock_triggered_actions(*args, **kwargs):
            self.times_called += 1
            return mock_triggered_actions.origin(*args, **kwargs)

        registry('nh.activity')._patch_method('search', mock_activity_search)
        self.report_pool._patch_method('get_triggered_action_ids',
                                       mock_triggered_actions)

    def tearDown(self):
        super(TestObsReportGetTriggeredActionIds, self).tearDown()
        self.registry('nh.activity')._revert_method('search')
        self.report_pool._revert_method('get_triggered_action_ids')

    def test_get_no_triggered_actions(self):
        """
        Test that on there being no triggered actions it returns an empty list
        and only made 1 call
        """
        triggered_actions = \
            self.report_pool.get_triggered_action_ids(self.cr, self.uid,
                                                      'no_triggered_actions')
        self.assertEqual(triggered_actions, [])
        self.assertEqual(self.times_called, 1)

    def test_get_triggered_action_ids_depth_one(self):
        """
        Test gets triggered actions at a single depth i.e:
        initial_activity
          -> triggered_action

        Should give [triggered_action] and makes 2 calls
        """
        triggered_actions = \
            self.report_pool.get_triggered_action_ids(self.cr, self.uid,
                                                      '1_triggered_action')
        self.assertEqual(triggered_actions, ['triggered_action'])
        self.assertEqual(self.times_called, 2)

    def test_get_triggered_action_ids_depth_one_multi(self):
        """
        Test gets multiple triggered actions at single depth i.e:
        initial_activity
          -> triggered_action_1
          -> triggered_action_2

        Should give [triggered_action_1, triggered_action_2] and makes 3 calls
        """
        triggered_actions = \
            self.report_pool.get_triggered_action_ids(self.cr, self.uid,
                                                      '2_triggered_actions')
        self.assertEqual(triggered_actions, ['triggered_action_1',
                                             'triggered_action_2'])
        self.assertEqual(self.times_called, 3)

    def test_get_triggered_action_ids_depth_two(self):
        """
        Test gets triggered actions when nested twice i.e:
        initial_activity
          -> triggered_action_1
             -> triggered_action_2

        Should give [triggered_action_1, triggered_action_2] and makes 3 calls
        """
        triggered_actions = \
            self.report_pool.get_triggered_action_ids(self.cr, self.uid,
                                                      '1_triggered_action_a')
        self.assertEqual(triggered_actions, ['1_triggered_action_1',
                                             'triggered_action_2'])
        self.assertEqual(self.times_called, 3)

    def test_get_triggered_action_ids_depth_two_multi(self):
        """
        Test gets multiple triggered actions when nested twice i.e:
        initial_activity
          -> triggered_action_1
             -> triggered_action_2
             -> triggered_action_3
          -> triggered_action_4

        Should give [triggered_action_1, triggered_action_4,
                     triggered_action_2, triggered_action_3] and makes 5 calls
        """
        triggered_actions = \
            self.report_pool.get_triggered_action_ids(self.cr, self.uid,
                                                      '1_triggered_action_b')
        self.assertEqual(triggered_actions, ['2_triggered_actions',
                                             'triggered_action_3',
                                             'triggered_action_1',
                                             'triggered_action_2'])
        self.assertEqual(self.times_called, 5)
