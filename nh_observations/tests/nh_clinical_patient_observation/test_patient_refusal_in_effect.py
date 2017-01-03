from openerp.tests.common import TransactionCase


class TestIsPatientRefusalInEffect(TransactionCase):
    """
    Test that the patient_refusal_in_effect method is returning True if
    the patient's last refused observation has had no full observations taken
    since
    """

    def setUp(self):
        super(TestIsPatientRefusalInEffect, self).setUp()
        self.observation_model = self.env['nh.clinical.patient.observation']
        self.activity_model = self.env['nh.activity']
        self.spell_model = self.env['nh.clinical.spell']
        self.transfer_model = self.env['nh.clinical.patient.transfer']

        self.no_obs_called = False
        self.fake_spell_activity_ids = [1]

        def patch_activity_search(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test')
            if test == 'no_spell':
                return []
            if test == 'no_obs' and self.no_obs_called:
                return []
            else:
                self.no_obs_called = True
            return self.fake_spell_activity_ids

        def patch_observation_search(*args, **kwargs):
            test = args[0]._context.get('test')
            if test == 'no_refused_obs':
                return []
            return [self.observation_model.new({})]

        def patch_activity_browse(*args, **kwargs):
            act_id = args[3] if len(args) > 3 else ''
            if act_id in self.fake_spell_activity_ids:
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
            if test == 'open_obs_not_child'\
                    or test == 'transfer_since_refused':
                return [2]
            return [666]

        def patch_patient_monitoring_exception_in_effect(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test')
            if test == 'pme_in_effect':
                return True
            return False

        def patch_patient_was_transferred_after_date(*args, **kwargs):
            self_arg = args[0]
            context = self_arg.env.context
            test = context.get('test')
            if test == 'transfer_since_refused':
                return True
            return False

        self.observation_model._patch_method(
            'get_open_obs_activity',
            patch_get_open_obs_activity
        )
        self.observation_model._patch_method(
            'search', patch_observation_search)
        self.activity_model._patch_method('search', patch_activity_search)
        self.activity_model._patch_method('browse', patch_activity_browse)
        self.spell_model._patch_method(
            'patient_monitoring_exception_in_effect',
            patch_patient_monitoring_exception_in_effect
        )
        self.transfer_model._patch_method(
            'patient_was_transferred_after_date',
            patch_patient_was_transferred_after_date
        )

    def tearDown(self):
        self.observation_model._revert_method('get_open_obs_activity')
        self.observation_model._revert_method('search')
        self.activity_model._revert_method('search')
        self.activity_model._revert_method('browse')
        self.spell_model._revert_method(
            'patient_monitoring_exception_in_effect')
        self.transfer_model._revert_method(
            'patient_was_transferred_after_date')
        super(TestIsPatientRefusalInEffect, self).tearDown()

    def test_no_spell_id(self):
        """
        Test returns False if no spell ID for patient.
        """
        self.assertFalse(self.observation_model
                         .with_context(test='no_spell')
                         .patient_refusal_in_effect(1))

    def test_no_refused_obs(self):
        """
        Test returns False if no refused obs for patient.
        """
        self.assertFalse(self.observation_model
                         .with_context(test='no_refused_obs')
                         .patient_refusal_in_effect(1))

    def test_no_obs_ids(self):
        """
        Test returns False if no observations for spell.
        """
        self.assertFalse(self.observation_model
                         .with_context(test='no_obs')
                         .patient_refusal_in_effect(1))

    def test_open_obs_is_child_of_last_refused(self):
        """
        Test returns True if currently open obs is a child of the last refused
        obs.
        """
        self.assertTrue(self.observation_model
                        .patient_refusal_in_effect(1))

    def test_open_obs_is_not_child_of_last_refused(self):
        """
        Test returns False if currently open obs is not a child of the last
        refused obs.
        """
        self.assertFalse(
            self.observation_model.with_context(test='open_obs_not_child')
                .patient_refusal_in_effect(1)
        )

    def test_patient_monitoring_exception_started(self):
        """
        Test returns False if there is a patient monitoring exception in
        effect.
        """
        self.assertFalse(
            self.observation_model.with_context(test='pme_in_effect')
                .patient_refusal_in_effect(1)
        )

    def test_transfer_since_last_refused(self):
        """
        Test returns False if the patient has been transferred since the last
        refused observation.
        """
        self.assertFalse(
            self.observation_model.with_context(test='transfer_since_refused')
                .patient_refusal_in_effect(1)
        )
