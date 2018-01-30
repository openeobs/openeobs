from openerp.tests.common import TransactionCase


class TestGetPolicyCreateData(TransactionCase):
    """
    Test the _get_policy_create_data method on the
    nh.clinical.patient.discharge model
    """

    def setUp(self):
        """ set up the tests """
        super(TestGetPolicyCreateData, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.activity_model = self.env['nh.activity']
        self.test_utils.admit_and_place_patient()

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

    def test_bed_location_unoccupied(self):
        """
        Test that no placement is created if the bed isn't taken at
        the time of the discharge being cancelled that the patient is put back
        into the bed
        """
        self.test_utils.discharge_patient()
        self.test_utils.cancel_patient_discharge()
        placement = self.get_placement(self.test_utils.patient.id)
        self.assertFalse(placement)

    def test_bed_location_occupied(self):
        """
        Test that the returned suggested_location_id is the ID of the ward that
        the bed is in if the patient is in a bed
        """
        self.test_utils.discharge_patient()
        patient = self.test_utils.create_and_register_patient()
        self.test_utils.admit_patient(
            hospital_number=patient.other_identifier,
            patient_id=patient.id,
            location_code=self.test_utils.ward.code
        )
        self.test_utils.place_patient(
            placement_activity_id=self.get_placement(patient.id).id)
        self.test_utils.cancel_patient_discharge()
        placement = self.get_placement(self.test_utils.patient.id)
        self.assertEqual(
            placement.data_ref.suggested_location_id.id,
            self.test_utils.ward.id
        )

    def test_ward_location(self):
        """
        Test that the returned suggested_location_id is the ID of the ward if
        the patient is in a ward
        """
        self.test_utils.transfer_patient(self.test_utils.other_ward.code)
        self.test_utils.discharge_patient()
        self.test_utils.cancel_patient_discharge()
        placement = self.get_placement(self.test_utils.patient.id)
        self.assertEqual(
            placement.data_ref.suggested_location_id.id,
            self.test_utils.other_ward.id
        )
