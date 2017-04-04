# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class GetReportEntryDictionary(TransactionCase):

    def setUp(self):
        super(GetReportEntryDictionary, self).setUp()

        nurse_user_id = 1
        nurse_name = 'William Wibblington'
        self.nurse_name = nurse_name

        shift_coordinator_user_id = 2
        shift_coordinator_name = 'Jeremy Giblet'
        self.shift_coordinator_name = shift_coordinator_name

        def mock_activity_read(*args, **kwargs):
            activity = {
                'create_uid': (nurse_user_id, nurse_name),
                'terminate_uid': (shift_coordinator_user_id,
                                  shift_coordinator_name),
                'date_started': '1952-10-12 15:10:44',
                'date_terminated': '1952-10-13 07:55:02',
                'cancel_reason_id': False,
                'data_ref': 'nh.clinical.pme.foo,1',
                'data_model': 'nh.clinical.patient_monitoring_exception',
            }

            test = self.env.context.get('test')
            if test == 'transfer':
                transfer_cancel_reason = self.browse_ref(
                    'nh_eobs.cancel_reason_transfer')
                activity['cancel_reason_id'] = (transfer_cancel_reason.id,
                                                'nh.cancel.reason')

            return [activity]
        self.activity_model = self.env['nh.activity']
        self.activity_model._patch_method('read', mock_activity_read)

        def mock_pme_read(*args, **kwargs):
            return {
                'reason': 'Because it seemed like a good idea at the time.'
            }
        self.pme_model = self.env['nh.clinical.patient_monitoring_exception']
        self.pme_model._patch_method('read', mock_pme_read)

        def mock_user_read(*args, **kwargs):
            user_id = None
            if hasattr(args[0], '_ids'):
                user_id = args[0].id
            elif len(args) >= 4:
                user_id = args[3]

            if user_id == nurse_user_id:
                nurse_group = self.browse_ref('nh_clinical.group_nhc_nurse')
                return [{'id': nurse_user_id,
                         'name': nurse_name,
                         'groups_id': [nurse_group.id]}]
            elif user_id == shift_coordinator_user_id:
                ward_manager_group = self.browse_ref(
                    'nh_clinical.group_nhc_ward_manager')
                return [{'id': shift_coordinator_user_id,
                        'name': shift_coordinator_name,
                         'groups_id': [ward_manager_group.id]}]
            else:
                return mock_user_read.origin(*args, **kwargs)
        self.user_model = self.env['res.users']
        self.user_model._patch_method('read', mock_user_read)

        def mock_cancel_reason_read(*args, **kwargs):
            return {'name': 'Transfer'}

        self.cancel_reason_model = self.env['nh.cancel.reason']
        self.cancel_reason_model._patch_method('read', mock_cancel_reason_read)

        self.report_model = self.env['report.nh.clinical.observation_report']
        # Stubbed out method to return nothing as was calling user read and
        # expecting all user values which is time consuming and not the code
        # under test anyway.
        self.report_model._patch_method(
            'convert_activity_dates_to_context_dates', lambda a, b: None)

    def call_test(self):
        self.pme_started_dictionary = \
            self.report_model.get_report_entry_dictionary(
                1, pme_started=True)
        self.pme_completed_dictionary = \
            self.report_model.get_report_entry_dictionary(
                1, pme_started=False)

    def test_started_user_is_nurse(self):
        self.call_test()
        expected = self.nurse_name
        actual = self.pme_started_dictionary.get('user')
        self.assertEqual(expected, actual)

    def test_completed_user_is_shift_coordinator(self):
        self.call_test()
        expected = self.shift_coordinator_name
        actual = self.pme_completed_dictionary.get('user')
        self.assertEqual(expected, actual)

    def test_transfer_reason_for_restart_obs(self):
        self.env.context = {'test': 'transfer'}
        self.call_test()
        expected = 'Transfer'
        actual = self.pme_completed_dictionary.get('reason')
        self.assertEqual(expected, actual)

    def tearDown(self):
        self.activity_model._revert_method('read')
        self.pme_model._revert_method('read')
        self.user_model._revert_method('read')
        self.report_model._revert_method(
            'convert_activity_dates_to_context_dates')
        self.cancel_reason_model._revert_method('read')
        super(GetReportEntryDictionary, self).tearDown()
