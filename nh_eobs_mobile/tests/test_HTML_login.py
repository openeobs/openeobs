__author__ = 'lorenzo'
import logging
from lxml import etree
from openerp.addons.nh_eobs_mobile.tests.common_HTML_rendering import MobileHTMLRenderingCase


_logger = logging.getLogger(__name__)


class TestLoginHTML(MobileHTMLRenderingCase):
    """
    Test case collecting all the tests relating to the RENDERING of the 'login' page.
    Compare the actual rendered HTML pages against fixtures (i.e. 'fake' HTML files) specially built.
    """

    def test_login_page_in_a_clean_state(self):
        """
        Test the 'login' page in the 'CLEAN' state:
        i.e. the user has just arrived in the page and the form is still pristine.
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'login_clean.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide them to the template for the rendering
        api_data = {
            'stylesheet': '/mobile/src/css/main.css',
            'logo': '/mobile/src/img/logo.png',
            'form_action': '/mobile/login/',
            'errors': '',
            'databases': ['nhclinical']
        }

        rendered_template = self.jinja_env.get_template('login.html').render(**api_data)
        compressed_rendered_template = self._compress_string(rendered_template)
        compressed_expected_output = self._compress_string(expected_output)
        self.assertEqual(compressed_rendered_template, compressed_expected_output)

    def test_login_page_in_an_invalid_state(self):
        """
        Test the 'login' page in the 'INVALID' state:
        i.e. the user has already submit wrong credentials, now he's been showing a login page with an error message.
        """
        # Retrieve the fixture for this test and parse it,
        # thus there is an expected output to compare the mobile controller's method's result against
        fixture_name = 'login_invalid.html'
        fixture_filepath = self._get_fixture_file_path(fixture_name)
        if fixture_filepath:
            tree = etree.parse(fixture_filepath)
            expected_output = etree.tostring(tree)
        else:
            _logger.warning('IOError: Error reading fixture "{}". Hence, this test has not been actually executed'.format(fixture_name))

        # Set up specific data to provide them to the template for the rendering
        api_data = {
            'stylesheet': '/mobile/src/css/main.css',
            'logo': '/mobile/src/img/logo.png',
            'form_action': '/mobile/login/',
            'errors': '<div class="alert alert-error">Invalid username/password</div>',
            'databases': ['nhclinical']
        }

        rendered_template = self.jinja_env.get_template('login.html').render(**api_data)
        compressed_rendered_template = self._compress_string(rendered_template)
        compressed_expected_output = self._compress_string(expected_output)
        self.assertEqual(compressed_rendered_template, compressed_expected_output)