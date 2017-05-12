# -*- coding: utf-8 -*-
# TODO These tests should really be in nh_eobs where the
# patient_monitoring_exception abstract model is, but they are here testing
# using obs stop instead because it is difficult to test with an abstract
# model. Need a better solution.
"""
===========
Terminology
===========
Throughout this module I have used 'pme' as an abbreviation for
'patient monitoring exception' because its usage will often take lines over the
PEP-8 character limit.
"""
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class TestGetPatientMonitoringExceptionReportData(TransactionCase):
    """
    Encapsulates common setup and constants used by classes that test the
    :method:<get_patient_monitoring_exceptions_report_data> method.
    """
    STOP_OBS_MSG = 'Stop Observations'
    RESTART_OBS_MSG = 'Restart Observations'
    TRANSFER = 'Transfer'

    ROOT_KEY = 'patient_monitoring_exception_history'
    DATE_KEY = 'date'
    USER_KEY = 'user'
    REASON_KEY = 'reason'
    STATUS_KEY = 'status'

    KEYS_LIST = [DATE_KEY, USER_KEY, REASON_KEY, STATUS_KEY]

    @classmethod
    def add_one_day_to_datetime_string(cls, start_date):
        """
        Helper method to add 1 day to datetime string
        :param start_date: String representing Odoo datetime
        :return: String representing Odoo datetime but 1 day later
        :rtype: str
        """
        delta = timedelta(days=1)
        return cls.add_time_delta_to_datetime_string(start_date, delta)

    @classmethod
    def add_time_delta_to_datetime_string(cls, date_string, time_delta):
        """
        Add a timedelta to the supplied datetime string
        :param date_string: String representing Odoo datetime
        :param time_delta: timedelta object to apply
        :return: Odoo datetime string for applied timedelta
        ;:rtype: str
        """
        date_time = datetime.strptime(date_string, dtf)
        date_time += time_delta
        return date_time.strftime(dtf)

    @classmethod
    def now_string(cls):
        """
        Get string for 'now'
        :return: Odoo datetime string for now()
        :rtype: str
        """
        now = datetime.now()
        now.replace(second=0, microsecond=0)
        return now.strftime(dtf)

    def create_spell(self):
        """
        Create the spell for the test and add properties for the spell to self
        """
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.patient = self.patient_model.create({
            'given_name': 'Jon',
            'family_name': 'Snow',
            'patient_identifier': 'a_patient_identifier'
        })
        self.spell_activity_id = self.spell_model.create_activity(
            {},
            {'patient_id': self.patient.id, 'pos_id': 1}
        )
        self.activity_model.start(self.spell_activity_id)
        self.spell_activity = \
            self.activity_model.browse(self.spell_activity_id)
        self.spell = self.spell_activity.data_ref

    def setUp(self):
        super(TestGetPatientMonitoringExceptionReportData, self).setUp()
        self.create_spell()

        self.pme_reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.pme_model = self.env['nh.clinical.pme.obs_stop']
        self.observation_report_model = \
            self.env['report.nh.clinical.observation_report']


