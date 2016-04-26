# coding: utf-8
from openerp.tests.common import SingleTransactionCase
from mock import MagicMock


class TestReviewFrequency(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestReviewFrequency, cls).setUpClass()
        cls.review_frequency_pool = cls.registry('nh.clinical.notification.frequency')
        cls.activity_pool = cls.registry('nh.activity')

        def mock_ews_id(*args, **kwargs):
            return [1]
        cls.activity_pool._patch_method('search', mock_ews_id)

    @classmethod
    def tearDownClass(cls):
        cls.activity_pool._revert_method('search')
        super(TestReviewFrequency, cls).tearDownClass()

    def test_15_minutes(self):
        meh = self.activity_pool.create(self.cr, self.uid, {
            'data_model': 'nh.clinical.patient.observation'})

        def mock_activity_browse(*args, **kwargs):
            self.activity_pool.read(self.cr, self.uid, meh)
            meh.data_ref.frequency = 15
            return meh
        self.activity_pool._patch_method('browse', mock_activity_browse)

        form_description = self.review_frequency_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(
            form_description[0]['selection'],
            [(15, 'Every 15 Minutes')]
        )