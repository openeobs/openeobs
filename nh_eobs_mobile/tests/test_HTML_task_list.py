__author__ = 'lorenzo'
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import logging
from lxml import etree
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering import MobileHTMLRenderingCase


_logger = logging.getLogger(__name__)


class TestTaskListHTML(MobileHTMLRenderingCase):
    """Test case collecting all the tests relating to the RENDERING of the 'task list' page.
    Compare the actual rendered HTML pages against fixtures (i.e. 'fake' HTML files) specially built.
    """
    template_id = 'nh_eobs_mobile.patient_task_list'

    def setUp(self):
        super(TestTaskListHTML, self).setUp()
        self.tasks_fixtures = [
            {
                'url': '/mobile/task/1',
                'color': 'level-not-set',
                'deadline_time': '04:00 hours',
                'full_name': 'Wren, Colin',
                'ews_score': 'False',
                'ews_trend': 'not-set',
                'location': 'Bed 1',
                'parent_location': 'Ward A',
                'summary': 'NEWS Observation'
            },
            {
                'url': '/mobile/task/2',
                'color': 'level-none',
                'deadline_time': 'overdue: 23:00 hours',
                'full_name': 'Ortiz, Joel',
                'ews_score': 0,
                'ews_trend': 'same',
                'notification': True,
                'location': 'Bed 2',
                'parent_location': 'Ward A',
                'summary': 'Assess Patient'
            },
            {
                'url': '/mobile/task/3',
                'color': 'level-one',
                'deadline_time': 'overdue: 1 day 02:00 hours',
                'full_name': 'Earp, Will',
                'ews_score': 2,
                'ews_trend': 'up',
                'location': 'Bed 3',
                'parent_location': 'Ward A',
                'summary': 'GCS Observation'
            },
            {
                'url': '/mobile/task/4',
                'color': 'level-two',
                'deadline_time': '1 day 02:00 hours',
                'full_name': 'Lenz, Gregor',
                'ews_score': 5,
                'ews_trend': 'down',
                'location': 'Bed 4',
                'notification': True,
                'parent_location': 'Ward A',
                'summary': 'Urgently inform medical team'
            },
            {
                'url': '/mobile/task/5',
                'color': 'level-three',
                'deadline_time': '00:00 hours',
                'full_name': 'Pascucci, Lorenzo',
                'ews_score': 8,
                'ews_trend': 'same',
                'location': 'Bed 5',
                'parent_location': 'Ward A',
                'summary': 'NEWS Observation'
            },
        ]

    def test_task_list_page_with_no_data(self):
        """Test the 'task list' page without any information in it."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_list_empty.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide the template the data it needs for the rendering
        api_data = {
            'items': [],
            'section': 'task',
            'username': 'nadine',
            'notification_count': 0,
            'urls': self.controller_urls,
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

    def test_task_list_page_with_tasks_data(self):
        """Test the 'task list' page with a list of tasks in it."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_list_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide the template the data it needs for the rendering
        api_data = {
            'items': self.tasks_fixtures,
            'section': 'task',
            'username': 'nadine',
            'notification_count': 0,
            'urls': self.controller_urls,
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

    def test_task_list_page_with_tasks_data_and_notification(self):
        """Test the 'task list' page with a list of tasks in it and a notification counter."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_list_notification.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide the template the data it needs for the rendering
        api_data = {
            'items': self.tasks_fixtures,
            'section': 'task',
            'username': 'nadine',
            'notification_count': 666,
            'urls': self.controller_urls,
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