class TestMonitoringExceptionsReturned(
        TestGetPatientMonitoringExceptionReportData):

    def setUp(self):
        super(TestMonitoringExceptionsReturned, self).setUp()
        self.ages_ago = '1989-06-06 14:00:00'
        self.start_date = self.now_string()

    def call_test(self, expected_num_stop_obs_entries,
                  expected_num_restart_obs_entries,
                  expected_reason_display_text='',
                  report_start_datetime=None, report_end_datetime=None):
        """
        Gets report data and asserts the expected number of 'Stop Obs' entries,
        expected number of 'Restart Obs' entries. Optionally also asserts
        the reason if the appropriate keyword argument is passed.
        :param expected_num_stop_obs_entries:
        :type expected_num_stop_obs_entries: int
        :param expected_num_restart_obs_entries:
        :type expected_num_restart_obs_entries: int
        :param expected_reason_display_text:
        :type expected_reason_display_text: str
        :param report_start_datetime: If not passed defaults to
        `datetime.datetime.now()`.
        :type report_start_datetime: str
        :param report_end_datetime: If not passed defaults to
        `datetime.datetime.now()`.
        :type report_end_datetime: str
        :return:
        """
        if not report_start_datetime:
            report_start_datetime = self.start_date  # Initialised in setUp().
        if not report_end_datetime:
            report_end_datetime = self.now_string()

        self.dictionary = self.observation_report_model \
            .get_patient_monitoring_exception_report_data(
                self.spell_activity.id, report_start_datetime,
                report_end_datetime)

        self.report_entries = self.dictionary[self.ROOT_KEY]

        expected_num_report_entries = expected_num_stop_obs_entries + \
            expected_num_restart_obs_entries
        self.assertEqual(len(self.report_entries), expected_num_report_entries)

        stop_obs_report_entries = self.get_stop_obs_report_entries()
        self.assertEqual(len(stop_obs_report_entries),
                         expected_num_stop_obs_entries)

        for entry in stop_obs_report_entries:
            self.assertEqual(entry[self.REASON_KEY],
                             expected_reason_display_text)

        restart_obs_report_entries = self.get_restart_obs_report_entries()
        self.assertEqual(len(restart_obs_report_entries),
                         expected_num_restart_obs_entries)

    def setup_pme(self, reason_display_text='', state='started',
                  date_started=None, date_terminated=None):
        """
        Create a PME, progress it's activity lifecycle, and modify start and
        terminated dates.
        :param reason_display_text:
        :type reason_display_text: str
        :param state:
        :type state: str
        :param date_started:
        :type date_started: str
        :param date_terminated:
        :type date_terminated: str
        :return:
        """
        if date_started is None:
            date_started = self.now_string()

        self.pme_reason = self.pme_reason_model.create(
            {'display_text': reason_display_text}
        )
        self.pme_activity_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.pme_reason.id, 'spell': self.spell.id}
        )
        self.pme = self.activity_model.browse(self.pme_activity_id).data_ref
        if state in ['started', 'completed', 'cancelled']:
            self.pme.start(self.pme_activity_id)
        if state == 'completed':
            self.pme.complete(self.pme_activity_id)
        if state == 'cancelled':
            self.pme.cancel(self.pme_activity_id)

        self.pme.date_started = date_started
        if state in ['completed', 'cancelled']:
            if date_terminated is None:
                date_terminated = self.now_string()
            self.pme.date_terminated = date_terminated

    def get_stop_obs_report_entries(self):
        """
        Get the report entries for restart obs PME messages
        :return: List of restart obs PME entries
        """
        pme_started_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.STATUS_KEY] == self.STOP_OBS_MSG]
        return pme_started_report_entries

    def get_restart_obs_report_entries(self):
        """
        Get the report entries for restart obs PME messages
        :return: List of restart obs PME entries
        """
        pme_ended_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.STATUS_KEY] == self.RESTART_OBS_MSG]
        return pme_ended_report_entries

    def test_returns_dictionary(self):
        """
        Test that the report dictionary is of type dict
        """
        self.call_test(0, 0)
        self.assertTrue(dict(self.dictionary))

    def test_dictionary_has_correct_root_key(self):
        """
        Test that the report dictionary has the correct root key
        """
        self.setup_pme(state='completed')
        self.call_test(1, 1)

        self.assertTrue(self.ROOT_KEY in self.dictionary)

    def test_root_key_value_is_a_list(self):
        """
        Test that the report dictionary's patient monitoring exception entry
        is a list of PMEs
        """
        self.setup_pme(state='completed')
        self.call_test(1, 1)

        self.assertTrue(isinstance(self.dictionary[self.ROOT_KEY], list))

    def test_list_items_have_correct_child_keys(self):
        """
        Test that the report's patient monitoring exception entries have the
        correct format
        """
        self.call_test(0, 0)
        items = self.dictionary[self.ROOT_KEY]
        for item in items:
            for key in item.keys():
                if key not in self.KEYS_LIST:
                    raise AssertionError("An unexpected key '{}' was found in "
                                         "the dictionary.".format(key))

    def test_closed_pme(self):
        """
        Test a PME that has been closed.
        """
        reason_display_text = 'pme_closed_reason'
        self.setup_pme(reason_display_text, state='completed')
        self.call_test(1, 1, reason_display_text)

    def test_open_pme(self):
        """
        Test a PME that is still open.
        """
        reason_display_text = 'pme_open_reason'
        self.setup_pme(reason_display_text)
        self.call_test(1, 0, reason_display_text)

    def test_pme_started_long_ago(self):
        """
        Test PME started before report start date.
        """
        reason_display_text = 'pme_started_long_ago_reason'
        self.setup_pme(reason_display_text, state='completed',
                       date_started=self.ages_ago)
        self.call_test(1, 1, reason_display_text)

    def test_pme_ends_after_report_end_date(self):
        """
        Test PME that ends after the report end date.
        """
        reason_display_text = 'pme_ends_in_the_future_reason'
        date_terminated = self.add_one_day_to_datetime_string(
            self.now_string())
        self.setup_pme(reason_display_text, state='completed',
                       date_terminated=date_terminated)
        self.call_test(1, 1, reason_display_text)

    def test_open_pme_started_before_report_start_date(self):
        """
        Test open PME started before the report start date.
        """
        reason_display_text = 'open_pme_started_before_report_start_still'
        self.setup_pme(reason_display_text, date_started=self.ages_ago)
        self.call_test(1, 0, reason_display_text)

    def test_report_range_inside_pme_range(self):
        """
        Tests EOBS-1117 which occurred when report date ranges were inside PME
        date ranges and wouldn't return the PME
        """
        reason_display_text = 'pme_active_during_report_range'

        date_started = self.add_time_delta_to_datetime_string(
            self.ages_ago, timedelta(hours=-1))
        date_terminated = self.add_time_delta_to_datetime_string(
            self.ages_ago, timedelta(hours=1))
        self.setup_pme(reason_display_text, state='completed',
                       date_started=date_started,
                       date_terminated=date_terminated)

        report_start_datetime = self.add_time_delta_to_datetime_string(
            self.ages_ago, timedelta(hours=-2))
        report_end_datetime = self.add_time_delta_to_datetime_string(
            self.ages_ago, timedelta(hours=2))
        self.call_test(1, 1, reason_display_text,
                       report_start_datetime=report_start_datetime,
                       report_end_datetime=report_end_datetime)

    def test_cancelled_pme(self):
        """
        Test cancelled PME included on the report.
        """
        reason_display_text = 'pme_cancelled'
        self.setup_pme(reason_display_text, state='cancelled')
        self.call_test(1, 1, reason_display_text)

    def test_pme_ended_before_start_date(self):
        """
        Test PME that ended before the start date is not included.
        """
        reason_display_text = 'def test_pme_ended_before_start_date'

        date_started = self.ages_ago
        date_terminated = self.add_time_delta_to_datetime_string(
            self.ages_ago, timedelta(hours=1))
        self.setup_pme(reason_display_text, state='completed',
                       date_started=date_started,
                       date_terminated=date_terminated)

        self.call_test(0, 0, reason_display_text)

    def test_reason_is_none_on_pme_ended_report_entry(self):
        """
        Test that the ended PME's reason is None
        """
        self.setup_pme(state='completed')
        self.call_test(1, 1)
        restart_obs_report_entries = self.get_restart_obs_report_entries()
        self.assertIsNone(restart_obs_report_entries[0]['reason'])

    def test_reason_set_on_transfer_report_entry(self):
        """
        Test that the PME ended via transfer has a reason of 'transfer'.
        """
        self.setup_pme(state='cancelled')

        # Setup cancellation of patient monitoring exception due to transfer.
        cancel_reason_transfer = \
            self.browse_ref('nh_clinical.cancel_reason_transfer')
        pme_activity = self.env['nh.activity'].browse(self.pme_activity_id)
        pme_activity.cancel_reason_id = \
            cancel_reason_transfer.id

        self.call_test(1, 1)

        expected_reason = self.TRANSFER
        actual_reason = self.get_restart_obs_report_entries()[0]['reason']
        self.assertEqual(expected_reason, actual_reason)

    def test_user_set_on_transfer_report_entry(self):
        """
        Test that the user responsible for the transfer is included in the
        PME that ended due to transfer
        """
        self.setup_pme(state='cancelled')

        # Setup cancellation of patient monitoring exception due to transfer.
        cancel_reason_transfer = \
            self.browse_ref('nh_clinical.cancel_reason_transfer')
        pme_activity = self.env['nh.activity'].browse(self.pme_activity_id)
        pme_activity.cancel_reason_id = \
            cancel_reason_transfer.id

        self.call_test(1, 1)

        expected_user = self.TRANSFER
        actual_user = self.get_restart_obs_report_entries()[0]['reason']
        self.assertEqual(expected_user, actual_user)

    def test_currently_active_pme_always_included(self):
        """
        Test a currently active PME started after the report range is included.
        """
        reason_display_text = 'current_active_pme'
        self.setup_pme(reason_display_text)
        date_started = self.ages_ago
        date_terminated = self.add_one_day_to_datetime_string(self.ages_ago)
        self.call_test(1, 0, reason_display_text,
                       date_started, date_terminated)
