# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_eobs.report import helpers
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetPatientMonitoringExceptionReportData(TransactionCase):

    def setUp(self):
        super(TestGetPatientMonitoringExceptionReportData, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.rapid_tranq_1_reason = \
            self.browse_ref('nh_eobs.acute_hospital_ed')
        self.rapid_tranq_2_reason = self.browse_ref('nh_eobs.awol')

        self.rapid_tranq_1_activity = \
            self.test_utils.create_activity_rapid_tranq()
        self.rapid_tranq_2_activity = \
            self.test_utils.create_activity_rapid_tranq(
                reason_id=self.rapid_tranq_2_reason.id)

        self.rapid_tranq_1_activity.data_ref.start(
            self.rapid_tranq_1_activity.id)
        self.rapid_tranq_1_activity.data_ref.complete(
            self.rapid_tranq_1_activity.id)
        self.rapid_tranq_2_activity.data_ref.start(
            self.rapid_tranq_2_activity.id)
        self.rapid_tranq_2_activity.data_ref.cancel(
            self.rapid_tranq_2_activity.id)

        one_day_ago = datetime.now() - timedelta(days=1)
        self.rapid_tranq_1_activity.date_started = one_day_ago

        self.report_pme_data = self.report_model\
            .get_patient_monitoring_exception_report_data(
                self.spell_activity.id)

    def test_contains_rapid_tranq_events(self):
        datetime_utils = self.env['datetime_utils']
        datetime_format = \
            datetime_utils.datetime_format_front_end_two_character_year

        rapid_tranq_1_date_started = datetime.strptime(
            self.rapid_tranq_1_activity.date_started, DTF)
        rapid_tranq_1_date_started = helpers.convert_db_date_to_context_date(
            self.env.cr, self.env.uid,
            rapid_tranq_1_date_started, datetime_format)

        rapid_tranq_1_date_terminated = datetime.strptime(
            self.rapid_tranq_1_activity.date_terminated, DTF)
        rapid_tranq_1_date_terminated = helpers\
            .convert_db_date_to_context_date(
                self.env.cr, self.env.uid, rapid_tranq_1_date_terminated,
                datetime_format)

        rapid_tranq_2_date_started = datetime.strptime(
            self.rapid_tranq_2_activity.date_started, DTF)
        rapid_tranq_2_date_started = helpers.convert_db_date_to_context_date(
            self.env.cr, self.env.uid, rapid_tranq_2_date_started,
            datetime_format)

        rapid_tranq_2_date_terminated = datetime.strptime(
            self.rapid_tranq_2_activity.date_terminated, DTF)
        rapid_tranq_2_date_terminated = helpers\
            .convert_db_date_to_context_date(
                self.env.cr, self.env.uid, rapid_tranq_2_date_terminated,
                datetime_format
            )

        expected_report_entries = [
            {
                'date': rapid_tranq_1_date_started,
                'user': 'Administrator',
                'status': 'Start Rapid Tranq.',
                'reason': None
            },
            {
                'date': rapid_tranq_1_date_terminated,
                'user': 'Administrator',
                'status': 'Stop Rapid Tranq.',
                'reason': None
            },
            {
                'date': rapid_tranq_2_date_started,
                'user': 'Administrator',
                'status': 'Start Rapid Tranq.',
                'reason': self.rapid_tranq_2_reason.display_text
            },
            {
                'date': rapid_tranq_2_date_terminated,
                'user': 'Administrator',
                'status': 'Stop Rapid Tranq.',
                'reason': None
            }
        ]
        expected = {
            'patient_monitoring_exception_history': expected_report_entries
        }
        actual = self.report_pme_data

        self.assertEqual(expected, actual)
