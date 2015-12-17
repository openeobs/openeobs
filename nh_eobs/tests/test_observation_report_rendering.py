from . import observation_report_helpers as helpers
from bs4 import BeautifulSoup


class TestObservationReportRendering(helpers.ObservationReportHelpers):

    def test_01_report_header_structure(self):
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': True
        }
        particularreport_obj = self.registry(self.report_model)
        report_html = particularreport_obj.render_html(
            self.cr, self.uid, [], data=report_data, context=None)
        beautiful_report = BeautifulSoup(report_html, 'html.parser')
        header_name = beautiful_report.select('.header .col-xs-9 h2')[0]
        self.assertEqual(
            header_name.string,
            'Test Patient',
            'Report header name is incorrect'
        )
