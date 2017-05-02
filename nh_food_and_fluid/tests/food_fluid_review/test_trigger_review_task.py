from openerp.tests.common import TransactionCase


class TestTriggerReviewTask(TransactionCase):
    """
    Test that the trigger review task method is only called when it's the
    correct time and the patient has an active F&F period
    """

    def test_not_active_correct_time(self):
        """
        Test that task is not created when F&F period is not active but
        is the correct time
        """
        self.assertTrue(False)

    def test_active_correct_time(self):
        """
        Test that task is created when F&F period is active and is the correct
        time
        """
        self.assertTrue(False)

    def test_not_active_incorrect_time(self):
        """
        Test that task is not created when F&F is not active and is not the
        correct time
        """
        self.assertTrue(False)

    def test_active_incorrect_time(self):
        """
        Test that task is not created when F&F is active but is not the correct
        time
        """
        self.assertTrue(False)

    def test_3pm_task_name(self):
        """
        Test that the 3pm task name is 'F&F - 3pm Fluid Intake Review'
        """
        self.assertTrue(False)

    def test_6am_task_name(self):
        """
        Test that the 6am task name is 'F&F - 6am Fluid Intake Review'
        """
        self.assertTrue(False)
