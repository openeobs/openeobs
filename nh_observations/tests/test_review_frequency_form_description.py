# coding: utf-8
from openerp.tests.common import SingleTransactionCase


class TestReviewFrequencyFormDesc(SingleTransactionCase):

    def test_form_description(self):
        review_freq_pool = self.registry('nh.clinical.notification.frequency')
        form_description = review_freq_pool.get_form_description(
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
