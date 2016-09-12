# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tests.common import TransactionCase


class TestNHClinicalWardBoardRestartsEWSTasks(TransactionCase):
    """
    Test that a new EWS task is generated when the observations are restarted
    """

    # @classmethod
    # def setUpClass(cls):
    #     super(TestNHClinicalWardBoardRestartsEWSTasks, cls).setUpClass()
    #     cls.wardboard_model = cls.registry('nh.clinical.wardboard')
    #     cls.activity_model = cls.registry('nh.activity')
    #     cls.spell_model = cls.registry('nh.clinical.spell')
    #     cls.ews_model = cls.registry('nh.clinical.patient.observation.ews')
    #     cls.api_model = cls.registry('nh.clinical.api')
    #
    #     def patch_wardboard_read(*args, **kwargs):
    #         return {
    #             'spell_activity_id': (1, 'Spell/Visit'),
    #             'patient_id': (1, 'Test Patient')
    #         }
    #
    #     def patch_toggle_obs_stop_flag(*args, **kwargs):
    #         return False
    #
    #     def patch_spell_search(*args, **kwargs):
    #         return [1]
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
    #     def patch_api_freq_change(*args, **kwargs):
    #         return True
    #
    #     cls.wardboard_model._patch_method(
    #         'set_obs_stop_flag', patch_toggle_obs_stop_flag)
    #     cls.wardboard_model._patch_method('read', patch_wardboard_read)
    #     cls.spell_model._patch_method('search', patch_spell_search)
    #     cls.ews_model._patch_method(
    #         'create_activity', patch_activity_create)
    #     cls.activity_model._patch_method('schedule', patch_activity_schedule)
    #     cls.api_model._patch_method('change_activity_frequency',
    #                                 patch_api_freq_change)

    def setUp(self):
        super(TestNHClinicalWardBoardRestartsEWSTasks, self).setUp()
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.wizard_model = \
            self.env['nh.clinical.patient_monitoring_exception.select_reason']

        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
        })

        self.spell_activity_id = self.spell_model.create_activity(
            {'state': 'started'},  # Fails a search later without this.
            {'patient_id': self.patient.id, 'pos_id': 1}
        )

        self.wardboard = self.wardboard_model.new(
            {'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient}
        )

    # @classmethod
    # def tearDownClass(cls):
    #     super(TestNHClinicalWardBoardRestartsEWSTasks, cls).tearDownClass()
    #     cls.wardboard_model._revert_method('set_obs_stop_flag')
    #     cls.wardboard_model._revert_method('read')
    #     cls.spell_model._revert_method('search')
    #     cls.ews_model._revert_method('create_activity')
    #     cls.activity_model._revert_method('schedule')
    #     cls.api_model._revert_method('change_activity_frequency')

    def test_ews_task_created(self):
        """
        Test that when obs_stop flag is set to False then a new EWS observation
        is scheduled for 1 hours time.
        :return:
        """
        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.wardboard.spell_activity_id.id)
        ]
        ews_activities_before = len(self.activity_model.search(domain))
        self.wardboard.create_new_ews()
        ews_activities_after = len(self.activity_model.search(domain))
        self.assertTrue(ews_activities_before + 1, ews_activities_after)

    def test_ews_due_in_one_hour(self):
        """
        Test that the newly created ews task is due one hour from creation.
        Actually tests the time in string format which only displays hours and
        minutes. This effectively rounds to the nearest minute for comparison.
        :return:
        """
        time_before_ews_creation = datetime.now()
        expected_time_due = time_before_ews_creation + timedelta(hours=1)
        expected_time_due_str = expected_time_due.strftime(DTF)
        new_ews_id = self.wardboard.create_new_ews()
        actual_time_due_str = self.activity_model.browse(new_ews_id).date_scheduled
        self.assertEquals(expected_time_due_str, actual_time_due_str)

