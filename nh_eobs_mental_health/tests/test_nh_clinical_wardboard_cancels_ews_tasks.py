from openerp.tests.common import TransactionCase
from openerp.osv import osv


class TestNHClinicalWardBoardCancelsEWSTasks(TransactionCase):
    """
    Test that the open EWS task for a spell is cancelled when pressing obs_stop
    and setting the flag to True
    """

    @classmethod
    def setUpClass(cls):
        super(TestNHClinicalWardBoardCancelsEWSTasks, cls).setUpClass()
        cls.foo = 1

    # @classmethod
    # def setUpClass(cls):
    #     super(TestNHClinicalWardBoardCancelsEWSTasks, cls).setUpClass()
    #     cls.wardboard_model = cls.registry('nh.clinical.wardboard')
    #     cls.activity_model = cls.registry('nh.activity')
    #     cls.spell_model = cls.registry('nh.clinical.spell')
    #     cls.ews_model = cls.registry('nh.clinical.patient.observation.ews')
    #     cls.patient_model = cls.registry('nh.clinical.patient')
    #
    #     def patch_cancel_open_activities(*args, **kwargs):
    #         context = kwargs.get('context', {})
    #         test = context.get('test', '')
    #         output = {
    #             'cancel_fail': False,
    #             'cancel_success': True
    #         }
    #         if test == 'cancel_success':
    #             global cancels_ews
    #             cancels_ews = True
    #         return output.get(test, [])
    #
    #     def patch_toggle_obs_stop_flag(*args, **kwargs):
    #         context = kwargs.get('context', {})
    #         test = context.get('test', '')
    #         if test == 'no_cancel':
    #             return False
    #         return True
    #
    #     def patch_spell_search(*args, **kwargs):
    #         return [1]
    #
    #     def patch_cancel_open_ews(*args, **kwargs):
    #         context = kwargs.get('context', {})
    #         test = context.get('test', '')
    #         if test == 'no_cancel':
    #             global cancel_called
    #             cancel_called = True
    #         return patch_cancel_open_ews.origin(*args, **kwargs)
    #
    #     def patch_activity_create(*args, **kwargs):
    #         context = kwargs.get('context', {})
    #         test = context.get('test', '')
    #         if test == 'create_success':
    #             global ews_create_called
    #             ews_create_called = True
    #             return 1
    #         return False
    #
    #     def patch_activity_schedule(*args, **kwargs):
    #         return True
    #
    #     cls.activity_model._patch_method(
    #         'cancel_open_activities', patch_cancel_open_activities)
    #     cls.wardboard_model._patch_method(
    #         'set_obs_stop_flag', patch_toggle_obs_stop_flag)
    #     cls.wardboard_model._patch_method(
    #         'cancel_open_ews', patch_cancel_open_ews)
    #     cls.spell_model._patch_method('search', patch_spell_search)
    #     cls.ews_model._patch_method(
    #         'create_activity', patch_activity_create)
    #     cls.activity_model._patch_method('schedule', patch_activity_schedule)
    #
    def setUp(self):
        super(TestNHClinicalWardBoardCancelsEWSTasks, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.wardboard_model = self.env['nh.clinical.wardboard']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {
                'patient_id': self.patient.id,
                'pos_id': 1
            }
        )
        # self.activity = self.activity_model.browse(self.activity_id)
        # self.spell = self.activity.spell_activity_id.data_ref

        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient
        })

        self.foo = 2

    @classmethod
    def tearDownClass(cls):
        super(TestNHClinicalWardBoardCancelsEWSTasks, cls).tearDownClass()
        cls.activity_model._revert_method('cancel_open_activities')
        cls.wardboard_model._revert_method('set_obs_stop_flag')
        cls.wardboard_model._revert_method('cancel_open_ews')
        cls.spell_model._revert_method('search')
        cls.ews_model._revert_method('create_activity')
        cls.activity_model._revert_method('schedule')

    def test_cancels_open_activities(self):
        self.env.context = {'test': 'cancel_success'}
        self.wardboard.toggle_obs_stop()
        self.assertTrue(cancels_ews)

    def test_raises_on_failing_to_cancel(self):
        with self.assertRaises(osv.except_osv):
            self.env.context = {'test': 'cancel_fail'}
            self.wardboard.toggle_obs_stop()

    def test_doesnt_cancel_on_restarting_obs(self):
        self.env.context = {'test': 'no_cancel'}
        self.wardboard.spell_activity_id.data_ref.obs_stop = True
        self.wardboard.toggle_obs_stop()
        self.assertFalse('cancel_called' in globals())
