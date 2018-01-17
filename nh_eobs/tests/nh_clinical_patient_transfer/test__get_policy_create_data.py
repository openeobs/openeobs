from openerp.tests.common import TransactionCase


class TestGetPolicyCreateData(TransactionCase):
    """
    Test the _get_policy_create_data method of the nh.clinical.patient.transfer
    model
    """

    def setUp(self):
        """ Set up the tests """
        super(TestGetPolicyCreateData, self).setUp()

    def test_case_1(self):
        """
        Test that when passed case 1 that it returns the location ID associated
        with the activity
        """
        self.assertTrue(False)

    def test_case_2_bed(self):
        """
        Test that when passed case 2 and that location is a bed that it gets
        the ward the bed is in and returns that location ID
        """
        self.assertTrue(False)

    def test_case_2_ward(self):
        """
        Test that when passed case 2 and that location is a ward that it
        returns that location ID
        """
        self.assertTrue(False)
