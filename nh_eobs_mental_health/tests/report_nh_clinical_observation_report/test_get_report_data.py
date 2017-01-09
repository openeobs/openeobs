from openerp.addons.nh_eobs.report import helpers
from openerp.tests.common import TransactionCase

from . import patient_refusal_event_fixtures


class TestGetReportData(TransactionCase):
    """
    Test the override of the get_model_data_as_json that sets the score to
    false for refused observations so they show on the chart correctly
    """

    def setUp(self):
        super(TestGetReportData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']
        report_data = {
            'spell_id': 1,
            'start_date': None,
            'end_date': None,
            'ews_only': True
        }
        self.example_data = helpers.data_dict_to_obj(report_data)

    def test_full_report(self):
        """
        Test that the mental health JS is returned when EWS only is False
        """
        report_data = self.report_model.get_report_data(
            self.example_data, ews_only=False)
        self.assertEqual(
            report_data.get('draw_graph_js'),
            '/nh_eobs_mental_health/static/src/js/observation_report.js'
        )

    def test_ews_only(self):
        """
        Test that the mental health JS is returned when EWS only is True
        """
        report_data = self.report_model.get_report_data(
            self.example_data, ews_only=True)
        self.assertEqual(
            report_data.get('draw_graph_js'),
            '/nh_eobs_mental_health/static/src/js/observation_report.js'
        )

    def test_adds_patient_refusal_events_data_to_dict(self):
        self.report_model = self.env['report.nh.clinical.observation_report']
        self.report_model._patch_method(
            'get_refusal_episodes',
            patient_refusal_event_fixtures.mock_get_refusal_episodes
        )
        try:
            report_data = self.report_model.get_report_data(self.example_data)
            self.assertTrue('patient_refusal_events' in report_data)
            number_of_events = len(report_data['patient_refusal_events'])
            self.assertEqual(3, number_of_events)
        finally:
            self.report_model._revert_method('get_refusal_episodes')
