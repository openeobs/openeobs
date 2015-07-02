__author__ = 'lorenzo'
import json
import logging
import openerp.tests
import requests
from openerp.addons.nh_eobs_api.routing import Route, RouteManager, ResponseJSON
from openerp.addons.nh_eobs_api.controllers.route_api import route_manager
from openerp.tests import DB as DB_NAME
from random import choice as random_choice


test_logger = logging.getLogger(__name__)


class TestOdooRouteDecoratorIntegration(openerp.tests.common.HttpCase):

    json_response_structure_keys = ['status', 'title', 'description', 'data']

    def _get_user_belonging_to_group(self, group_name):
        """Get the 'login' name of a user belonging to a specific group.

        :param group_name: A string with the name of the group from which retrieve a user (belonging to it)
        :return: A string with the 'login' of the user belonging to the group passed as argument (or None if there isn't any user belonging to that group)
        """
        users_pool = self.registry['res.users']
        users_login_list = users_pool.search_read(self.cr, self.uid,
                                                  domain=[('groups_id.name', '=', group_name)],
                                                  fields=['login'])
        login_name = random_choice(users_login_list).get('login')
        return login_name

    def _get_authenticated_response(self, user_name):
        """Get a Response object with an authenticated session within its cookies.

        :param user_name: A string with the username of the user to be authenticated as
        :return: A Response object
        """
        auth_response = requests.post(route_manager.BASE_URL + '/web/login',
                                      {'login': user_name,
                                       'password': user_name,
                                       'database': DB_NAME},
                                      cookies=self.session_resp.cookies)
        return auth_response

    def setUp(self):
        super(TestOdooRouteDecoratorIntegration, self).setUp()
        self.session_resp = requests.post(route_manager.BASE_URL + '/web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self.fail('Cannot retrieve a valid session to be used for the tests!')

        # Authenticate as a 'nurse' user and check the login was successful
        login_name = self._get_user_belonging_to_group('NH Clinical Nurse Group')
        self.assertNotEqual(login_name, False,
                            "Cannot find any 'nurse' user for authentication before running the test!")
        self.auth_resp = self._get_authenticated_response(login_name)
        self.assertEqual(self.auth_resp.status_code, 200)
        #self.assertIn('class="tasklist"', self.auth_resp.content)

    def test_route_json_partial_reasons(self):
        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_partial_reasons')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.get(route_manager.BASE_URL + route_under_test.url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        expected_json = self.registry('nh.clinical.patient.observation.ews')._partial_reasons
        returned_json = json.loads(test_resp.text)

        ## check the returned JSON structure meets the 'standard' one
        for k in self.json_response_structure_keys:
            self.assertIn(k, returned_json)

        self.assertEqual(returned_json['status'], ResponseJSON.STATUS_SUCCESS)
        self.assertEqual(returned_json['title'], 'Reason for partial observation')
        self.assertEqual(returned_json['description'], 'Please select an option from the list')
        self.assertEqual(returned_json['data'], expected_json)

    def test_route_json_colleagues_list(self):
        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_colleagues_list')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.get(route_manager.BASE_URL + route_under_test.url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        expected_json = self.registry('nh.eobs.api').get_share_users(self.cr, self.uid)
        returned_json = json.loads(test_resp.text)

        ## check the returned JSON structure meets the 'standard' one
        for k in self.json_response_structure_keys:
            self.assertIn(k, returned_json)

        self.assertEqual(returned_json['status'], ResponseJSON.STATUS_SUCCESS)
        self.assertEqual(returned_json['title'], 'Colleagues on shift')
        self.assertEqual(returned_json['description'], 'Choose colleagues for stand-in')
        self.assertEqual(returned_json['data'], expected_json)

    def test_route_json_share_patients(self):
        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_share_patients')
        self.assertIsInstance(route_under_test, Route)

        # Try to access the route with a request method not allowed, expecting an error
        test_resp_wrong = requests.get(route_manager.BASE_URL + route_under_test.url,
                                       cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp_wrong.status_code, 405)

        # Access the route with the allowed request method
        test_resp = requests.post(route_manager.BASE_URL + route_under_test.url,
                                  data={'user_ids': [1, 2, 3], 'patient_ids': [4, 5, 6]},
                                  cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        #expected_json = ''
        returned_json = json.loads(test_resp.text)

        ## check the returned JSON structure meets the 'standard' one
        for k in self.json_response_structure_keys:
            self.assertIn(k, returned_json)

        """
        self.assertEqual(returned_json['status'], ResponseJSON.STATUS_SUCCESS)
        self.assertEqual(returned_json['title'], '')
        self.assertEqual(returned_json['description'], '')
        self.assertEqual(returned_json['data'], expected_json)
        """