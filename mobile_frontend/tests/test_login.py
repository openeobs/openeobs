__author__ = 'colin'

import openerp.tests
import helpers

class TestLogin(openerp.tests.HttpCase):

    # I would use ''.format on these strings instead but for some reason the work console makes format throw a wobbly

    def test_mobile_redirect_not_logged_in(self):
        self.phantom_js(helpers.URL_PREFIX, 'if(document.location.href === "http://localhost:8169%s"){ console.log("ok") }else{ console.log("error") }' %(helpers.URLS['login']), 'document')
    def test_mobile_redirect_logged_in(self):
        self.phantom_js(helpers.URL_PREFIX, 'if(document.location.href === "http://localhost:8169%s"){ console.log("ok") }else{ console.log("error") }' %(helpers.URLS['task_list']), 'document', login='admin')
    def test_mobile_redirect_invalid_login(self):
        self.phantom_js(helpers.URL_PREFIX, 'if(document.location.href === "http://localhost:8169%s"){ console.log("ok") }else{ console.log("error") }' %(helpers.URLS['login']), 'document', login='meh')