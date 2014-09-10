__author__ = 'colin'

import openerp.tests
import helpers

class TestAjaxTakeCancel(openerp.tests.HttpCase):

    def setUp(self):
        super(TestAjaxTakeCancel, self).setUp()

        # set up database connection objects
        self.registry = openerp.modules.registry.RegistryManager.get('t4clinical_test')
        self.uid = 1
        self.host = 'http://localhost:8169'

        self.demo_api = self.registry.get('t4.clinical.api.demo')


    # test task taking and cancel taking via ajax
    def test_ajax_take_cancel(self):
