from . import observation_report_helpers as helpers
from bs4 import BeautifulSoup
from datetime import datetime


class TestObservationTableRendering(helpers.ObservationReportHelpers):

    def test_01_ews_table_structure(self):
        """
        Test that the EWS table is rendering correctly when all data present
        """
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': True
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[0]
        table = header.parent.findNext('table')
        table_headers = table.select('th')
        table_columns = table.select('td')
        self.assertEqual(len(table_headers),
                         9,
                         'Incorrect number of table headers')
        self.assertEqual(len(table_columns),
                         9,
                         'Incorrect number of table columns')
        date_header = table_headers[0]
        resp_header = table_headers[1]
        ox_sat_header = table_headers[2]
        temp_header = table_headers[3]
        bp_sys_header = table_headers[4]
        bp_dia_header = table_headers[5]
        pulse_header = table_headers[6]
        avpu_header = table_headers[7]
        sup_ox_header = table_headers[8]
        date_column = table_columns[0]
        resp_column = table_columns[1]
        ox_sat_column = table_columns[2]
        temp_column = table_columns[3]
        bp_sys_column = table_columns[4]
        bp_dia_column = table_columns[5]
        pulse_column = table_columns[6]
        avpu_column = table_columns[7]
        sup_ox_column = table_columns[8]
        self.assertEqual(date_header.text,
                         'Date',
                         'Incorrect date table header')
        date_term = self.ews_values['date_terminated']
        test_date_term = datetime.strptime(date_term, self.odoo_date_format)\
            .strftime(self.pretty_date_format)
        self.assertEqual(date_column.text,
                         test_date_term,
                         'Incorrect date table column')
        self.assertEqual(resp_header.text,
                         'RespirationRate',
                         'Incorrect resp rate table header')
        self.assertEqual(resp_column.text,
                         '%s' % self.ews_values['respiration_rate'],
                         'Incorrect resp rate table column')
        self.assertEqual(ox_sat_header.text,
                         'O2Saturation',
                         'Incorrect o2 saturation table header')
        ox_sat = self.ews_values['indirect_oxymetry_spo2']
        ox_target = 'Target: 0-100'
        self.assertEqual(ox_sat_column.text,
                         '{0}{1}'.format(ox_sat, ox_target),
                         'Incorrect o2 saturation table column')
        self.assertEqual(temp_header.text,
                         'BodyTemperature',
                         'Incorrect temperature table header')
        self.assertEqual(temp_column.text,
                         '%s' % self.ews_values['body_temperature'],
                         'Incorrect temperature table column')
        self.assertEqual(bp_sys_header.text,
                         'BloodPressureSystolic',
                         'Incorrect systolic blood pressure table header')
        self.assertEqual(bp_sys_column.text,
                         '%s' % self.ews_values['blood_pressure_systolic'],
                         'Incorrect systolic blood pressure table column')
        self.assertEqual(bp_dia_header.text,
                         'BloodPressureDiastolic',
                         'Incorrect diastolic blood pressure table header')
        self.assertEqual(bp_dia_column.text,
                         '%s' % self.ews_values['blood_pressure_diastolic'],
                         'Incorrect diastolic blood pressure table column')
        self.assertEqual(pulse_header.text,
                         'PulseRate',
                         'Incorrect pulse table header')
        self.assertEqual(pulse_column.text,
                         '%s' % self.ews_values['pulse_rate'],
                         'Incorrect pulse table column')
        self.assertEqual(avpu_header.text,
                         'AVPU',
                         'Incorrect avpu table header')
        self.assertEqual(avpu_column.text,
                         self.ews_values['avpu_text'],
                         'Incorrect avpu table column')
        self.assertEqual(sup_ox_header.text,
                         'Supplemental O2',
                         'Incorrect supplemental oxygen table header')
        self.assertEqual(sup_ox_column.text.strip(),
                         'See table',
                         'Incorrect supplemental oxygen table column')

    def test_02_ews_table_structure_no_target(self):
        """
        Test that the EWS table is rendering correctly when all data present
        """

        self.o2target_id = []
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': True
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[0]
        table = header.parent.findNext('table')
        table_columns = table.select('td')
        ox_sat_column = table_columns[2]
        ox_sat = self.ews_values['indirect_oxymetry_spo2']
        self.assertEqual(ox_sat_column.text,
                         '{0}'.format(ox_sat),
                         'Incorrect o2 saturation table column')

    def test_03_ews_table_structure_no_supplement_oxygen(self):
        """
        Test that the EWS table is rendering correctly when all data present
        """

        self.ews_values['oxygen_administration_flag'] = 0
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': True
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[0]
        table = header.parent.findNext('table')
        table_columns = table.select('td')
        sup_ox_column = table_columns[8]
        self.assertEqual(sup_ox_column.text,
                         '\n',
                         'Incorrect supplemental oxygen table column')
