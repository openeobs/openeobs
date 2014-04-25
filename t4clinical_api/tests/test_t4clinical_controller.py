from openerp.tests import common

import openerp.addons.web.http as http
from mock import Mock, patch
import openerp.addons.t4clinical_api.controllers.t4clinical_controller as t4clinical_controller


class TestT4clinicalController(common.SingleTransactionCase):

    @patch('openerp.addons.web.http.Controller')
    def setUp(self, httpController):
        global host
        self.t4controller = t4clinical_controller.T4clinicalController(httpController)

        host = 'http://localhost:8069'
        super(TestT4clinicalController, self).setUp()

    @patch('openerp.addons.web.http.httprequest')
    def test_activities_urls_test_one(self, req):
        global host
        req.httprequest.path = '/api/activities/'
        req.httprequest.method = 'GET'

        self.t4controller.activities(req)

    @patch('openerp.addons.web.http.httprequest')
    def test_activities_urls_test_two(self, req):
        global host
        req.httprequest.path = '/api/activities/10/assign'
        req.httprequest.method = 'GET'

        self.t4controller.activities(req)
