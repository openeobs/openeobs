from openerp.tests.common import TransactionCase


class TestGetPolicyCreateData(TransactionCase):
    """
    Test the _get_policy_create_data method for the
    nh.clinical.patient.admission model
    """

    def setUp(self):
        """ Set up the tests """
        super(TestGetPolicyCreateData, self).setUp()

    def test_suggested_location_id(self):
        """
        Test that _get_polcu_create_data returns a dictionary with the
        suggested_location_id in it
        """
        self.assertTrue(False)
