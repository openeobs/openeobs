from openerp.tests.common import SingleTransactionCase


class TestNHeObsAPIGetActiveObservations(SingleTransactionCase):
    """
    Test that setting the obs_stop flag on the patient's spell means no
    observations are active for the patient
    """
    
    @classmethod
    def setUpClass(cls):
        super(TestNHeObsAPIGetActiveObservations, cls).setUpClass()
        cls.spell_model = cls.registry('nh.clinical.spell')
        cls.patient_model = cls.registry('nh.clinical.patient')
        cls.api_model = cls.registry('nh.eobs.api')
        cls.user_model = cls.registry('res.users')
        cls.activity_model = cls.registry('nh.activity')

        def patch_spell_search(*args, **kwargs):
            return [1]

        def patch_spell_read(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test')
            stopped = False
            if test == 'hide_obs':
                stopped = True
            return {
                'obs_stop': stopped
            }

        def patch_activity_search(*args, **kwargs):
            return [1]

        # patch activity search so when super is hit returns active obs list
        cls.activity_model._patch_method('search', patch_activity_search)
        cls.spell_model._patch_method('search', patch_spell_search)
        cls.spell_model._patch_method('read', patch_spell_read)

    @classmethod
    def tearDownClass(cls):
        cls.activity_model._revert_method('search')
        cls.spell_model._revert_method('search')
        cls.spell_model._revert_method('read')
        super(TestNHeObsAPIGetActiveObservations, cls).tearDownClass()

    def test_no_activities_on_obs_stop(self):
        """
        Test that no activities are provided when the obs_stop flag is set on
        the spell
        """
        cr, uid = self.cr, self.uid
        active_obs = self.api_model.get_active_observations(
            cr, uid, 666, context={'test': 'hide_obs'})
        self.assertEqual(active_obs, [])

    def test_has_activities_on_no_obs_stop(self):
        """
        Test that no activities are provided when the obs_stop flag is set on
        the spell
        """
        cr, uid = self.cr, self.uid
        active_obs = self.api_model.get_active_observations(
            cr, uid, 666, context={'test': 'show_obs'})
        self.assertNotEqual(active_obs, [])
