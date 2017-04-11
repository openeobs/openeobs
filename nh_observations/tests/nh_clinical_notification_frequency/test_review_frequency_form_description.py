# coding: utf-8
from openerp.addons.nh_observations import frequencies
from openerp.tests.common import SingleTransactionCase


class TestReviewFrequencyFormDesc(SingleTransactionCase):

    def test_form_description(self):
        review_freq_pool = self.registry('nh.clinical.notification.frequency')
        form_description = review_freq_pool.get_form_description(
            self.cr, self.uid, 1, context=None)

        self.assertEqual(form_description[0]['selection'],
                         frequencies.as_list())
