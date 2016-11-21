from openerp.tests.common import TransactionCase


class TestFullObservationSinceRefused(TransactionCase):
    """
    Test that the method to go down the chain of activities returns if a full
    observation has been taken since the supplied activity
    """

    def setUp(self):
        super(TestFullObservationSinceRefused, self).setUp()
        self.activity_model = self.env['nh.activity']
        self.observation_model = self.env['nh.clinical.patient.observation']

        def patch_get_next_obs_activity(*args, **kwargs):
            return []

        self.observation_model._patch_method(
            'get_next_obs_activity', patch_get_next_obs_activity)

        self.first_obs = self.activity_model.new(
            {
                'data_ref': self.observation_model.new(
                    {
                        'partial_reason': 'refused',
                    }
                ),
                'state': 'completed',
                'child_ids': ['child_one']
            }
        )

    def tearDown(self):
        self.observation_model._revert_method('get_next_obs_activity')
        super(TestFullObservationSinceRefused, self).tearDown()

    def test_no_full_observations(self):
        """
        Test that it returns True if no full observations have been taken
        since
        """
        refused = self.observation_model.full_observation_since_refused(
            self.first_obs
        )
        self.assertTrue(False)

    def test_full_observation(self):
        """
        Test that it returns False if there if a full observation has been
        taken since
        """
        self.assertFalse(True)
