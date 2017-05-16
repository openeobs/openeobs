from openerp.tests.common import TransactionCase
from datetime import datetime
import pytz


class TestGetReviewEnd(TransactionCase):
    """
    Test method to get review end from datetime representing the start of the
    F&F period and the trigger time for the review
    """

    def setUp(self):
        super(TestGetReviewEnd, self).setUp()
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.start_datetime = datetime(1988, 1, 12, 7, 0, 0, tzinfo=pytz.utc)

    def test_gets_review_same_day(self):
        """
        Test if trigger time is 6am that it gets review end as same day at
        14:59
        """
        review_end = self.review_model.get_review_end(self.start_datetime, 6)
        self.assertEqual(review_end, '1988-01-12 14:59:00')

    def test_gets_review_next_day(self):
        """
        Test if trigger time is 3pm that it gets review end as next day at
        05:59
        """
        review_end = self.review_model.get_review_end(self.start_datetime, 15)
        self.assertEqual(review_end, '1988-01-13 05:59:00')
