__author__ = 'lorenzo'
import logging
from lxml import etree
from openerp.addons.nh_eobs_mobile.controllers.urls import URLS
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering import MobileHTMLRenderingCase


_logger = logging.getLogger(__name__)


class TestPatientListHTML(MobileHTMLRenderingCase):
    """
    Test case collecting all the tests relating to the RENDERING of the 'patient list' page.
    Compare the actual rendered HTML pages against fixtures (i.e. 'fake' HTML files) specially built.
    """
    template_id = 'nh_eobs_mobile.patient_task_list'
    patients_fixtures = [
        {
            'url': '/mobile/patient/1',
            'color': 'level-not-set',
            'deadline_time': '04:00 hours',
            'full_name': 'Wren, Colin',
            'ews_score': 'False',
            'ews_trend': 'False',
            'location': 'Bed 1',
            'parent_location': 'Ward A'
        },
        {
            'url': '/mobile/patient/2',
            'color': 'level-none',
            'deadline_time': 'overdue: 23:00 hours',
            'full_name': 'Ortiz, Joel',
            'ews_score': 0,
            'ews_trend': 'same',
            'location': 'Bed 2',
            'parent_location': 'Ward A'
        },
        {
            'url': '/mobile/patient/3',
            'color': 'level-one',
            'deadline_time': 'overdue: 1 day 02:00 hours',
            'full_name': 'Earp, Will',
            'ews_score': 2,
            'ews_trend': 'up',
            'location': 'Bed 3',
            'parent_location': 'Ward A'
        },
        {
            'url': '/mobile/patient/4',
            'color': 'level-two',
            'deadline_time': '1 day 02:00 hours',
            'full_name': 'Lenz, Gregor',
            'ews_score': 5,
            'ews_trend': 'down',
            'location': 'Bed 4',
            'parent_location': 'Ward A'
        },
        {
            'url': '/mobile/patient/5',
            'color': 'level-three',
            'deadline_time': '00:00 hours',
            'full_name': 'Pascucci, Lorenzo',
            'ews_score': 8,
            'ews_trend': 'same',
            'location': 'Bed 5',
            'parent_location': 'Ward A'
        }
    ]

    def test_patient_list_page_with_no_data(self):
        """Test the 'patient list' page without any information in it."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'patient_list_empty.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide the template the data it needs for the rendering
        api_data = {
            'notifications': [],
            'items': [],
            'notification_count': 0,
            'followed_items': [],
            'section': 'patient',
            'username': 'nadine',
            'urls': URLS
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

    def test_patient_list_page_with_only_own_patients_data(self):
        """Test the 'patient list' page with information about own patients, but without data about followed patients."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'patient_list_data_no_follow_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Small fix for the patients data
        patients = self.patients_fixtures[:]
        for p in patients:
            if not p.get('summary'):
                p['summary'] = False

        # Set up specific data to provide the template the data it needs for the rendering
        api_data = {
            'notifications': [],
            'items': patients,
            'notification_count': 0,
            'followed_items': [],
            'section': 'patient',
            'username': 'nadine',
            'urls': URLS
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

    def test_patient_list_page_with_own_patients_data_and_invitation_data(self):
        """Test the 'patient list' page with information about own patients and invitation from other users."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'patient_list_data_no_follow_data_invitation.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Small fix for the patients data
        patients = self.patients_fixtures[:]
        for p in patients:
            if not p.get('summary'):
                p['summary'] = False

        # Set up specific data to provide the template the data it needs for the rendering
        notifications = [
            {
                'id': 1,
                'message': 'You have been invited to follow 1 patient(s) from Norah Miller'
            }
        ]

        api_data = {
            'notifications': notifications,
            'items': patients,
            'notification_count': 0,
            'followed_items': [],
            'section': 'patient',
            'username': 'nadine',
            'urls': URLS
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

    def test_patient_list_page_with_own_patients_and_followed_patients_data(self):
        """Test the 'patient list' page with information about own patients and followed ones."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'patient_list_data_follow_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide the template the data it needs for the rendering
        followed_patients = [
            {
                'url': '/mobile/patient/5',
                'color': 'level-three',
                'deadline_time': '00:00 hours',
                'full_name': 'Pascucci, Lorenzo',
                'ews_score': 8,
                'ews_trend': 'same',
                'location': 'Bed 5',
                'parent_location': 'Ward A'
            }
        ]

        # Small fix for the patients and followed_patients data
        patients = self.patients_fixtures[:-1]  # avoid duplicating last patient's data (he's already among the followed ones)
        for p in patients:
            if not p.get('summary'):
                p['summary'] = False
        for f_p in followed_patients:
            if not f_p.get('trend_icon') and f_p['ews_trend'] in ['up', 'down', 'same', 'first', 'not-set']:
                f_p['trend_icon'] = 'icon-{}-arrow'.format(f_p['ews_trend'])
            if not f_p.get('summary'):
                f_p['summary'] = False

        api_data = {
            'notifications': [],
            'items': patients,
            'notification_count': 0,
            'followed_items': followed_patients,
            'section': 'patient',
            'username': 'nadine',
            'urls': URLS
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
