# -*- coding: utf-8 -*-
"""
Throughout this module I have used 'pme' as an abbreviation for
'patient monitoring exception' because its usage will often take lines over the
PEP-8 character limit.
"""
from datetime import datetime, timedelta

from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

from openerp.addons.nh_eobs.report import helpers


class TestGetPatientMonitoringExceptionReportData(TransactionCase):

    @classmethod
    def setUpClass(cls):
        cls.stop_obs_msg = 'Stop Observations'
        cls.restart_obs_msg = 'Restart Observations'

        cls.root_key = 'patient_monitoring_exceptions'
        cls.date_key = 'date'
        cls.user_key = 'user'
        cls.reason_key = 'reason'
        cls.status_key = 'status'

        cls.keys_list = [cls.date_key, cls.user_key,
                         cls.reason_key, cls.status_key]

    def setUp(self):
        super(TestGetPatientMonitoringExceptionReportData, self).setUp()
        cr, uid = self.cr, self.uid
        self.observation_report_model = \
            self.registry('report.nh.clinical.observation_report')
        self.patient_model = self.env['nh.clinical.patient']
        self.spell_model = self.env['nh.clinical.spell']
        self.activity_model = self.env['nh.activity']
        self.pme_reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.pme_model = self.env['nh.clinical.patient_monitoring_exception']
        self.pme_reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']

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

        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient
        })

        # Create some patient monitoring exception reasons.
        self.reason_1 = \
            self.pme_reason_model.create({'display_text': 'reason_one'})
        self.reason_2 = \
            self.pme_reason_model.create({'display_text': 'reason_two'})
        self.reason_3 = \
            self.pme_reason_model.create({'display_text': 'reason_three'})

        # Create some patient monitoring exceptions.
        pme_closed_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.reason_1.id, 'spell': self.spell.id}
        )
        pme_open_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.reason_2.id, 'spell': self.spell.id}
        )
        pme_started_long_ago_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.reason_1.id, 'spell': self.spell.id}
        )
        pme_ends_in_the_future_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.reason_2.id, 'spell': self.spell.id}
        )
        pme_still_open_before_start_date_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.reason_3.id, 'spell': self.spell.id}
        )

        # Progress activity lifecycle of the patient monitoring exceptions.
        self.pme_model.start(pme_closed_id)
        self.pme_model.complete(pme_closed_id)
        self.pme_model.start(pme_open_id)
        self.pme_model.start(pme_started_long_ago_id)
        self.pme_model.complete(pme_started_long_ago_id)
        self.pme_model.start(pme_ends_in_the_future_id)
        self.pme_model.complete(pme_ends_in_the_future_id)
        self.pme_model.start(pme_still_open_before_start_date_id)

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

        self.start_date = self.pme_closed.date_started
        self.end_date = self.pme_closed.date_terminated

        # Modify start date and end dates.
        ages_ago = '1900-01-01 15:00:00'
        self.pme_started_long_ago.date_started = ages_ago
        self.pme_ends_in_the_future.date_terminated = \
            self.add_one_day_to_datetime_string(self.end_date)
        self.pme_still_open_before_start_date.date_started = ages_ago

        self.dictionary = \
            self.observation_report_model.\
                get_patient_monitoring_exception_report_data(
                    cr, uid, self.spell_activity.id,
                    self.start_date, self.end_date
                )

        self.report_entries = self.dictionary[self.root_key]

    @classmethod
    def add_one_day_to_datetime_string(cls, start_date):
        datetime_obj = datetime.strptime(start_date, dtf)
        delta = timedelta(days=1)
        datetime_obj += delta
        return datetime_obj.strftime(dtf)

    def get_pme_ended_report_entries(self):
        pme_ended_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.status_key] == self.restart_obs_msg]
        return pme_ended_report_entries

    def test_returns_dictionary(self):
        self.assertTrue(dict(self.dictionary))

    def test_dictionary_has_correct_root_key(self):
        self.dictionary[self.root_key]

    def test_root_key_value_is_a_list(self):
        self.assertTrue(list(self.dictionary[self.root_key]))

    def test_list_items_have_correct_child_keys(self):
        items = self.dictionary[self.root_key]
        for item in items:
            for key in item.keys():
                if key not in self.keys_list:
                    raise AssertionError("An unexpected key '{}' was found in "
                                         "the dictionary.".format(key))

    def test_start_of_patient_monitoring_exception_returned(self):
        report_entry = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.date_key] == self.start_date
             and report_entry[self.status_key] == self.stop_obs_msg]

        self.assertEqual(
            len(report_entry), 3,
            "Two patient monitoring exceptions are started '{}'."
                .format(self.pme_closed.date_started)
        )

    def test_end_of_patient_monitoring_exception_returned(self):
        report_entry = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.date_key] == self.end_date
             and report_entry[self.status_key] == self.restart_obs_msg]

        self.assertEqual(
            len(report_entry), 1,
            "One patient monitoring exception has ended '{}'."
                .format(self.pme_closed.date_terminated)
        )

    def test_correct_number_of_started_pme_record_entries(self):
        pme_started_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.status_key] == self.stop_obs_msg]

        self.assertEqual(len(pme_started_report_entries), 4,
                         "Two patient monitoring exceptions are started "
                         "for the spell.")


    def test_correct_number_of_ended_pme_record_entries(self):
        pme_ended_report_entries = self.get_pme_ended_report_entries()

        self.assertEqual(len(pme_ended_report_entries), 2,
                         "One patient monitoring exception has ended "
                         "for the spell.")

    def test_still_open_pme_is_returned_even_if_outside_date_range(self):
        pme_still_open_before_start_date_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.date_key] ==
             self.pme_still_open_before_start_date.date_started
             and report_entry[self.reason_key] == self.reason_3.display_name]

        self.assertEqual(len(pme_still_open_before_start_date_report_entries),
                         1,
                         "One patient monitoring exception is still open with"
                         "a 'date started' field before the specified start "
                         "date.")

    def test_ended_pme_started_before_start_date_is_excluded(self):
        pme_started_long_ago_report_entries = \
            [report_entry for report_entry in self.report_entries
             if report_entry[self.date_key] ==
             self.pme_started_long_ago.date_started
             and report_entry[self.reason_key] == self.reason_1.display_name]

        self.assertEqual(len(pme_started_long_ago_report_entries), 0,
                         "There should not be any report entries for the "
                         "patient monitoring exception that was started long "
                         "ago.")

    def test_reason_is_none_on_pme_ended_report_entry(self):
        pme_ended_report_entries = self.get_pme_ended_report_entries()
        for report_entry in pme_ended_report_entries:
            if report_entry[self.reason_key] is not None:
                raise AssertionError("All reasons on report entries for "
                                     "restarting of obs should be `None`.")
