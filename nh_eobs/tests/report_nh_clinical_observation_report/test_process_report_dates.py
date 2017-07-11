# -*- coding: utf-8 -*-
""" Module for TestProcessReportDates class. """
from openerp.tests.common import TransactionCase

from openerp.addons.nh_eobs.report.helpers import BaseReport


class TestProcessReportDates(TransactionCase):
    """
    Test ProcessReportDates method of the
    report.nh.clinical.observation_report model.
    """
    def setUp(self):
        super(TestProcessReportDates, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']
        self.report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']

        self.data = self.report_wizard_model.create({
            'start_time': '2017-03-05 15:00:00',
            'end_time': '2017-05-24 15:00:00'
        })
        self.data_empty = self.report_wizard_model.create({
            'start_time': False,
            'end_time': False
        })
        self.spell_dictionary = {
            'date_started': '2017-01-01 14:00:00',
            'date_terminated': '2017-06-06 14:00:00'
        }
        self.spell_dictionary_no_date_terminated = {
            'date_started': '2017-01-01 14:00:00',
            'date_terminated': False
        }
        # Only interested in object having a value for 'time generated'.
        self.base_report = BaseReport(None, None, None, '2017-07-06 10:00:00')

    def call_test(self, data=None, spell=None, base_report=None):
        """
        Calls the method under test with sane defaults arguments unless they
        are passed in which case the defaults are overridden.

        :param data: Input data for the report such as start and end datetimes.
        :type data: nh.clinical.observation_report_wizard
        :param spell: Start and end datetimes for the spell.
        :type spell: dict
        :param base_report: Object with important datetimes found in the
        header of the report.
        :type base_report: BaseReport
        :return:
        """
        if data is None:
            data = self.data
        if spell is None:
            spell = self.spell_dictionary
        if base_report is None:
            base_report = self.base_report

        self.report_dates = self.report_model.process_report_dates(
            data, spell, base_report
        )

    def test_spell_start_equals_passed_spells_dict_date_started_key(self):
        """
        The spell_start attribute of the returned ReportDates object has the
        same value as the date_started key of the passed spell dictionary.
        """
        self.call_test()
        expected = self.spell_dictionary['date_started']
        actual = self.report_dates.spell_start
        self.assertEqual(expected, actual)

    def test_spell_end_equals_passed_spell_dicts_date_terminated_key(self):
        """
        The spell_end attribute of the returned ReportDates object has the
        same value as the date_terminated key of the passed spell dictionary.
        """
        self.call_test()
        expected = self.spell_dictionary['date_terminated']
        actual = self.report_dates.spell_end
        self.assertEqual(expected, actual)

    def test_report_start_equals_passed_report_period_start_datetime(self):
        """
        The report_start attribute of the returned ReportDates object has the
        same value as the start_time attribute of the passed data object if it
        exists.
        """
        self.call_test()
        expected = self.data.start_time
        actual = self.report_dates.report_start
        self.assertEqual(expected, actual)

    def test_report_start_equals_spell_start_when_no_passed_start_datetime(
            self):
        """
        The report_start attribute of the returned ReportDates object has the
        same value as the date_started attribute of the passed spell dictionary
        when there is no value for the start_time attribute of the passed date
        object.
        """
        self.call_test(data=self.data_empty)

        expected = self.spell_dictionary['date_started']
        actual = self.report_dates.report_start
        self.assertEqual(expected, actual)

    def test_report_end_equals_passed_report_period_end_datetime(self):
        """
        The report_end attribute of the returned ReportDates object has the
        same value as the end_time attribute of the passed data object if it
        exists.
        """
        self.call_test()
        expected = self.data.end_time
        actual = self.report_dates.report_end
        self.assertEqual(expected, actual)

    def test_report_end_equals_spell_end_when_no_passed_end_datetime(self):
        """
        The report_end attribute of the returned ReportDates object has the
        same value as the spell_end attribute of the passed spell dictionary
        when there is no value for the end_time attribute of the passed date
        object.
        """
        self.call_test(data=self.data_empty)

        expected = self.spell_dictionary['date_terminated']
        actual = self.report_dates.report_end
        self.assertEqual(expected, actual)

    def test_report_end_equals_time_generated_when_no_spell_end_or_datetime(
            self):
        """
        The report_end attribute of the returned ReportDates object has the
        same value as the datetime when the report was generated when there is
        no other values found for the spell_end attribute on the passed spell
        dictionary or the end_time attribute of the passed date object.
        """
        self.call_test(data=self.data_empty,
                       spell=self.spell_dictionary_no_date_terminated)

        expected = self.base_report.time_generated
        actual = self.report_dates.report_end
        self.assertEqual(expected, actual)
