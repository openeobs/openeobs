# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestLocaliseAndFormatDatetimes(TransactionCase):
    def setUp(self):
        super(TestLocaliseAndFormatDatetimes, self).setUp()

        self.report_data = {
            'report_start': None,
            'report_end': '2017-06-06 13:00:00',
            'spell': {
                'date_terminated': None
            },
            'spell_start': None,
            'patient': {
                'dob': '2017-06-06 00:00:00'
            },
            'ews': [],
            'table_ews': [],
            'patient_monitoring_exception_history': [],
            'transfer_history': []
        }

        context = {'tz': 'Europe/London'}
        report_model = self.env['report.nh.clinical.observation_report']
        report_model.with_context(context)._localise_and_format_datetimes(
            self.report_data)

    def test_date_of_birth_formatted_without_hours_and_minutes(self):
        expected = '06/06/2017'
        actual = self.report_data['patient']['dob']

        self.assertEqual(expected, actual)

    def test_report_end_is_current_local_time(self):
        expected = '14:00 06/06/17'
        actual = self.report_data['report_end']

        self.assertEqual(expected, actual)
