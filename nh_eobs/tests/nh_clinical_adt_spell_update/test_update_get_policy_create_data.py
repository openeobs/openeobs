from openerp.tests.common import TransactionCase


class TestGetPolicyCreateData(TransactionCase):
    """
    Test the _get_policy_create_data method of the nh.clinical.adt.spell.update
    model
    """

    def setUp(self):
        super(TestGetPolicyCreateData, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.api_model = self.env['nh.clinical.api']
        self.activity_model = self.env['nh.activity']
        self.test_utils.create_locations()
        self.test_utils.create_users()
        self.test_utils.create_patient()
        self.spell = self.test_utils.admit_patient()

    def get_placement_after_update(self, location_code):
        """
        Send the Spell update message and return any placements after

        :param location_code: Code associated with the location
        :type location_code: basestring
        :return: Placement records
        """
        self.api_model.admit_update(
            self.test_utils.patient.other_identifier,
            {
                'given_name': 'Test',
                'family_name': 'McTestersen',
                'location': location_code
            }
        )
        return self.activity_model.search(
            [
                ['state', 'not in', ['completed', 'cancelled']],
                ['data_model', '=', 'nh.clinical.patient.placement'],
                ['patient_id', '=', self.test_utils.patient.id]
            ]
        )

    def test_update_with_bed(self):
        """
        Test that on the patient being in the ward and the patient's spell
        being updated with a bed location that the patient is moved into the
        bed and the placement is generated and not completed, there's a
        potential to have two patients in a bed.

        Raised EOBS-2297 to question this logic as it breaks the system.
        """
        placement = self.get_placement_after_update(self.test_utils.bed.code)
        self.assertEqual(
            placement.data_ref.suggested_location_id,
            self.test_utils.bed
        )

    def test_update_with_ward(self):
        """
        Test that when the patient is on a ward and the patient's spell is
        updated with a ward location that the policy isn't triggered
        """
        initial_placement = self.activity_model.search(
            [
                ['state', 'not in', ['completed', 'cancelled']],
                ['data_model', '=', 'nh.clinical.patient.placement'],
                ['patient_id', '=', self.test_utils.patient.id]
            ]
        )
        placement = self.get_placement_after_update(self.test_utils.ward.code)
        self.assertEqual(placement.id, initial_placement.id)
