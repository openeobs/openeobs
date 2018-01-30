from openerp.tests.common import TransactionCase


class TestGetPolicyCreateData(TransactionCase):
    """
    Test the _get_policy_create_data method of the nh.clinical.patient.transfer
    model
    """

    def setUp(self):
        """ Set up the tests """
        super(TestGetPolicyCreateData, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.activity_model = self.env['nh.activity']
        self.test_utils.admit_and_place_patient()
        self.test_utils.transfer_patient(
            location_code=self.test_utils.other_ward.code)

    def get_placement(self, patient_id):
        """
        Return the placement for the patient

        :param patient_id: ID of the patient to search for placements for
        :return: Placement records found
        """
        return self.activity_model.search(
            [
                ['patient_id', '=', patient_id],
                ['state', 'not in', ['completed', 'cancelled']],
                ['data_model', '=', 'nh.clinical.patient.placement']
            ]
        )

    def test_case_1(self):
        """
        Test that when passed case 1 that it returns the location ID associated
        with the activity.

        Case 1 is carried out on transfer so will create a placement in the
        ward that the patient is being transferred to
        """
        placement = self.get_placement(self.test_utils.patient.id)
        self.assertEqual(
            placement.data_ref.suggested_location_id.id,
            self.test_utils.other_ward.id
        )

    def test_case_2_bed_unoccupied(self):
        """
        Test that when passed case 2 and that location is a bed that it gets
        the ward the bed is in and returns that location ID

        Case 2 is carried out on cancel_transfer so will not create a patient
        when the patient's original bed is available
        """
        self.test_utils.cancel_patient_transfer()
        placement = self.get_placement(self.test_utils.patient.id)
        self.assertFalse(placement)

    def test_case_2_bed_occupied(self):
        """
        Test that when passed case 2 and that location is a bed that it gets
        the ward the bed is in and returns that location ID

        Case 2 is carried out on cancel_transfer so will not create a patient
        when the patient's original bed is available
        """
        patient = self.test_utils.create_and_register_patient()
        self.test_utils.admit_patient(
            hospital_number=patient.other_identifier,
            patient_id=patient.id,
            location_code=self.test_utils.ward.code
        )
        self.test_utils.place_patient(
            placement_activity_id=self.get_placement(patient.id).id)
        self.test_utils.cancel_patient_transfer()
        placement = self.get_placement(self.test_utils.patient.id)
        self.assertEqual(
            placement.data_ref.suggested_location_id.id,
            self.test_utils.ward.id
        )

    def test_case_2_ward(self):
        """
        Test that when passed case 2 and that location is a ward that it
        returns that location ID

        Case 2 is carried out on cancel_transfer so will create a placement
        in the original ward the patient was in
        """
        self.test_utils.transfer_patient(
            location_code=self.test_utils.ward.code)
        self.test_utils.cancel_patient_transfer()
        placement = self.get_placement(self.test_utils.patient.id)
        self.assertEqual(
            placement.data_ref.suggested_location_id.id,
            self.test_utils.other_ward.id
        )
