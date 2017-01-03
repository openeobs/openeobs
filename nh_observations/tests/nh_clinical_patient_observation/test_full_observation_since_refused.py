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

        self.obs_refused = self.activity_model.new(
            {
                'data_ref': self.observation_model.new(
                    {
                        'partial_reason': 'refused',
                    }
                ),
                'state': 'completed',
                'child_ids': ['no_child']
            }
        )

        self.obs_full = self.activity_model.new(
            {
                'data_ref': self.observation_model.new({}),
                'state': 'completed',
                'child_ids': ['no_child']
            }
        )

        self.obs_partial = self.activity_model.new(
            {
                'data_ref': self.observation_model.new(
                    {
                        'partial_reason': 'patient_away_from_bed',
                    }
                ),
                'state': 'completed',
                'child_ids': ['no_child']
            }
        )

        self.scheduled_obs = self.activity_model.new({
            'data_ref': self.observation_model.new({}),
            'state': 'scheduled',
            'child_ids': []
        })

        def patch_get_next_obs_activity(*args, **kwargs):
            activity = args[1]
            child_id = activity.child_ids.id
            options = {
                'no_child': self.scheduled_obs,
                'refused_child': self.obs_refused,
                'full_child': self.obs_full,
                'partial_child': self.obs_partial
            }
            return options.get(child_id)

        self.observation_model._patch_method(
            'get_next_obs_activity', patch_get_next_obs_activity)

    def tearDown(self):
        self.observation_model._revert_method('get_next_obs_activity')
        super(TestFullObservationSinceRefused, self).tearDown()

    def test_only_refused(self):
        """
        Test that it returns False if no observations have been taken
        since the refused.
        """
        self.assertFalse(self.observation_model.full_observation_since_refused(
            self.obs_refused
        ))

    def test_refused_then_partial(self):
        """
        Test that it returns False if no full observations have been taken
        since a refused.
        """
        refused = self.activity_model.new(
            {
                'data_ref': self.observation_model.new(
                    {
                        'partial_reason': 'refused',
                    }
                ),
                'state': 'completed',
                'child_ids': ['partial_child']
            }
        )
        self.assertFalse(self.observation_model.full_observation_since_refused(
            refused
        ))

    def test_refused_then_full(self):
        """
        Test that it returns True if full observations have been taken
        since the refused.
        """
        refused = self.activity_model.new(
            {
                'data_ref': self.observation_model.new(
                    {
                        'partial_reason': 'refused',
                    }
                ),
                'state': 'completed',
                'child_ids': ['full_child']
            }
        )
        self.assertTrue(self.observation_model.full_observation_since_refused(
            refused
        ))

    def test_only_full(self):
        """
        Test that it returns True if the initial observation passed is not
        refused but full.
        """
        self.assertTrue(self.observation_model.full_observation_since_refused(
            self.obs_full
        ))

    def test_only_partial(self):
        """
        Test that it returns False if the initial observation passed is not
        refused but another partial.
        """
        self.assertFalse(self.observation_model.full_observation_since_refused(
            self.obs_partial
        ))
