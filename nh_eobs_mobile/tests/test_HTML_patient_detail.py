__author__ = 'lorenzo'
import logging
import mock
from lxml import etree
from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering import MobileHTMLRenderingCase


_logger = logging.getLogger(__name__)


class TestPatientDetailHTML(MobileHTMLRenderingCase):
    """
    Test case collecting all the tests relating to the RENDERING of the 'patient detail' page.
    Compare the actual rendered HTML pages against fixtures (i.e. 'fake' HTML files) specially built.
    """

    def test_patient_detail_page_with_no_data(self):
        """Test the 'patient detail' page with just information about the patient (no observations' information)."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'patient_detail_no_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_data = {
            'patient_name': 'Wren, Colin',
            'patient_location': 'Ward A, Bed 01',
            'patient_id': 1,
            'news_deadline': '04:00 hours',
            'observations': []
        }
        api_call = mock.Mock(return_value=api_data)

        # Stupid check if Mock is doing is work TODO: remove it !
        api_resp = api_call()
        api_call.assert_any_call()
        self.assertEqual(api_resp, api_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_patient(mobile_frontend, api_call())
        self.assertEqual(rendered_template, expected_output)

    def test_patient_detail_page_with_observations_data(self):
        """
        Test the 'patient detail' page with:
            - information about the patient
            - a list of ad hoc observations to be taken
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'patient_detail_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_data = {
            'patient_name': 'Wren, Colin',
            'patient_location': 'Ward A, Bed 01',
            'patient_id': 1,
            'news_deadline': '04:00 hours',
            'observations': [
                'National Early Warning Score (NEWS)',
                'Glasgow Coma Scale (GCS)',
                'Height',
                'Weight',
                'Blood Product',
                'Blood Sugar',
                'Bristol Stool Scale',
                'Postural Blood Pressure'
            ]
        }
        api_call = mock.Mock(return_value=api_data)

        # Stupid check if Mock is doing is work TODO: remove it !
        api_resp = api_call()
        api_call.assert_any_call()
        self.assertEqual(api_resp, api_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_patient(mobile_frontend, api_call())
        self.assertEqual(rendered_template, expected_output)

    def test_patient_detail_page_with_observations_data_and_notification(self):
        """
        Test the 'patient detail' page with:
            - information about the patient
            - a list of ad hoc observations to be taken
            - number of notifications
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'patient_detail_data_notification.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_patient_data = {
            'patient_name': 'Wren, Colin',
            'patient_location': 'Ward A, Bed 01',
            'patient_id': 1,
            'news_deadline': '04:00 hours',
            'observations': [
                'National Early Warning Score (NEWS)',
                'Glasgow Coma Scale (GCS)',
                'Height',
                'Weight',
                'Blood Product',
                'Blood Sugar',
                'Bristol Stool Scale',
                'Postural Blood Pressure'
            ]
        }
        api_notification_counter_data = 666

        api_patient = mock.Mock(return_value=api_patient_data)
        api_notifications = mock.Mock(return_value=api_notification_counter_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_patient(mobile_frontend, api_patient(), api_notifications())
        self.assertEqual(rendered_template, expected_output)