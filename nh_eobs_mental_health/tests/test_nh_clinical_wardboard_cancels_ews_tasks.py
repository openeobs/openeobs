from openerp.tests.common import SingleTransactionCase
from openerp.osv import osv


class TestNHClinicalWardBoardCancelsEWSTasks(SingleTransactionCase):
    """
    Test that the open EWS task for a spell is cancelled when pressing obs_stop
    and setting the flag to True
    """

    @classmethod
    def setUpClass(cls):
        super(TestNHClinicalWardBoardCancelsEWSTasks, cls).setUpClass()
        cls.wardboard_model = cls.registry('nh.clinical.wardboard')
        cls.activity_model = cls.registry('nh.activity')

        def patch_wardboard_read(*args, **kwargs):
            return {
                'spell_activity_id': (1, 'Spell/Visit'),
                'patient_id': (1, 'Test Patient')
            }

        def patch_cancel_open_activities(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            output = {
                'cancel_fail': False,
                'cancel_success': True
            }
            if test == 'cancel_success':
                global cancels_ews
                cancels_ews = True
            return output.get(test, [])

        def patch_toggle_obs_stop_flag(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            if test == 'no_cancel':
                return False
            return True

        def patch_cancel_open_ews(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            if test == 'no_cancel':
                global cancel_called
                cancel_called = True
            return patch_cancel_open_ews.origin(*args, **kwargs)

        cls.activity_model._patch_method(
            'cancel_open_activities', patch_cancel_open_activities)
        cls.wardboard_model._patch_method(
            'toggle_obs_stop_flag', patch_toggle_obs_stop_flag)
        cls.wardboard_model._patch_method(
            'cancel_open_ews', patch_cancel_open_ews)
        cls.wardboard_model._patch_method('read', patch_wardboard_read)

    @classmethod
    def tearDownClass(cls):
        super(TestNHClinicalWardBoardCancelsEWSTasks, cls).tearDownClass()
        cls.activity_model._revert_method('cancel_open_activities')
        cls.wardboard_model._revert_method('toggle_obs_stop_flag')
        cls.wardboard_model._revert_method('cancel_open_ews')
        cls.wardboard_model._revert_method('read')

    def test_cancels_open_activities(self):
        self.wardboard_model.toggle_obs_stop(
            self.cr, self.uid, 1337, context={'test': 'cancel_success'})
        self.assertTrue(cancels_ews)

    def test_raises_on_failing_to_cancel(self):
        with self.assertRaises(osv.except_osv):
            self.wardboard_model.toggle_obs_stop(
                self.cr, self.uid, 1337, context={'test': 'cancel_fail'})

    def test_doesnt_cancel_on_restarting_obs(self):
        self.wardboard_model.toggle_obs_stop(
            self.cr, self.uid, 1337, context={'test': 'no_cancel'})
        self.assertFalse('cancel_called' in globals())
