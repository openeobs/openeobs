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
        table = header.findNext('table')
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
        Test that the EWS table is rendering correctly when no oxygen target
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
        table = header.findNext('table')
        table_columns = table.select('td')
        ox_sat_column = table_columns[2]
        ox_sat = self.ews_values['indirect_oxymetry_spo2']
        self.assertEqual(ox_sat_column.text,
                         '{0}'.format(ox_sat),
                         'Incorrect o2 saturation table column')

    def test_03_ews_table_structure_no_supplement_oxygen(self):
        """
        Test that the EWS table is rendering correctly when no supplemental o2
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
        table = header.findNext('table')
        table_columns = table.select('td')
        sup_ox_column = table_columns[8]
        self.assertEqual(sup_ox_column.text,
                         '\n',
                         'Incorrect supplemental oxygen table column')

    def test_04_ews_supplmental_oxygen_table_structure_all(self):
        """
        Test that the supplemental oxygen table renders correctly
        """
        self.ews_values['oxygen_administration_flag'] = True
        self.ews_values['flow_rate'] = 1
        self.ews_values['concentration'] = 2
        self.ews_values['cpap_peep'] = 3
        self.ews_values['niv_backup'] = 4
        self.ews_values['niv_ipap'] = 5
        self.ews_values['niv_epap'] = 6

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
        header = beautiful_report.select('h4')[0]
        table = header.findNext('table')
        table_headers = table.select('th')
        table_columns = table.select('tbody > tr > td')
        self.assertEqual(len(table_headers),
                         3,
                         'Incorrect number of table headers')
        self.assertEqual(len(table_columns),
                         3,
                         'Incorrect number of table columns')
        date_header = table_headers[0]
        device_header = table_headers[1]
        values_header = table_headers[2]
        date_column = table_columns[0]
        device_column = table_columns[1]
        values_column = table_columns[2]
        self.assertEqual(date_header.text,
                         'Date',
                         'Incorrect date table header')
        date_term = self.ews_values['date_terminated']
        test_date_term = datetime.strptime(date_term, self.odoo_date_format)\
            .strftime(self.pretty_date_format)
        self.assertEqual(date_column.text,
                         test_date_term,
                         'Incorrect date table column')
        self.assertEqual(device_header.text,
                         'Device',
                         'Incorrect device table header')
        self.assertEqual(device_column.text,
                         self.ews_values['device_id'][1],
                         'Incorrect device table column')
        self.assertEqual(values_header.text,
                         'Values',
                         'Incorrect value table header')
        self.assertEqual(
            values_column.text.strip().replace('\n', ''),
            'Flow Rate:1Concentration:2CPAP PEEP (cmH2O):3NIV Back-up rate '
            '(br/min):4NIV IPAP (cmH2O):5NIV EPAP (cmH2O):6',
            'Incorrect value table column'
        )

    def test_05_ews_sup_o2_table_structure_no_flow(self):
        """
        Test that the supplemental oxygen table renders correctly without flow
        """
        self.ews_values['oxygen_administration_flag'] = True
        self.ews_values['flow_rate'] = 0
        self.ews_values['concentration'] = 2
        self.ews_values['cpap_peep'] = 3
        self.ews_values['niv_backup'] = 4
        self.ews_values['niv_ipap'] = 5
        self.ews_values['niv_epap'] = 6

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
        header = beautiful_report.select('h4')[0]
        table = header.findNext('table')
        table_columns = table.select('tbody > tr > td')
        values_column = table_columns[2]
        self.assertEqual(
            values_column.text.strip().replace('\n', ''),
            'Concentration:2CPAP PEEP (cmH2O):3NIV Back-up rate '
            '(br/min):4NIV IPAP (cmH2O):5NIV EPAP (cmH2O):6',
            'Incorrect value table column'
        )

    def test_06_ews_sup_o2_table_structure_no_concentration(self):
        """
        Test that the supplemental oxygen table renders correctly without
        concentration
        """
        self.ews_values['oxygen_administration_flag'] = True
        self.ews_values['flow_rate'] = 1
        self.ews_values['concentration'] = 0
        self.ews_values['cpap_peep'] = 3
        self.ews_values['niv_backup'] = 4
        self.ews_values['niv_ipap'] = 5
        self.ews_values['niv_epap'] = 6

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
        header = beautiful_report.select('h4')[0]
        table = header.findNext('table')
        table_columns = table.select('tbody > tr > td')
        values_column = table_columns[2]
        self.assertEqual(
            values_column.text.strip().replace('\n', ''),
            'Flow Rate:1CPAP PEEP (cmH2O):3NIV Back-up rate '
            '(br/min):4NIV IPAP (cmH2O):5NIV EPAP (cmH2O):6',
            'Incorrect value table column'
        )

    def test_07_ews_sup_o2_table_structure_no_cpap(self):
        """
        Test that the supplemental oxygen table renders correctly without cpap
        """
        self.ews_values['oxygen_administration_flag'] = True
        self.ews_values['flow_rate'] = 1
        self.ews_values['concentration'] = 2
        self.ews_values['cpap_peep'] = 0
        self.ews_values['niv_backup'] = 4
        self.ews_values['niv_ipap'] = 5
        self.ews_values['niv_epap'] = 6

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
        header = beautiful_report.select('h4')[0]
        table = header.findNext('table')
        table_columns = table.select('tbody > tr > td')
        values_column = table_columns[2]
        self.assertEqual(
            values_column.text.strip().replace('\n', ''),
            'Flow Rate:1Concentration:2NIV Back-up rate '
            '(br/min):4NIV IPAP (cmH2O):5NIV EPAP (cmH2O):6',
            'Incorrect value table column'
        )

    def test_08_ews_sup_o2_table_structure_no_nivbackup(self):
        """
        Test that the supplemental oxygen table renders correctly without niv
        backup
        """
        self.ews_values['oxygen_administration_flag'] = True
        self.ews_values['flow_rate'] = 1
        self.ews_values['concentration'] = 2
        self.ews_values['cpap_peep'] = 3
        self.ews_values['niv_backup'] = 0
        self.ews_values['niv_ipap'] = 5
        self.ews_values['niv_epap'] = 6

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
        header = beautiful_report.select('h4')[0]
        table = header.findNext('table')
        table_columns = table.select('tbody > tr > td')
        values_column = table_columns[2]
        self.assertEqual(
            values_column.text.strip().replace('\n', ''),
            'Flow Rate:1Concentration:2CPAP PEEP (cmH2O):3'
            'NIV IPAP (cmH2O):5NIV EPAP (cmH2O):6',
            'Incorrect value table column'
        )

    def test_09_ews_sup_o2_table_structure_no_nivipap(self):
        """
        Test that the supplemental oxygen table renders correctly without niv
        ipap
        """
        self.ews_values['oxygen_administration_flag'] = True
        self.ews_values['flow_rate'] = 1
        self.ews_values['concentration'] = 2
        self.ews_values['cpap_peep'] = 3
        self.ews_values['niv_backup'] = 4
        self.ews_values['niv_ipap'] = 0
        self.ews_values['niv_epap'] = 6

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
        header = beautiful_report.select('h4')[0]
        table = header.findNext('table')
        table_columns = table.select('tbody > tr > td')
        values_column = table_columns[2]
        self.assertEqual(
            values_column.text.strip().replace('\n', ''),
            'Flow Rate:1Concentration:2CPAP PEEP (cmH2O):3NIV Back-up rate '
            '(br/min):4NIV EPAP (cmH2O):6',
            'Incorrect value table column'
        )

    def test_10_ews_sup_o2_table_structure_no_niv_epap(self):
        """
        Test that the supplemental oxygen table renders correctly
        """
        self.ews_values['oxygen_administration_flag'] = True
        self.ews_values['flow_rate'] = 1
        self.ews_values['concentration'] = 2
        self.ews_values['cpap_peep'] = 3
        self.ews_values['niv_backup'] = 4
        self.ews_values['niv_ipap'] = 5
        self.ews_values['niv_epap'] = 0

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
        header = beautiful_report.select('h4')[0]
        table = header.findNext('table')
        table_columns = table.select('tbody > tr > td')
        values_column = table_columns[2]
        self.assertEqual(
            values_column.text.strip().replace('\n', ''),
            'Flow Rate:1Concentration:2CPAP PEEP (cmH2O):3NIV Back-up rate '
            '(br/min):4NIV IPAP (cmH2O):5',
            'Incorrect value table column'
        )

    def test_11_weight_table_structure(self):
        """
        Test that the weight table is rendering correctly
        """
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': False
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[1]
        table = header.findNext('table')
        table_headers = table.select('th')
        table_columns = table.select('td')
        self.assertEqual(len(table_headers),
                         2,
                         'Incorrect number of table headers')
        self.assertEqual(len(table_columns),
                         2,
                         'Incorrect number of table columns')
        date_header = table_headers[0]
        weight_header = table_headers[1]
        date_column = table_columns[0]
        weight_column = table_columns[1]
        self.assertEqual(date_header.text,
                         'Date',
                         'Incorrect date table header')
        date_term = self.weight_values['date_terminated']
        test_date_term = datetime.strptime(date_term, self.odoo_date_format)\
            .strftime(self.pretty_date_format)
        self.assertEqual(date_column.text,
                         test_date_term,
                         'Incorrect date table column')
        self.assertEqual(weight_header.text,
                         'Value',
                         'Incorrect weight table header')
        self.assertEqual(weight_column.text,
                         '%s' % self.weight_values['weight'],
                         'Incorrect weight table column')

    def test_12_gcs_table_structure(self):
        """
        Test that the gcs table is rendering correctly
        """
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': False
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[2]
        table = header.findNext('table')
        table_headers = table.select('th')
        table_columns = table.select('td')
        self.assertEqual(len(table_headers),
                         4,
                         'Incorrect number of table headers')
        self.assertEqual(len(table_columns),
                         4,
                         'Incorrect number of table columns')
        date_header = table_headers[0]
        eyes_header = table_headers[1]
        verbal_header = table_headers[2]
        motor_header = table_headers[3]
        date_column = table_columns[0]
        eyes_column = table_columns[1]
        verbal_column = table_columns[2]
        motor_column = table_columns[3]
        self.assertEqual(date_header.text,
                         'Date',
                         'Incorrect date table header')
        date_term = self.gcs_values['date_terminated']
        test_date_term = datetime.strptime(date_term, self.odoo_date_format)\
            .strftime(self.pretty_date_format)
        self.assertEqual(date_column.text,
                         test_date_term,
                         'Incorrect date table column')
        self.assertEqual(eyes_header.text,
                         'Eyes',
                         'Incorrect eyes table header')
        self.assertEqual(eyes_column.text,
                         '%s' % self.gcs_values['eyes'],
                         'Incorrect eyes table column')
        self.assertEqual(motor_header.text,
                         'Motor',
                         'Incorrect motor table header')
        self.assertEqual(motor_column.text,
                         '%s' % self.gcs_values['motor'],
                         'Incorrect motor table column')
        self.assertEqual(verbal_header.text,
                         'Verbal',
                         'Incorrect verbal table header')
        self.assertEqual(verbal_column.text,
                         '%s' % self.gcs_values['verbal'],
                         'Incorrect verbal table column')

    def test_13_blood_sugar_table_structure(self):
        """
        Test that the blood sugar table is rendering correctly
        """
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': False
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[3]
        table = header.findNext('table')
        table_headers = table.select('th')
        table_columns = table.select('td')
        self.assertEqual(len(table_headers),
                         2,
                         'Incorrect number of table headers')
        self.assertEqual(len(table_columns),
                         2,
                         'Incorrect number of table columns')
        date_header = table_headers[0]
        bs_header = table_headers[1]
        date_column = table_columns[0]
        bs_column = table_columns[1]
        self.assertEqual(date_header.text,
                         'Date',
                         'Incorrect date table header')
        date_term = self.blood_sugar_values['date_terminated']
        test_date_term = datetime.strptime(date_term, self.odoo_date_format)\
            .strftime(self.pretty_date_format)
        self.assertEqual(date_column.text,
                         test_date_term,
                         'Incorrect date table column')
        self.assertEqual(bs_header.text,
                         'Blood Sugar (mmol/L)',
                         'Incorrect blood sugar table header')
        self.assertEqual(bs_column.text,
                         '%s' % self.blood_sugar_values['blood_sugar'],
                         'Incorrect blood sugar table column')

    def test_14_pain_table_structure(self):
        """
        Test that the pain score table is rendering correctly
        """
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': False
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[4]
        table = header.findNext('table')
        table_headers = table.select('th')
        table_columns = table.select('td')
        self.assertEqual(len(table_headers),
                         3,
                         'Incorrect number of table headers')
        self.assertEqual(len(table_columns),
                         3,
                         'Incorrect number of table columns')
        date_header = table_headers[0]
        resting_header = table_headers[1]
        movement_header = table_headers[2]
        date_column = table_columns[0]
        resting_column = table_columns[1]
        movement_column = table_columns[2]
        self.assertEqual(date_header.text,
                         'Date',
                         'Incorrect date table header')
        date_term = self.pain_values['date_terminated']
        test_date_term = datetime.strptime(date_term, self.odoo_date_format)\
            .strftime(self.pretty_date_format)
        self.assertEqual(date_column.text,
                         test_date_term,
                         'Incorrect date table column')
        self.assertEqual(resting_header.text,
                         'Resting Score',
                         'Incorrect resting score table header')
        self.assertEqual(resting_column.text,
                         '%s' % self.pain_values['rest_score'],
                         'Incorrect resting score table column')
        self.assertEqual(movement_header.text,
                         'Movement Score',
                         'Incorrect movement score table header')
        self.assertEqual(movement_column.text,
                         '%s' % self.pain_values['movement_score'],
                         'Incorrect movement score table column')

    def test_15_blood_product_table_structure(self):
        """
        Test that the blood product table is rendering correctly
        """
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': False
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[5]
        table = header.findNext('table')
        table_headers = table.select('th')
        table_columns = table.select('td')
        self.assertEqual(len(table_headers),
                         3,
                         'Incorrect number of table headers')
        self.assertEqual(len(table_columns),
                         3,
                         'Incorrect number of table columns')
        date_header = table_headers[0]
        vol_header = table_headers[1]
        product_header = table_headers[2]
        date_column = table_columns[0]
        vol_column = table_columns[1]
        product_column = table_columns[2]
        self.assertEqual(date_header.text,
                         'Date',
                         'Incorrect date table header')
        date_term = self.blood_product_values['date_terminated']
        test_date_term = datetime.strptime(date_term, self.odoo_date_format)\
            .strftime(self.pretty_date_format)
        self.assertEqual(date_column.text,
                         test_date_term,
                         'Incorrect date table column')
        self.assertEqual(vol_header.text,
                         'Vol (ml)',
                         'Incorrect vol table header')
        self.assertEqual(vol_column.text,
                         '%s' % self.blood_product_values['vol'],
                         'Incorrect vol table column')
        self.assertEqual(product_header.text,
                         'Blood Product',
                         'Incorrect blood product table header')
        self.assertEqual(product_column.text,
                         '%s' % self.blood_product_values['product'],
                         'Incorrect blood product table column')
        
    def test_16_bristol_stools_table_structure(self):
        """
        Test that the bristol stools table is rendering correctly
        """
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': False
        }
        report_obj = self.registry(self.report_model)
        report_html = report_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header = beautiful_report.select('h3')[6]
        table = header.findNext('table')
        table_headers = table.select('th')
        table_columns = table.select('td')
        self.assertEqual(len(table_headers),
                         12,
                         'Incorrect number of table headers')
        self.assertEqual(len(table_columns),
                         12,
                         'Incorrect number of table columns')
        date_header = table_headers[0]
        bowel_open_header = table_headers[1]
        nausea_header = table_headers[2]
        vomiting_header = table_headers[3]
        quantity_header = table_headers[4]
        colour_header = table_headers[5]
        bristol_type_header = table_headers[6]
        offensive_header = table_headers[7]
        strain_header = table_headers[8]
        laxatives_header = table_headers[9]
        samples_header = table_headers[10]
        rectal_exam_header = table_headers[11]
        date_column = table_columns[0]
        bowel_open_column = table_columns[1]
        nausea_column = table_columns[2]
        vomiting_column = table_columns[3]
        quantity_column = table_columns[4]
        colour_column = table_columns[5]
        bristol_type_column = table_columns[6]
        offensive_column = table_columns[7]
        strain_column = table_columns[8]
        laxatives_column = table_columns[9]
        samples_column = table_columns[10]
        rectal_exam_column = table_columns[11]
        self.assertEqual(date_header.text,
                         'Date',
                         'Incorrect date table header')
        date_term = self.stools_values['date_terminated']
        test_date_term = datetime.strptime(date_term, self.odoo_date_format)\
            .strftime(self.pretty_date_format)
        self.assertEqual(date_column.text,
                         test_date_term,
                         'Incorrect date table column')
        self.assertEqual(bowel_open_header.text,
                         'Bowel Open',
                         'Incorrect bowel table header')
        self.assertEqual(
            bowel_open_column.text,
            self.boolean_to_text(self.stools_values['bowel_open']),
            'Incorrect bowel_open table column'
        )
        self.assertEqual(nausea_header.text,
                         'Nausea',
                         'Incorrect bowel table header')
        self.assertEqual(
            nausea_column.text,
            self.boolean_to_text(self.stools_values['nausea']),
            'Incorrect nausea table column'
        )
        self.assertEqual(vomiting_header.text,
                         'Vomiting',
                         'Incorrect bowel table header')
        self.assertEqual(
            vomiting_column.text,
            self.boolean_to_text(self.stools_values['vomiting']),
            'Incorrect vomiting table column'
        )
        self.assertEqual(quantity_header.text,
                         'Quantity',
                         'Incorrect bowel table header')
        self.assertEqual(
            quantity_column.text,
            self.stools_values['quantity'],
            'Incorrect quantity table column'
        )
        self.assertEqual(colour_header.text,
                         'Colour',
                         'Incorrect bowel table header')
        self.assertEqual(
            colour_column.text,
            self.stools_values['colour'],
            'Incorrect colour table column'
        )
        self.assertEqual(bristol_type_header.text,
                         'Bristol Type',
                         'Incorrect bowel table header')
        self.assertEqual(
            bristol_type_column.text,
            self.stools_values['bristol_type'],
            'Incorrect bristol_type table column'
        )
        self.assertEqual(offensive_header.text,
                         'Offensive',
                         'Incorrect bowel table header')
        self.assertEqual(
            offensive_column.text,
            self.boolean_to_text(self.stools_values['offensive']),
            'Incorrect offensive table column'
        )
        self.assertEqual(strain_header.text,
                         'Strain',
                         'Incorrect bowel table header')
        self.assertEqual(
            strain_column.text,
            self.boolean_to_text(self.stools_values['strain']),
            'Incorrect strain table column'
        )
        self.assertEqual(laxatives_header.text,
                         'Laxatives',
                         'Incorrect bowel table header')
        self.assertEqual(
            laxatives_column.text,
            self.boolean_to_text(self.stools_values['laxatives']),
            'Incorrect laxatives table column'
        )
        self.assertEqual(samples_header.text,
                         'Samples',
                         'Incorrect bowel table header')
        self.assertEqual(
            samples_column.text,
            self.stools_values['samples'],
            'Incorrect samples table column'
        )
        self.assertEqual(rectal_exam_header.text,
                         'Rectal Exam',
                         'Incorrect bowel table header')
        self.assertEqual(
            rectal_exam_column.text,
            self.boolean_to_text(self.stools_values['rectal_exam']),
            'Incorrect rectal_exam table column'
        )
