from openerp.tests.common import TransactionCase


class TestGetEscalationTasksForScore(TransactionCase):
    """
    Test That get_escalation_tasks_for_score returns the correct escalation
    tasks for the score supplied
    """

    def setUp(self):
        super(TestGetEscalationTasksForScore, self).setUp()
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']

    def test_raises_on_score_out_of_bounds(self):
        """
        Test method raises an error if score passed is out of bounds
        """
        with self.assertRaises(ValueError) as error:
            self.review_model.get_escalation_tasks_for_score(666)
        self.assertEqual(
            error.exception.message, 'Supplied score out of range')

    def test_tasks_for_zero_score(self):
        """
        Test method returns the correct tasks for score of 0
        """
        tasks = self.review_model.get_escalation_tasks_for_score(0)
        self.assertEqual(
            tasks,
            [
                'Confirm adequate intake'
            ])

    def test_tasks_for_one_score(self):
        """
        Test method returns the correct tasks for score of 1
        """
        tasks = self.review_model.get_escalation_tasks_for_score(1)
        self.assertEqual(
            tasks,
            [
                'Encourage fluid intake to above 1500ml',
                'Keep monitoring',
                'Inform Shift Coordinator'
            ])

    def test_tasks_for_two_score(self):
        """
        Test method returns the correct tasks for score of 2
        """
        tasks = self.review_model.get_escalation_tasks_for_score(2)
        self.assertEqual(
            tasks,
            [
                'Encourage hourly fluids immediately',
                'Inform Shift Coordinator'
            ])

    def test_tasks_for_three_score(self):
        """
        Test method returns the correct tasks for score of 3
        """
        tasks = self.review_model.get_escalation_tasks_for_score(3)
        self.assertEqual(
            tasks,
            [
                'Inform medical staff immediately'
            ])
