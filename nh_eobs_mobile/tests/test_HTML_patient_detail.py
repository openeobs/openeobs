__author__ = 'lorenzo'
import logging
import mock
from lxml import etree
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering import MobileHTMLRenderingCase


_logger = logging.getLogger(__name__)


class TestPatientDetailHTML(MobileHTMLRenderingCase):
    """Test case collecting all the tests relating to the RENDERING of the 'patient detail' page.
    Compare the actual rendered HTML pages against fixtures (i.e. 'fake' HTML files) specially built.
    """
    template_id = 'nh_eobs_mobile.patient'

    def setUp(self):
        super(TestPatientDetailHTML, self).setUp()
        self.observations = [
            {
                'type': 'ews',
                'name': 'National Early Warning Score (NEWS)'
            },
            {
                'type': 'gcs',
                'name': 'Glasgow Coma Scale (GCS)'
            },
            {
                'type': 'height',
                'name': 'Height'
            },
            {
                'type': 'weight',
                'name': 'Weight'
            },
            {
                'type': 'blood_product',
                'name': 'Blood Product'
            },
            {
                'type': 'blood_sugar',
                'name': 'Blood Sugar'
            },
            {
                'type': 'stools',
                'name': 'Bristol Stool Scale'
            },
            {
                'type': 'pbp',
                'name': 'Postural Blood Pressure'
            }
        ]
        self.patient_data = {
            'full_name': 'Wren, Colin',
            'location': 'Ward A, Bed 01',
            'id': 1,
            'next_ews_time': '04:00 hours',
        }

    def test_patient_detail_page_with_no_data(self):
        """Test the 'patient detail' page with only information about the patient (no observations' information)."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'patient_detail_no_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide the template the data it needs for the rendering
        api_data = {
            'patient': self.patient_data,
            'urls': self.controller_urls,
            'section': 'patient',
            'obs_list': [],
            'notification_count': 0,
            'username': 'norah'
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and convert it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small fix for the comparison's sake
        compressed_rendered_parsed = self._compress_string('<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(compressed_expected_output, compressed_rendered_parsed)

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
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide the template the data it needs for the rendering

        api_data = {
            'patient': self.patient_data,
            'urls': self.controller_urls,
            'section': 'patient',
            'obs_list': self.observations,
            'notification_count': 0,
            'username': 'norah'
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and convert it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small fix for the comparison's sake
        compressed_rendered_parsed = self._compress_string('<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(compressed_expected_output, compressed_rendered_parsed)

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
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide the template the data it needs for the rendering
        api_data = {
            'patient': self.patient_data,
            'urls': self.controller_urls,
            'section': 'patient',
            'obs_list': self.observations,
            'notification_count': 666,
            'username': 'norah'
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and convert it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small fix for the comparison's sake
        compressed_rendered_parsed = self._compress_string('<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(compressed_expected_output, compressed_rendered_parsed)