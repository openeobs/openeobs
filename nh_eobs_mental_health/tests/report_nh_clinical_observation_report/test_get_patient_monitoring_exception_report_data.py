# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_eobs.report import helpers
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetPatientMonitoringExceptionReportData(TransactionCase):

    def setUp(self):
        super(TestGetPatientMonitoringExceptionReportData, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)

        self.activity_model = self.env['nh.activity']

        # Create some PME activities.
        self.obs_stop_1_activity = self.test_utils.create_activity_obs_stop()
        self.obs_stop_1_activity.data_ref.start(self.obs_stop_1_activity.id)
        self.obs_stop_1_activity.data_ref.complete(self.obs_stop_1_activity.id)

        self.rapid_tranq_1_activity = self.test_utils\
            .create_activity_rapid_tranq()
        self.rapid_tranq_1_activity.data_ref.start(
            self.rapid_tranq_1_activity.id)
        self.rapid_tranq_1_activity.data_ref.complete(
            self.rapid_tranq_1_activity.id)

        self.rapid_tranq_2_activity = self.test_utils\
            .create_activity_rapid_tranq()
        self.rapid_tranq_2_activity.data_ref.start(
            self.rapid_tranq_2_activity.id)
        self.rapid_tranq_2_activity.data_ref.complete(
            self.rapid_tranq_2_activity.id)

        # Order the PME activities by adjusting time fields.
        self.pme_events = [
            self.add_n_minutes(self.obs_stop_1_activity, 'date_started', 0),
            self.add_n_minutes(self.rapid_tranq_1_activity, 'date_started', 1),
            self.add_n_minutes(self.rapid_tranq_2_activity, 'date_started', 2),
            self.add_n_minutes(
                self.rapid_tranq_2_activity, 'date_terminated', 3),
            self.add_n_minutes(self.obs_stop_1_activity, 'date_terminated', 4),
            self.add_n_minutes(
                self.rapid_tranq_1_activity, 'date_terminated', 5),
        ]

        self.report_model = self.env['report.nh.clinical.observation_report']
        self.report_data = self.report_model\
            .get_patient_monitoring_exception_report_data(
                self.spell_activity.id)
        self.patient_monitoring_exception_history = \
            self.report_data['patient_monitoring_exception_history']

    @staticmethod
    def add_n_minutes(activity, datetime_field, minutes):
        """
        Move one of an activities datetimes into the future by adding minutes
        to it. As well as assigning the new datetime to the activity, it is
        also returned as a string for convenience.

        :param activity:
        :param datetime_field:
        :param minutes:
        :return:
        :rtype: str
        """
        datetime_str = getattr(activity, datetime_field)

        date_time = datetime.strptime(datetime_str, DTF)
        date_time = date_time + timedelta(minutes=minutes)
        new_datetime = date_time.strftime(DTF)

        setattr(activity, datetime_field, new_datetime)
        return new_datetime

    def test_entries_returned_in_chronological_order(self):
        report_datetime_format = self.env['datetime_utils'] \
            .datetime_format_front_end_two_character_year

        def reformat_and_convert_timezone(date_time):
            date_time = datetime.strptime(date_time, DTF)
            return helpers.convert_db_date_to_context_date(
                self.env.cr, self.env.uid, date_time, report_datetime_format)

        expected = map(reformat_and_convert_timezone, self.pme_events)
        actual = map(lambda item: item['date'],
                     self.patient_monitoring_exception_history)

        self.assertEqual(expected, actual)
