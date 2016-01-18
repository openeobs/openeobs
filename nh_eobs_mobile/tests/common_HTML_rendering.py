# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from lxml import etree
from openerp.addons.nh_eobs_mobile.controllers.urls import URLS
from openerp.modules.module import get_module_path
from openerp.tests import common
import jinja2
import os


class MobileHTMLRenderingCase(common.TransactionCase):
    """Parent test case for all the test cases related to the HTML
    rendering by the mobile controller."""

    @classmethod
    def setUpClass(cls):
        """Declare useful variables to be inherited and used by
        the children test cases.
        For instance:
            - the path to the 'fixtures' directory
            - an XML parser set to remove all the white spaces
            while parsing a file
            - a Jinja2 environment to be used for rendering templates
            - a context dictionary to be passed to the Odoo's
            methods requiring it
            - the URLS dictionary used by the mobile controller
            - etc.
        """
        super(MobileHTMLRenderingCase, cls).setUpClass()
        cls.fixtures_directory = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'fixtures')
        cls.no_whitespace_parser = etree.XMLParser(remove_blank_text=True)
        loader = jinja2.FileSystemLoader(
            get_module_path('nh_eobs_mobile') + '/views/')
        cls.jinja_env = jinja2.Environment(loader=loader)
        cls.context = {
            'lang': 'en_GB',
            'tz': 'Europe/London',
            'uid': 1
        }
        cls.controller_urls = URLS

    def _get_fixture_file_path(self, fixture_name):
        """Return the absolute path of a fixture file present in the
        'fixtures' sub-directory.
        :param fixture_name: A string with the name of the fixture file.
        :returns: A string with the absolute path of the
        file passed as argument, or False if such a file doesn't exist.
        """
        fixture_name = str(fixture_name)
        file_path = os.path.join(self.fixtures_directory, fixture_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path
        else:
            return False

    def _render_template(self, cr, uid, template_id=None, options=None):
        """Rely on Odoo's 'view' model to render a specific template with
        a specific context.
        :param template_id: A string with the template's ID
        (as stored in the Odoo's database)
        :param options: A dictionary which will be used to render the template
        (as Odoo's 'qcontext')
        """
        return self.registry('ir.ui.view').render(
            cr, uid,
            template_id,
            options,
            context=self.context)

    def _compress_string(self, string_data):
        """Remove the newline characters and the spaces from a string."""
        return string_data.replace('\n', '').replace(' ', '')
