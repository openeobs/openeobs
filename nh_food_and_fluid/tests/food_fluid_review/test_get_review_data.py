from openerp.tests.common import TransactionCase


class TestGetReviewData(TransactionCase):
    """
    Test functionality of getting review data for the period up to the 
    review trigger time
    """

    def setUp(self):
        super(TestGetReviewData, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.