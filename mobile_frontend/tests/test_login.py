__author__ = 'colin'

import openerp.tests

class TestLogin(openerp.tests.HttpCase):

    def test_mobile_redirect_not_logged_in(self):
        self.phantom_js('/mobile', 'if(document.location.href === "http://localhost:8169/mobile/login/"){ console.log("ok") }else{ console.log("error") }', 'document')
    def test_mobile_redirect_logged_in(self):
        self.phantom_js('/mobile', 'if(document.location.href === "http://localhost:8169/mobile/tasks/"){ console.log("ok") }else{ console.log("error") }', 'document', login='admin')
    def test_mobile_redirect_invalid_login(self):
        self.phantom_js('/mobile', 'if(document.location.href === "http://localhost:8169/mobile/login/"){ console.log("ok") }else{ console.log("error") }', 'document', login='meh')