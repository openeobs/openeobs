from openerp.tests.common import TransactionCase
from openerp.addons.nh_eobs_api.controllers.route_api import NH_API


class TestGetNextAction(TransactionCase):
    """
    Test that get_next_action on route_api controller returns the correct
    action
    """

    def test_returns_task_when_taskId_present(self):
        """
        Test that when taskId is in the data dict that it returns the
        task action
        """
        data = {
            'taskId': 1
        }
        next_action = NH_API().get_next_action(data)
        self.assertEqual(next_action, 'json_task_form_action')

    def test_returns_patient_when_taskId_not_present(self):
        """
        Test that when taskId is not present it returns patient action
        """
        data = {}
        next_action = NH_API().get_next_action(data)
        self.assertEqual(next_action, 'json_patient_form_action')
