# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from lxml import etree
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering \
    import MobileHTMLRenderingCase
import logging

_logger = logging.getLogger(__name__)


class TestStandInListHTML(MobileHTMLRenderingCase):
    """Test case collecting all the tests relating to the
    RENDERING of the 'stand in' page.
    Compare the actual rendered HTML pages against fixtures
    (i.e. 'fake' HTML files) specially built.
    """
    template_id = 'nh_eobs_mobile.share_patients_list'

    def setUp(self):
        super(TestStandInListHTML, self).setUp()
        self.patients_fixtures = [
            {
                'id': 1,
                'color': 'level-not-set',
                'deadline_time': '04:00 hours',
                'full_name': 'Wren, Colin',
                'ews_score': 'False',
                'ews_trend': 'False',
                'location': 'Bed 1',
                'parent_location': 'Ward A'
            },
            {
                'id': 2,
                'color': 'level-none',
                'deadline_time': 'overdue: 23:00 hours',
                'full_name': 'Ortiz, Joel',
                'ews_score': 0,
                'ews_trend': 'same',
                'location': 'Bed 2',
                'parent_location': 'Ward A'
            },
            {
                'id': 3,
                'color': 'level-one',
                'deadline_time': 'overdue: 1 day 02:00 hours',
                'full_name': 'Earp, Will',
                'ews_score': 2,
                'ews_trend': 'up',
                'location': 'Bed 3',
                'parent_location': 'Ward A'
            },
            {
                'id': 4,
                'color': 'level-two',
                'deadline_time': '1 day 02:00 hours',
                'full_name': 'Lenz, Gregor',
                'ews_score': 5,
                'ews_trend': 'down',
                'location': 'Bed 4',
                'parent_location': 'Ward A',
                'invited_users': 'Harold Bishop, Norah Miller'
            },
            {
                'id': 5,
                'color': 'level-three',
                'deadline_time': '00:00 hours',
                'full_name': 'Pascucci, Lorenzo',
                'ews_score': 8,
                'ews_trend': 'same',
                'location': 'Bed 5',
                'parent_location': 'Ward A',
                'invited_users': 'Harold Bishop, Norah Miller',
                'followers': 'Harold Bishop'
            }
        ]

    def test_stand_in_list_page_with_no_data(self):
        """Test the 'stand in' page without any information in it."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile
        # controller's method's result against
        fixture_name = 'stand_in_list_empty.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning(
                'IOError: Error reading fixture "{}". Hence, '
                'this test has not been actually executed'.format(
                    fixture_name
                )
            )

        # Set up specific data to provide the template the data it
        # needs for the rendering
        api_data = {
            'items': [],
            'section': 'patient',
            'username': 'nadine',
            'share_list': True,
            'notification_count': 0,
            'urls': self.controller_urls,
            'user_id': self.uid
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and
        # convert it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(
            self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small fix
        # for the comparison's sake
        compressed_rendered_parsed = self._compress_string(
            '<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(
            compressed_expected_output,
            compressed_rendered_parsed
        )

    def test_stand_in_list_page_with_patients_data(self):
        """Test the 'stand in' page with a list of patients in it."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile
        # controller's method's result against
        fixture_name = 'stand_in_list_data.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning(
                'IOError: Error reading fixture "{}". Hence, '
                'this test has not been actually executed'.format(
                    fixture_name)
            )

        # Small fix for the patients data
        patients = self.patients_fixtures[:]
        for p in patients:
            if not p.get('trend_icon') and p['ews_trend'] in ['up',
                                                              'down',
                                                              'same',
                                                              'first',
                                                              'not-set']:
                p['trend_icon'] = 'icon-{}-arrow'.format(p['ews_trend'])

        # Set up specific data to provide the template the data it
        # needs for the rendering
        api_data = {
            'items': patients,
            'section': 'patient',
            'username': 'nadine',
            'share_list': True,
            'notification_count': 0,
            'urls': self.controller_urls,
            'user_id': self.uid
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and convert
        # it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(
            self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small fix for
        # the comparison's sake
        compressed_rendered_parsed = self._compress_string(
            '<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(
            compressed_expected_output,
            compressed_rendered_parsed
        )

    def test_stand_in_list_page_with_patients_data_and_notification(self):
        """Test the 'stand in' page with a list of patients in it
         and a notification counter."""
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile
        # controller's method's result against
        fixture_name = 'stand_in_list_notification.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree, method='html')
        else:
            _logger.warning(
                'IOError: Error reading fixture "{}". Hence, '
                'this test has not been actually executed'.format(
                    fixture_name)
            )

        # Small fix for the patients data
        patients = self.patients_fixtures[:]
        for p in patients:
            if not p.get('trend_icon') and p['ews_trend'] in ['up',
                                                              'down',
                                                              'same',
                                                              'first',
                                                              'not-set']:
                p['trend_icon'] = 'icon-{}-arrow'.format(p['ews_trend'])

        # Set up specific data to provide the template the data
        # it needs for the rendering
        api_data = {
            'items': patients,
            'section': 'patient',
            'username': 'nadine',
            'share_list': True,
            'notification_count': 666,
            'urls': self.controller_urls,
            'user_id': self.uid
        }

        # Test the template rendering.
        # Pass the rendered template through the parser and
        # convert it back to string.
        # This way it's 'string-comparable' with the fixture file parsed above.
        rendered_template = self._render_template(
            self.cr, self.uid, self.template_id, options=api_data)
        temp_tree = etree.fromstring(rendered_template)
        rendered_and_parsed = etree.tostring(temp_tree, method='html')

        compressed_expected_output = self._compress_string(expected_output)
        # Add the 'doctype' string (before compressing) as a small fix for
        # the comparison's sake
        compressed_rendered_parsed = self._compress_string(
            '<!DOCTYPE html>'+rendered_and_parsed)

        self.assertEqual(
            compressed_expected_output,
            compressed_rendered_parsed
        )
