from openerp.tests.common import TransactionCase


class TestGetPolicyCreateData(TransactionCase):
    """
    Test the _get_policy_create_data method for the
    nh.clinical.patient.admission model
    """

    def setUp(self):
        """ Set up the tests """
        super(TestGetPolicyCreateData, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.placement_model = self.env['nh.clinical.patient.placement']
        self.test_utils.create_locations()
        self.test_utils.create_users()
        self.test_utils.create_patient()
        self.test_utils.admit_patient()

    def test_suggested_location_id(self):
        """
        Test that _get_policy_create_data returns a dictionary with the
        suggested_location_id in it
        """
        placement = self.placement_model.search(
            [
                ['patient_id', '=', self.test_utils.patient.id]
            ]
        )
        self.assertEqual(
            placement.suggested_location_id.id,
            self.test_utils.ward.id
        )
