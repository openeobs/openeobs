from openerp.tests import common
from mock import Mock, patch
import openerp.addons.t4clinical_api.controllers.t4clinical_controller as t4clinical_controller


class TestT4clinicalController(common.SingleTransactionCase):

    @patch('openerp.addons.web.http.Controller')
    def setUp(self, httpController):
        global host, cr, uid, activity_pool
        cr = self.cr
        uid = self.uid

        activity_pool = self.registry('t4.activity')
        self.t4controller = t4clinical_controller.T4clinicalController(httpController)

        host = 'http://localhost:8069'
        super(TestT4clinicalController, self).setUp()

    @patch('openerp.addons.web.http.httprequest')
    def test_activities_urls(self, req):
        with patch('openerp.addons.web.session') as session:
            global host, cr, uid, activity_pool

            activity_id = activity_pool.search(cr, uid, [])[0]
            session._db = 't4clinical_default_config'
            session._uid = uid
            req.httprequest.session = {'0': session}

            req.httprequest.path = '/api/activities/'
            req.httprequest.method = 'GET'
            print "TEST - API activity URLS - " + req.httprequest.path + " " + req.httprequest.method + " getActivities"
            self.t4controller.activities(req)

            req.httprequest.path += str(activity_id)
            print "TEST - API activity URLS - " + req.httprequest.path + " " + req.httprequest.method + " getActivity"
            self.t4controller.activities(req)

            req.httprequest.method = 'POST'
            print "TEST - API activity URLS - " + req.httprequest.path + " " + req.httprequest.method + " submit"
            self.t4controller.activities(req)

            req.httprequest.method = 'DELETE'
            print "TEST - API activity URLS - " + req.httprequest.path + " " + req.httprequest.method + " cancel"
            self.t4controller.activities(req)

            req.httprequest.path += '/assign'
            req.httprequest.method = 'POST'
            print "TEST - API activity URLS - " + req.httprequest.path + " " + req.httprequest.method + " assign"
            self.t4controller.activities(req)

            req.httprequest.method = 'DELETE'
            print "TEST - API activity URLS - " + req.httprequest.path + " " + req.httprequest.method + " unassign"
            self.t4controller.activities(req)

            req.httprequest.path = req.httprequest.path[:-7] + '/complete'
            req.httprequest.method = 'POST'
            print "TEST - API activity URLS - " + req.httprequest.path + " " + req.httprequest.method + " complete"
            self.t4controller.activities(req)

    # @patch('openerp.addons.web.http.httprequest')
    # def test_activities_urls_test_one(self, req):
    #     with patch('openerp.addons.web.session') as session:
    #         global host
    #         session._db = 't4clinical_default_config'
    #         session._uid = 1
    #         req.httprequest.path = '/api/activities/'
    #         req.httprequest.method = 'GET'
    #         req.httprequest.session = {'0': session}
    #
    #         self.t4controller.activities(req)

    # @patch('openerp.addons.web.http.httprequest')
    # def test_activities_urls_test_two(self, req):
    #     global host
    #     req.httprequest.path = '/api/activities/10/assign'
    #     req.httprequest.method = 'GET'
    #
    #     self.t4controller.activities(req)
