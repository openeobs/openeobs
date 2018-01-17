from openerp.tests.common import TransactionCase


class TestGetPolicyCreateData(TransactionCase):
    """
    Test the _get_policy_create_data method on the
    nh.clinical.patient.discharge model
    """

    def setUp(self):
        """ set up the tests """
        super(TestGetPolicyCreateData, self).setUp()

    def test_bed_location(self):
        """
        Test that the returned suggested_location_id is the ID of the ward that
        the bed is in if the patient is in a bed
        """
        self.assertTrue(False)

    def test_ward_location(self):
        """
        Test that the returned suggested_location_id is the ID of the ward if
        the patient is in a ward
        """
        self.assertTrue(False)
