# -*- coding: utf-8 -*-
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
        date_time = datetime.strptime(start_date, dtf)
        delta = timedelta(days=1)
        date_time += delta
        return date_time.strftime(dtf)

    @classmethod
    def now_string(cls):
        now = datetime.now()
        return now.strftime(dtf)

    def create_spell(self):
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
        self.spell_activity = \
            self.activity_model.browse(self.spell_activity_id)
        self.spell = self.spell_activity.data_ref

    def setUp(self):
        super(TestGetPatientMonitoringExceptionReportData, self).setUp()
        self.create_spell()


class TestMonitoringExceptionsReturned(
        TestGetPatientMonitoringExceptionReportData):

    def setUp(self):
        super(TestMonitoringExceptionsReturned, self).setUp()

        self.pme_reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.pme_model = self.env['nh.clinical.patient_monitoring_exception']
        self.observation_report_model = \
            self.env['report.nh.clinical.observation_report']

        # Create some patient monitoring exception reasons.
        self.pme_closed_reason = \
            self.pme_reason_model.create({'display_text': 'pme_closed_reason'})
        self.pme_open_reason = \
            self.pme_reason_model.create({'display_text': 'pme_open_reason'})
        self.pme_started_long_ago_reason = self.pme_reason_model.create(
            {'display_text': 'pme_started_long_ago_reason'}
        )
        self.pme_ends_in_the_future_reason = self.pme_reason_model.create(
            {'display_text': 'pme_ends_in_the_future_reason'}
        )
        self.pme_still_open_before_start_date_reason = \
            self.pme_reason_model.create(
                {'display_text': 'pme_still_open_before_start_date_reason'}
            )
        self.pme_cancelled_due_to_transfer_reason = \
            self.pme_reason_model.create(
                {'display_text': 'pme_cancelled_due_to_transfer_reason'}
            )
        self.pme_ended_before_start_date_reason = \
            self.pme_reason_model.create(
                {'display_text': 'pme_ended_before_start_date_reason'}
            )

        # Create some patient monitoring exceptions.
        pme_closed_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.pme_closed_reason.id, 'spell': self.spell.id}
        )
        pme_open_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.pme_open_reason.id, 'spell': self.spell.id}
        )
        pme_started_long_ago_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.pme_started_long_ago_reason.id,
             'spell': self.spell.id}
        )
        pme_ends_in_the_future_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.pme_ends_in_the_future_reason.id,
             'spell': self.spell.id}
        )
        pme_still_open_before_start_date_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.pme_still_open_before_start_date_reason.id,
             'spell': self.spell.id}
        )
        pme_cancelled_due_to_transfer_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.pme_cancelled_due_to_transfer_reason.id,
             'spell': self.spell.id}
        )
        pme_ended_before_start_date_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.pme_ended_before_start_date_reason.id,
             'spell': self.spell.id}
        )

        # Set start datetime to be used for report.
        self.start_date = self.now_string()

        # Progress activity lifecycle of the patient monitoring exceptions.
        self.pme_model.start(pme_closed_id)
        self.pme_model.complete(pme_closed_id)
        self.pme_model.start(pme_open_id)
        self.pme_model.start(pme_started_long_ago_id)
        self.pme_model.complete(pme_started_long_ago_id)
        self.pme_model.start(pme_ends_in_the_future_id)
        self.pme_model.complete(pme_ends_in_the_future_id)
        self.pme_model.start(pme_still_open_before_start_date_id)
        self.pme_model.start(pme_cancelled_due_to_transfer_id)
        self.pme_model.cancel(pme_cancelled_due_to_transfer_id)
        self.pme_model.start(pme_ended_before_start_date_id)
        self.pme_model.complete(pme_ended_before_start_date_id)

        # Set end datetime to be used for report.
        self.end_date = self.now_string()

        # Get records for the patient monitoring exceptions.
        self.pme_closed = self.activity_model.browse(pme_closed_id)
        self.pme_open = self.activity_model.browse(pme_open_id)
        self.pme_started_long_ago = self.activity_model.browse(
            pme_started_long_ago_id
        )
        self.pme_ends_in_the_future = self.activity_model.browse(
            pme_ends_in_the_future_id
        )
        self.pme_still_open_before_start_date = self.activity_model.browse(
            pme_still_open_before_start_date_id
        )
        self.pme_cancelled_due_to_transfer = self.activity_model.browse(
            pme_cancelled_due_to_transfer_id
        )
        self.pme_ended_before_start_date = self.activity_model.browse(
            pme_ended_before_start_date_id
        )

        # Modify start date and end dates.
        ages_ago = '1989-06-06 14:00:00'
        self.pme_started_long_ago.date_started = ages_ago
        self.pme_ends_in_the_future.date_terminated = \
            self.add_one_day_to_datetime_string(self.end_date)
        self.pme_still_open_before_start_date.date_started = ages_ago
        self.pme_ended_before_start_date.date_started = ages_ago
        self.pme_ended_before_start_date.date_terminated = \
            self.add_one_day_to_datetime_string(ages_ago)

        # Setup cancellation of patient monitoring exception due to transfer.
        cancel_reason_transfer = \
            self.browse_ref('nh_eobs.cancel_reason_transfer')
        self.pme_cancelled_due_to_transfer.cancel_reason_id = \
            cancel_reason_transfer.id

        self.dictionary = self.observation_report_model\
            .get_patient_monitoring_exception_report_data(
                self.spell_activity.id, self.start_date, self.end_date
            )

        self.report_entries = self.dictionary[self.ROOT_KEY]

    def get_restart_obs_report_entries(self):
        pme_ended_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.STATUS_KEY] == self.RESTART_OBS_MSG]
        return pme_ended_report_entries

    def test_returns_dictionary(self):
        self.assertTrue(dict(self.dictionary))

    def test_dictionary_has_correct_root_key(self):
        self.assertTrue(self.dictionary.get(self.ROOT_KEY))

    def test_root_key_value_is_a_list(self):
        self.assertTrue(isinstance(self.dictionary[self.ROOT_KEY], list))

    def test_list_items_have_correct_child_keys(self):
        items = self.dictionary[self.ROOT_KEY]
        for item in items:
            for key in item.keys():
                if key not in self.KEYS_LIST:
                    raise AssertionError("An unexpected key '{}' was found in "
                                         "the dictionary.".format(key))

    def test_correct_number_of_started_pme_record_entries(self):
        pme_started_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.STATUS_KEY] == self.STOP_OBS_MSG]

        self.assertEqual(len(pme_started_report_entries), 6,
                         "Unexpected number of 'started' report entries.")

    def test_correct_number_of_ended_pme_record_entries(self):
        pme_ended_report_entries = self.get_restart_obs_report_entries()

        self.assertEqual(len(pme_ended_report_entries), 3,
                         "Unexpected number of 'ended' report entries.")

    def test_still_open_pme_is_returned_even_if_outside_date_range(self):
        pme_still_open_before_start_date_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.REASON_KEY] ==
             self.pme_still_open_before_start_date_reason.display_name]

        self.assertEqual(len(pme_still_open_before_start_date_report_entries),
                         1,
                         "Unexpected number of report entries added that were "
                         "started before the start date.")

    def test_ended_pme_before_start_date_is_excluded(self):
        pme_started_long_ago_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.REASON_KEY] ==
             self.pme_ended_before_start_date.display_name]

        self.assertEqual(len(pme_started_long_ago_report_entries), 0,
                         "There should not be any report entries for the "
                         "patient monitoring exception that was completed "
                         "before the start date.")

    def test_reason_is_none_on_pme_ended_report_entry(self):
        pme_ended_report_entries = self.get_restart_obs_report_entries()
        pme_ended_no_reason_report_entries = \
            [report_entry for report_entry in pme_ended_report_entries
             if report_entry[self.REASON_KEY] is None]

        self.assertEqual(len(pme_ended_no_reason_report_entries), 2,
                         "All reasons on report entries for restarting of obs "
                         "should be `None`.")

    def test_reason_set_on_transfer_report_entry(self):
        pme_ended_report_entries = self.get_restart_obs_report_entries()
        pme_transfer_report_entries = \
            [report_entry for report_entry in pme_ended_report_entries
             if report_entry[self.REASON_KEY] is self.TRANSFER]

        self.assertEqual(len(pme_transfer_report_entries), 1,
                         "Unexpected amount of patient monitoring excpetions "
                         "with transfer set as reason.")

    def test_user_set_on_transfer_report_entry(self):
        pme_ended_report_entries = self.get_restart_obs_report_entries()
        pme_transfer_report_entries = \
            [report_entry for report_entry in pme_ended_report_entries
             if report_entry[self.USER_KEY] is self.TRANSFER]

        self.assertEqual(len(pme_transfer_report_entries), 1,
                         "Unexpected amount of patient monitoring excpetions "
                         "with transfer set as user.")


class TestDatesInTheFuture(TestGetPatientMonitoringExceptionReportData):

    def setUp(self):
        super(TestDatesInTheFuture, self).setUp()

        self.observation_report_model = \
            self.env['report.nh.clinical.observation_report']

    def test_start_date_in_the_future(self):
        self.start_date = self.add_one_day_to_datetime_string(
            self.now_string()
        )

        self.dictionary = self.observation_report_model \
            .get_patient_monitoring_exception_report_data(
                self.spell_activity.id, self.start_date, None
            )

    def test_end_date_in_the_future(self):
        self.end_date = self.add_one_day_to_datetime_string(self.now_string())

        self.dictionary = self.observation_report_model \
            .get_patient_monitoring_exception_report_data(
                self.spell_activity.id, None, self.end_date
            )

    def test_start_and_end_date_in_the_future(self):
        self.start_date = self.add_one_day_to_datetime_string(
            self.now_string()
        )
        self.end_date = self.add_one_day_to_datetime_string(self.now_string())

        self.dictionary = self.observation_report_model \
            .get_patient_monitoring_exception_report_data(
                self.spell_activity.id, self.start_date, self.end_date
            )
