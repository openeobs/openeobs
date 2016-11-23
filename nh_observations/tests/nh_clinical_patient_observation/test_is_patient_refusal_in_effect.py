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
        self.no_obs_called = False

        def patch_activity_search(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test')
            if test == 'no_spell':
                return []
            if test == 'no_obs' and self.no_obs_called:
                return []
            else:
                self.no_obs_called = True
            return ['activities']

        def patch_observation_search(*args, **kwargs):
            test = args[0]._context.get('test')
            if test == 'no_refused_obs':
                return []
            return [self.observation_model.new({})]

        def patch_activity_browse(*args, **kwargs):
            act_id = args[3] if len(args) > 3 else ''
            if act_id == 'activities':
                obs = self.activity_model.new(
                    {
                        'data_ref': self.observation_model.new({}),
                        'state': 'completed',
                        'child_ids': [666]
                    }
                )
                return obs
            return patch_activity_browse.origin(*args, **kwargs)

        def patch_get_open_obs_activity(*args, **kwargs):
            test = args[0]._context.get('test')
            if test == 'no_open_obs':
                return []
            if test == 'open_obs_not_child':
                return [2]
            return [666]

        def patch_full_observation_since_refused(*args, **kwargs):
            return 'full_observation_since_refused_called'

        self.observation_model._patch_method(
            'full_observation_since_refused',
            patch_full_observation_since_refused)
        self.observation_model._patch_method(
            'get_open_obs_activity',
            patch_get_open_obs_activity
        )
        self.observation_model._patch_method(
            'search', patch_observation_search)
        self.activity_model._patch_method('search', patch_activity_search)
        self.activity_model._patch_method('browse', patch_activity_browse)

    def tearDown(self):
        self.observation_model._revert_method('full_observation_since_refused')
        self.observation_model._revert_method('get_open_obs_activity')
        self.observation_model._revert_method('search')
        self.activity_model._revert_method('search')
        self.activity_model._revert_method('browse')
        super(TestIsPatientRefusalInEffect, self).tearDown()

    def test_no_spell_id(self):
        """
        Test that it returns False is no spell ID for patient
        """
        self.assertFalse(
            self.observation_model
                .with_context(test='no_spell')
                .is_patient_refusal_in_effect(1))

    def test_no_refused_obs(self):
        """
        Test that it returns False if no refused obs for patient
        """
        self.assertFalse(
            self.observation_model
                .with_context(test='no_refused_obs')
                .is_patient_refusal_in_effect(1))

    def test_no_obs_ids(self):
        """
        Test returns False if no observations for spell
        """
        self.assertFalse(
            self.observation_model
                .with_context(test='no_obs')
                .is_patient_refusal_in_effect(1))

    def test_no_open_obs(self):
        """
        Test returns True if currently open obs is direct child of last refused
        obs
        """
        self.assertEqual(
            self.observation_model
                .with_context(test='no_open_obs')
                .is_patient_refusal_in_effect(1),
            'full_observation_since_refused_called'
        )

    def test_open_obs_child(self):
        """
        Test returns True if currently open obs is direct child of last refused
        obs
        """
        self.assertEqual(
            self.observation_model
                .with_context(test='open_obs_not_child')
                .is_patient_refusal_in_effect(1),
            'full_observation_since_refused_called'
        )

    def test_open_obs_is_child_of_refused(self):
        """
        Test returns True if currently open obs is direct child of last refused
        obs
        """
        self.assertTrue(
            self.observation_model
                .with_context(test='open_obs_is_child')
                .is_patient_refusal_in_effect(1)
        )
