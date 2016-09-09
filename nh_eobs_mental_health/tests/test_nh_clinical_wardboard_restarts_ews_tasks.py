from openerp.tests.common import SingleTransactionCase


class TestNHClinicalWardBoardRestartsEWSTasks(SingleTransactionCase):
    """
    Test that a new EWS task is generated when the observations are restarted
    """

    @classmethod
    def setUpClass(cls):
        super(TestNHClinicalWardBoardRestartsEWSTasks, cls).setUpClass()
        cls.wardboard_model = cls.registry('nh.clinical.wardboard')
        cls.activity_model = cls.registry('nh.activity')
        cls.spell_model = cls.registry('nh.clinical.spell')
        cls.ews_model = cls.registry('nh.clinical.patient.observation.ews')
        cls.api_model = cls.registry('nh.clinical.api')

        def patch_wardboard_read(*args, **kwargs):
            return {
                'spell_activity_id': (1, 'Spell/Visit'),
                'patient_id': (1, 'Test Patient')
            }

        def patch_toggle_obs_stop_flag(*args, **kwargs):
            return False

        def patch_spell_search(*args, **kwargs):
            return [1]

        def patch_activity_create(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            if test == 'create_success':
                global ews_create_called
                ews_create_called = True
                return 1
            return False

        def patch_activity_schedule(*args, **kwargs):
            return True

        def patch_api_freq_change(*args, **kwargs):
            return True

        cls.wardboard_model._patch_method(
            'set_obs_stop_flag', patch_toggle_obs_stop_flag)
        cls.wardboard_model._patch_method('read', patch_wardboard_read)
        cls.spell_model._patch_method('search', patch_spell_search)
        cls.ews_model._patch_method(
            'create_activity', patch_activity_create)
        cls.activity_model._patch_method('schedule', patch_activity_schedule)
        cls.api_model._patch_method('change_activity_frequency',
                                    patch_api_freq_change)

    @classmethod
    def tearDownClass(cls):
        super(TestNHClinicalWardBoardRestartsEWSTasks, cls).tearDownClass()
        cls.wardboard_model._revert_method('set_obs_stop_flag')
        cls.wardboard_model._revert_method('read')
        cls.spell_model._revert_method('search')
        cls.ews_model._revert_method('create_activity')
        cls.activity_model._revert_method('schedule')
        cls.api_model._revert_method('change_activity_frequency')

    def test_schedules_new_ews(self):
        """
        Test that on when obs_stop flag is set to False that a new EWS
        observation is scheduled for 1 hours time
        :return:
        """
        self.wardboard_model.toggle_obs_stop(
            self.cr, self.uid, 1337, context={'test': 'create_success'})
        self.assertTrue(ews_create_called)


