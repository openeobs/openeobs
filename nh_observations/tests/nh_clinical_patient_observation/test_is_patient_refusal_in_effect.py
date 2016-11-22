from openerp.tests.common import TransactionCase


class TestIsPatientRefusalInEffect(TransactionCase):
    """
    Test that the is_patient_refusal_in_effect method is returning True if
    the patient's last refused observation has had no full observations taken
    since
    """

    def setUp(self):
        super(TestIsPatientRefusalInEffect, self).setUp()
        self.observation_model = self.env['nh.clinical.patient.observation']
        self.activity_model = self.env['nh.activity']

        def patch_patient_has_spell(*args, **kwargs):
            return [1]

        def patch_activity_search(*args, **kwargs):
            return [1]

        def patch_activity_browse(*args, **kwargs):
            return [1]

        def patch_full_observation_since_refused(*args, **kwargs):
            return False

        self.observation_model._patch_method(
            'patient_has_spell', patch_activity_browse)
        self.observation_model._patch_method(
            'full_observation_since_refused',
            patch_full_observation_since_refused)
        self.activity_model._patch_method('search', patch_activity_search)
        self.activity_model._patch_method('browse', patch_activity_browse)

    def tearDown(self):
        self.observation_model._revert_method('patient_has_spell')
        self.observation_model._revert_method('full_observation_since_refused')
        self.activity_model._patch_method('search')
        self.activity_model._patch_method('browse')
        super(TestIsPatientRefusalInEffect, self).tearDown()

    def test_no_spell_id(self):
        """
        Test that it returns False is no spell ID for patient
        """
        self.assertFalse(True)

    def test_no_obs_ids(self):
        """
        Test returns False if no observations for spell
        """
        self.assertFalse(True)

    def test_open_obs_is_child_of_refused(self):
        """
        Test returns True if currently open obs is direct child of last refused
        obs
        """
        self.assertTrue(False)

    def test_full_obs_since_refused(self):
        """
        Test returns False if full observation after refused obs
        """
        self.assertFalse(True)

    def test_no_full_obs_since_refused(self):
        """
        Test returns True if no full observation after refused obs
        """
        self.assertTrue(False)

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