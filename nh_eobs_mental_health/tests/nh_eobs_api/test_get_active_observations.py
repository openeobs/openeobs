from openerp.tests.common import TransactionCase


class TestNHeObsAPIGetActiveObservations(TransactionCase):
    """
    Test that setting the obs_stop flag on the patient's spell means no
    observations are active for the patient
    """

    def setUp(self):
        super(TestNHeObsAPIGetActiveObservations, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.api_model = self.env['nh.eobs.api']

    def call_test(self):
        self.obs_list = self.api_model.get_active_observations(
            self.patient.id)

    def test_populated_list_when_not_on_obs_stop(self):
        """
        Test that the gcs dict is removed from the returned list
        """
        self.call_test()
        self.assertGreater(len(self.obs_list), 0)

    def test_empty_list_on_obs_stop(self):
        """
        Test that no observations are displayed when obs_stop flag is set to
        True
        """
        self.test_utils_model.start_pme()
        self.call_test()
        self.assertEqual(self.obs_list, [])
