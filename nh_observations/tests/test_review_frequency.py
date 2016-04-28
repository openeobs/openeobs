# coding: utf-8
from openerp.tests.common import SingleTransactionCase


class TestReviewFrequency(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestReviewFrequency, cls).setUpClass()
        cls.review_frequency_pool = \
            cls.registry('nh.clinical.notification.frequency')
        cls.activity_pool = cls.registry('nh.activity')

        def mock_ews_id(*args, **kwargs):
            return [9001]
        cls.activity_pool._patch_method('search', mock_ews_id)

    @classmethod
    def tearDownClass(cls):
        cls.activity_pool._revert_method('search')
        super(TestReviewFrequency, cls).tearDownClass()

    def setUp(self):
        super(TestReviewFrequency, self).setUp()
        self.activity = self.activity_pool.new(self.cr, self.uid, {
            'data_model': 'nh.clinical.patient.observation'})

    def tearDown(self):
        self.activity_pool._revert_method('browse')
        super(TestReviewFrequency, self).tearDown()

    def setUpMock(self, frequency):
        def mock_activity_browse(*args, **kwargs):
            if len(args) > 2 and args[3] == 9001:
                self.activity.data_ref = \
                    self.registry('nh.clinical.patient.observation') \
                        .new(self.cr, self.uid, {'frequency': frequency})
                return self.activity
            else:
                return mock_activity_browse.origin(*args, **kwargs)

        self.activity_pool._patch_method('browse', mock_activity_browse)

    def test_15_minutes(self):
        self.setUpMock(15)
        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(
            form_description[0]['selection'],
            [(15, 'Every 15 Minutes')]
        )

    def test_30_minutes(self):
        self.setUpMock(30)
        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(
            form_description[0]['selection'],
            [
                (15, 'Every 15 Minutes'),
                (30, 'Every 30 Minutes')
            ]
        )

    def test_60_minutes(self):
        self.setUpMock(60)
        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(
            form_description[0]['selection'],
            [
                (15, 'Every 15 Minutes'),
                (30, 'Every 30 Minutes'),
                (60, 'Every Hour')
            ]
        )

    def test_6_hours(self):
        self.setUpMock(360)
        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(
            form_description[0]['selection'],
            [
                (15, 'Every 15 Minutes'),
                (30, 'Every 30 Minutes'),
                (60, 'Every Hour'),
                (120, 'Every 2 Hours'),
                (240, 'Every 4 Hours'),
                (360, 'Every 6 Hours'),
            ]
        )

    def test_24_hours(self):
        self.setUpMock(1440)
        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(
            form_description[0]['selection'],
            [
                (15, 'Every 15 Minutes'),
                (30, 'Every 30 Minutes'),
                (60, 'Every Hour'),
                (120, 'Every 2 Hours'),
                (240, 'Every 4 Hours'),
                (360, 'Every 6 Hours'),
                (480, 'Every 8 Hours'),
                (600, 'Every 10 Hours'),
                (720, 'Every 12 Hours'),
                (1440, 'Every Day')
            ]
        )

    def test_25_hours(self):
        with self.assertRaises(ValueError):
            self.setUpMock(1500)
            self.review_frequency_pool.get_form_description(self.cr, self.uid,
                                                            1, context=None)

    def test_0_minutes(self):
        self.setUpMock(0)
        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(form_description[0]['selection'], [])

    def test_no_obs_record(self):
        def mock_activity_browse(*args, **kwargs):
            if len(args) > 2 and args[3] == 9001:
                self.activity.data_ref = None
                return self.activity
            else:
                return mock_activity_browse.origin(*args, **kwargs)

        self.activity_pool._patch_method('browse', mock_activity_browse)
        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(
            form_description[0]['selection'],
            [
                (15, 'Every 15 Minutes'),
                (30, 'Every 30 Minutes'),
                (60, 'Every Hour'),
                (120, 'Every 2 Hours'),
                (240, 'Every 4 Hours'),
                (360, 'Every 6 Hours'),
                (480, 'Every 8 Hours'),
                (600, 'Every 10 Hours'),
                (720, 'Every 12 Hours'),
                (1440, 'Every Day')
            ]
        )

    def test_no_ews(self):

        def mock_no_ews_id(*args, **kwargs):
            return []

        self.activity_pool._patch_method('search', mock_no_ews_id)
        self.activity_pool._patch_method('browse', mock_no_ews_id)

        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(
            form_description[0]['selection'],
            [
                (15, 'Every 15 Minutes'),
                (30, 'Every 30 Minutes'),
                (60, 'Every Hour'),
                (120, 'Every 2 Hours'),
                (240, 'Every 4 Hours'),
                (360, 'Every 6 Hours'),
                (480, 'Every 8 Hours'),
                (600, 'Every 10 Hours'),
                (720, 'Every 12 Hours'),
                (1440, 'Every Day')
            ]
        )