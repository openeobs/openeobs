from . import observation_report_helpers as helpers
from bs4 import BeautifulSoup
from datetime import datetime


class TestObservationReportRendering(helpers.ObservationReportHelpers):

    def test_01_report_header_structure(self):
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
        header_name = beautiful_report.select('.header .col-xs-9 h2')[0]
        self.assertEqual(
            header_name.string,
            'Test Patient',
            'Report header name is incorrect'
        )
        header_image = beautiful_report.select('.header .col-xs-3 img')[0]
        self.assertEqual(
            header_image['src'],
            'data:image/png;base64,{0}'.format(self.test_logo),
            'Report logo is incorrect'
        )

    def test_02_report_footer_structure(self):
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
        footer_info = beautiful_report.select('.footer .col-xs-9 p')[0]
        footer_image = footer_info.select('img')[0]
        footer_info = footer_info.text
        footer_has_name = 'Administrator' in footer_info
        date_string = datetime.now().strftime('%H:%M %d/%m/%y')
        footer_has_print_date = date_string in footer_info
        footer_has_hosp_name = 'Test Hospital' in footer_info
        footer_has_nhs_number = 'NHS1234123' in footer_info
        self.assertTrue(footer_has_name, 'Incorrect name in footer')
        self.assertTrue(footer_has_print_date, 'Incorrect date in footer')
        self.assertTrue(footer_has_hosp_name, 'Incorrect hosp name in footer')
        self.assertTrue(footer_has_nhs_number, 'Incorrect NHS num in footer')
        self.assertEqual(footer_image['src'],
                         '/nh_eobs/static/src/img/open_eobs_logo.png',
                         'Incorrect logo image linked to in footer')
        self.assertEqual(footer_image['alt'],
                         'Open-eObs',
                         'Incorrect alt tag for footer image')
