__author__ = 'lorenzo'
import logging
import mock
from lxml import etree
from openerp.addons.nh_eobs_mobile.controllers.main import MobileFrontend
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering import MobileHTMLRenderingCase


_logger = logging.getLogger(__name__)


class TestTaskListHTML(MobileHTMLRenderingCase):
    """
    Test case collecting all the tests relating to the RENDERING of the 'task list' page.
    Compare the actual rendered HTML pages against fixtures (i.e. 'fake' HTML files) specially built.
    """

    def test_task_list_page_with_no_data(self):
        """Test the 'task list' page without any information in it."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_list_empty.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_data = []
        api_call = mock.Mock(return_value=api_data)

        # Stupid check if Mock is doing is work TODO: remove it !
        api_resp = api_call()
        api_call.assert_any_call()
        self.assertEqual(api_resp, api_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_tasks(mobile_frontend, api_call())
        self.assertEqual(rendered_template, expected_output)

    def test_task_list_page_with_tasks_data(self):
        """Test the 'task list' page with a list of tasks in it."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_list_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_data = [
            {
                'url': '/mobile/task/1',
                'color': 'level-not-set',
                'deadline_time': '04:00 hours',
                'full_name': 'Wren, Colin',
                'ews_score': False,
                'ews_trend': False,
                'location': 'Bed 1',
                'parent_location': 'Ward A',
                'summary': 'NEWS Observation'
            },
            {
                'url': '/mobile/task/2',
                'color': 'level-none',
                'deadline_time': 'overdue 23:00 hours',
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
                'deadline_time': 'overdue 1 day 02:00 hours',
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
        api_call = mock.Mock(return_value=api_data)

        # Stupid check if Mock is doing is work TODO: remove it !
        api_resp = api_call()
        api_call.assert_any_call()
        self.assertEqual(api_resp, api_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_tasks(mobile_frontend, api_call())
        self.assertEqual(rendered_template, expected_output)

    def test_task_list_page_with_tasks_data_and_notification(self):
        """Test the 'task list' page with a list of tasks in it and a notification counter."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'task_list_notification.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Mock the calling of an API method,
        # to provide the mobile controller's method the data it needs for the rendering
        api_tasks_data = [
            {
                'url': '/mobile/task/1',
                'color': 'level-not-set',
                'deadline_time': '04:00 hours',
                'full_name': 'Wren, Colin',
                'ews_score': False,
                'ews_trend': False,
                'location': 'Bed 1',
                'parent_location': 'Ward A',
                'summary': 'NEWS Observation'
            },
            {
                'url': '/mobile/task/2',
                'color': 'level-none',
                'deadline_time': 'overdue 23:00 hours',
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
                'deadline_time': 'overdue 1 day 02:00 hours',
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
        api_notification_counter_data = 666

        api_tasks = mock.Mock(return_value=api_tasks_data)
        api_notifications = mock.Mock(return_value=api_notification_counter_data)

        # Actually call the mobile controller's method and check its output against the expected one
        # TODO: find a way to successfully call the mobile controller method !!!
        mobile_frontend = MobileFrontend()
        rendered_template = mobile_frontend.get_tasks(mobile_frontend, api_tasks(), api_notifications())
        self.assertEqual(rendered_template, expected_output)