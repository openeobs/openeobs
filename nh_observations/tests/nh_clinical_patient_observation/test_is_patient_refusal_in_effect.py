from openerp.tests.common import TransactionCase


class TestIsPatientRefusalInEffect(TransactionCase):
    """
    Test that the is_patient_refusal_in_effect method is returning True if
    the patient's last refused observation has had no full observations taken
    since
    """





    def test_no_full_observations(self):
        """
        Test that it's returning True if no full observations have been taken
        """

        self.assertTrue(False)

    def test_full_observation(self):
        """
        Test that it's returning False if a full observation has been taken
        """
        self.assertFalse(True)