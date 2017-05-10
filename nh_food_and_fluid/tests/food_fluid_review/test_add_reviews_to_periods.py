from openerp.tests.common import TransactionCase


class TestAddReviewsToPeriods(TransactionCase):
    """
    Test the functionality to add the reviews to for the period dictionaries
    passed to the report
    """

    def setUp(self):
        super(TestAddReviewsToPeriods, self).setUp()
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']

        def patch_get_review_data(*args, **kwargs):
            return None

        self.review_model._patch_method(
            'get_review_data', patch_get_review_data)

    def tearDown(self):
        self.review_model._revert_method('get_review_data')
        super(TestAddReviewsToPeriods, self).tearDown()

    def test_adds_reviews_key_to_periods(self):
        """
        Test that the review key is present in the periods returned by
        get_period_dictionaries
        """
        new_periods = self.review_model.add_reviews_to_periods(1, [{}])
        self.assertTrue('reviews' in new_periods[0])

    def test_has_3pm_review_key(self):
        """
        Test that the 3pm review is present in the reviews for the period
        """
        new_periods = self.review_model.add_reviews_to_periods(1, [{}])
        self.assertTrue(15 in new_periods[0]['reviews'])

    def test_has_6am_review_key(self):
        """
        Test that the 6am review is present in the reviews for the period
        """
        new_periods = self.review_model.add_reviews_to_periods(1, [{}])
        self.assertTrue(6 in new_periods[0]['reviews'])
