from openerp.tests.common import TransactionCase


class TestViewDescription(TransactionCase):
    """
    Test that the view description contains the review task if a review task
    is open for the patient
    """

    def test_review_task_include_when_task_open(self):
        """
        Test that the review task is included in the view description if there
        is a currently open review task
        """
        self.assertTrue(False)

    def test_no_review_when_no_open_task(self):
        """
        Test that the review task is not inclulded if it's been closed
        """
        self.assertTrue(False)
