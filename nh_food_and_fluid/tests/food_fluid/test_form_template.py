from openerp.tests.common import TransactionCase


class TestFormTemplate(TransactionCase):
    """
    Test that the form template is rendered with and without the review 
    task if there is an open review task for the patient
    """

    def test_review_task_present_when_task_open(self):
        """
        Test that the review task is included in the template if there is a 
        currently open review task for the patient
        """
        self.assertTrue(False)

    def test_review_task_not_present_when_closed(self):
        """
        Test that the review task is not included in the template if there
        is no currently open review task for the patient
        """
        self.assertTrue(False)
