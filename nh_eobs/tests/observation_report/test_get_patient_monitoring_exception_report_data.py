# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase

from openerp.addons.nh_eobs.report import helpers


class TestGetPatientMonitoringExceptionReportData(TransactionCase):

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

        self.reason_1 = \
            self.pme_reason_model.create({'display_text': 'reason_one'})
        self.reason_2 = \
            self.pme_reason_model.create({'display_text': 'reason_two'})
        self.reason_3 = \
            self.pme_reason_model.create({'display_text': 'reason_three'})

        pme_closed = self.pme_model.create_activity(
            {
                'parent_id': self.spell_activity_id,
            },
            {'reason': self.reason_1.id, 'spell': self.spell.id}
        )
        # pme_2 = self.pme_model.create({
        #     'reason': self.reason_2, 'spell': self.spell
        # })
        # pme_3 = self.pme_model.create({
        #     'reason': self.reason_3, 'spell': self.spell
        # })
        self.pme_model.start(pme_closed)
        pme_closed = self.activity_model.browse(pme_closed)
        self.start_date = pme_closed.date_started

        input_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': False
        }
        self.input_data_obj = helpers.data_dict_to_obj(input_data)

        self.dictionary = \
            self.observation_report_model.\
                get_patient_monitoring_exception_report_data(
                    cr, uid, self.spell_activity.id, self.start_date
                )

        self.root_key = 'patient_monitoring_exceptions'
        self.date_key = 'date'
        self.user_key = 'user'
        self.reason_key = 'reason'
        self.status_key = 'status'
        self.keys_list = [self.date_key, self.user_key,
                          self.reason_key, self.status_key]

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
        report_entries = self.dictionary[self.root_key]
        report_entry = [report_entry for report_entry in report_entries
                        if report_entry[self.date_key] == self.start_date]
        self.assertEqual(
            len(report_entry), 1,
            "Should be one report entry with start date '{}'."
                .format(self.start_date)
        )
        if len(report_entry) != 1:
            raise AssertionError()

    def test_end_of_patient_monitoring_exception_returned(self):
        pass