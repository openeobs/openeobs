# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase

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
        pme_not_started_id = self.pme_model.create_activity(
            {'parent_id': self.spell_activity_id},
            {'reason': self.reason_2.id, 'spell': self.spell.id}
        )

        # Progress activity lifecycle of the patient monitoring exceptions.
        self.pme_model.start(pme_closed_id)
        self.pme_model.complete(pme_closed_id)
        self.pme_model.start(pme_open_id)

        # Get records for the patient monitoring exceptions.
        self.pme_closed = self.activity_model.browse(pme_closed_id)
        self.pme_open = self.activity_model.browse(pme_open_id)
        self.pme_not_started = self.activity_model.browse(pme_not_started_id)

        self.dictionary = \
            self.observation_report_model.\
                get_patient_monitoring_exception_report_data(
                    cr, uid, self.spell_activity.id,
                    self.pme_closed.date_started
                )

        self.report_entries = self.dictionary[self.root_key]

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
        report_entry = [report_entry for report_entry in self.report_entries
                        if report_entry[self.date_key] ==
                            self.pme_closed.date_started
                        and report_entry[self.status_key] == self.stop_obs_msg]

        self.assertEqual(
            len(report_entry), 2,
            "Two patient monitoring exceptions are started '{}'."
                .format(self.pme_closed.date_started)
        )

    def test_end_of_patient_monitoring_exception_returned(self):
        report_entry = [report_entry for report_entry in self.report_entries
                        if report_entry[self.date_key] ==
                            self.pme_closed.date_terminated
                        and report_entry[self.status_key] ==
                            self.restart_obs_msg]

        self.assertEqual(
            len(report_entry), 1,
            "One patient monitoring exception is completed '{}'."
                .format(self.pme_closed.date_terminated)
        )

    def test_correct_number_of_started_pme_record_entries(self):
        pme_started_report_entries = [report_entry for report_entry
                                      in self.report_entries
                                      if report_entry[self.status_key] ==
                                        self.stop_obs_msg]
        self.assertEqual(len(pme_started_report_entries), 2,
                         "Two patient monitoring exceptions are started "
                         "for the spell.")


    def test_correct_number_of_completed_pme_record_entries(self):
        pme_started_report_entries = [report_entry for report_entry
                                      in self.report_entries
                                      if report_entry[self.status_key] ==
                                      self.restart_obs_msg]
        self.assertEqual(len(pme_started_report_entries), 1,
                         "One patient monitoring exception is completed "
                         "for the spell.")
