__author__ = 'colin'
from openerp.tools import config 
import openerp.tests
import helpers


class TestLogin(openerp.tests.HttpCase):
    def setUp(self):
        super(TestLogin, self).setUp()
        self.host = "http://localhost:%s" % config['xmlrpc_port']
        js_code_template = 'if(document.location.href === "%s%%s"){ console.log("ok") }else{ console.log("error") }' % self.host
        self.js_login = js_code_template % helpers.URLS['login']
        self.js_task_list = js_code_template % helpers.URLS['task_list']

    def test_mobile_redirect_not_logged_in(self):
        print self.js_login
        self.phantom_js(helpers.URL_PREFIX, self.js_login, 'document')

    def test_mobile_redirect_logged_in(self):
        self.phantom_js(helpers.URL_PREFIX, self.js_task_list, 'document', login='admin')

    def test_mobile_redirect_invalid_login(self):
        self.phantom_js(helpers.URL_PREFIX, self.js_login, 'document', login='meh')