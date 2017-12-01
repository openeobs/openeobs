from openerp.tests.common import TransactionCase


class TestGetFilename(TransactionCase):
    """
    Test the filename that is returned for the file that will be saved to the
    database and filesystem
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestGetFilename, self).setUp()
        self.api_model = self.env['nh.eobs.api']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()

    def test_no_spell_id(self):
        """
        Test that when no spell_id is passed that it returns False
        """
        self.assertFalse(self.api_model.get_filename())

    def test_patient_in_bed(self):
        """
        Test that when patient is in a bed that it gets the ward name by going
        up the chain of locations
        """
        self.assertEqual(
            '{ward}_{surname}_{identifier}_{spell}'.format(
                ward=self.test_utils.ward.display_name,
                surname=self.test_utils.patient.family_name,
                identifier=self.test_utils.patient.patient_identifier,
                spell=self.test_utils.spell.id
            ),
            self.api_model.get_filename(self.test_utils.spell.id)
        )

    def test_patient_on_ward(self):
        """
        Test that when patient is on a ward that it gets the ward name from the
        current location
        """
        self.test_utils.transfer_patient(self.test_utils.other_ward.code)
        self.assertEqual(
            '{ward}_{surname}_{identifier}_{spell}'.format(
                ward=self.test_utils.other_ward.display_name,
                surname=self.test_utils.patient.family_name,
                identifier=self.test_utils.patient.patient_identifier,
                spell=self.test_utils.spell.id
            ),
            self.api_model.get_filename(self.test_utils.spell.id)
        )

    def test_patient_name_format(self):
        """
        Test that when the patient has non-alphanumeric characters in their
        name (i.e. they're surname is O'Neill ) then this is removed from the
        string
        """
        self.test_utils.patient.write({'family_name': 'O\'Neill'})
        self.assertEqual(
            '{ward}_ONeill_{identifier}_{spell}'.format(
                ward=self.test_utils.ward.display_name,
                surname=self.test_utils.patient.family_name,
                identifier=self.test_utils.patient.patient_identifier,
                spell=self.test_utils.spell.id
            ),
            self.api_model.get_filename(self.test_utils.spell.id)
        )
