from openerp.tests.common import TransactionCase
from openerp.osv import osv


class TestNHClinicalWardBoardCancelsEWSTasks(TransactionCase):
    """
    Test that the open EWS task for a spell is cancelled when pressing obs_stop
    and setting the flag to True
    """

    def setUp(self):
        super(TestNHClinicalWardBoardCancelsEWSTasks, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        self.pme_reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.pme_model = self.env['nh.clinical.patient_monitoring_exception']

        # Create wardboard
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

        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient
        })

        self.cancel_reason = self.pme_reason_model.browse([1])

        def patch_cancel_open_activities(*args, **kwargs):
            context = args[0]._context
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

        def patch_pme_create_activity(*args, **kwargs):
            return 'This_is_not_an_id'

        def patch_pme_start(*args, **kwargs):
            return True

        def patch_activity_browse(*args, **kwargs):
            if len(args) > 1 and args[1] == 'This_is_not_an_id':
                return self.activity_model.new({})
            return patch_activity_browse.origin(*args, **kwargs)

        def patch_cancel_open_ews(*args, **kwargs):
            context = kwargs.get('context', {})
            test = context.get('test', '')
            if test == 'no_cancel':
                global cancel_called
                cancel_called = True
            return patch_cancel_open_ews.origin(*args, **kwargs)

        self.activity_model._patch_method(
            'cancel_open_activities', patch_cancel_open_activities)
        self.wardboard_model._patch_method(
            'set_obs_stop_flag', patch_toggle_obs_stop_flag)
        self.wardboard_model._patch_method(
            'cancel_open_ews', patch_cancel_open_ews)
        self.pme_model._patch_method(
            'create_activity', patch_pme_create_activity
        )
        self.pme_model._patch_method('start', patch_pme_start)
        self.activity_model._patch_method('browse', patch_activity_browse)

    def tearDown(self):
        super(TestNHClinicalWardBoardCancelsEWSTasks, self).tearDown()
        self.activity_model._revert_method('cancel_open_activities')
        self.wardboard_model._revert_method('set_obs_stop_flag')
        self.wardboard_model._revert_method('cancel_open_ews')
        self.pme_model._revert_method('create_activity')
        self.pme_model._revert_method('start')
        self.activity_model._revert_method('browse')

    def test_cancels_open_activities(self):
        self.env.context = {'test': 'cancel_success'}
        self.wardboard.start_patient_monitoring_exception(
            self.cancel_reason,
            self.wardboard.spell_activity_id.data_ref.id,
            self.wardboard.spell_activity_id.id
        )
        self.assertTrue(cancels_ews)

    def test_raises_on_failing_to_cancel(self):
        with self.assertRaises(osv.except_osv):
            self.env.context = {'test': 'cancel_fail'}
            self.wardboard.start_patient_monitoring_exception(
            self.cancel_reason,
            self.wardboard.spell_activity_id.data_ref.id,
            self.wardboard.spell_activity_id.id
        )
