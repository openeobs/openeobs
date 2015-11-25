__author__ = 'lorenzo'

import logging
import re
import requests
from random import choice as random_choice

from openerp import tests
from openerp.addons.nh_eobs_mobile.controllers.urls import routes
from openerp.tests import DB as DB_NAME
from openerp.tools import config


SERVER_PROTOCOL = "http"
SERVER_ADDRESS = "localhost"
SERVER_PORT = "{0}".format(config['xmlrpc_port'])
MOBILE_URL_PREFIX = 'mobile/'
BASE_URL = SERVER_PROTOCOL + '://' + SERVER_ADDRESS + ':' + SERVER_PORT + '/'
BASE_MOBILE_URL = BASE_URL + MOBILE_URL_PREFIX

test_logger = logging.getLogger(__name__)


class TestMobileControllerRouting(tests.common.HttpCase):

    def _parse_route_arguments(self, route):
        """Parse route arguments according to specific rules.

        :param route: A dictionary with all the necessary route data
        :return: A URL-formatted string with a value for each argument, or None if the route doesn't required any argument
        """
        # Regex and variables for managing the route's arguments
        index_argument_regex = re.compile(r'_id$')
        observation_argument_regex = re.compile(r'^observation$')
        model_observation_types = {
            'height',
            'weight',
            'blood_product',
            'blood_sugar',
            'pain',
            'urine_output',
            'uotarget',
            'bowels_open',
        }
        active_observation_types = {
            'height',
            'weight',
            'blood_product',
            'blood_sugar',
            'ews',
            'stools',
            'gcs',
            'pbp',
        }
        # Use only observation's types present in both the sets
        usable_observation_types = list(model_observation_types & active_observation_types)

        # Parse the route's arguments
        route_arguments = None
        if route['args']:
            argument_list = []
            for arg in route['args']:
                if observation_argument_regex.search(arg):
                    argument_list.append(random_choice(usable_observation_types))
                elif index_argument_regex.search(arg):
                    argument_list.append('1')
            if len(argument_list) == 1:
                route_arguments = argument_list[0]
            elif len(argument_list) > 1:
                route_arguments = '/'.join(argument_list)
        return route_arguments

    def _build_url(self, route_endpoint, route_arguments, mobile=True):
        """Build a URL from the endpoint and the arguments provided.

        :param route_endpoint: A string with the endpoint of a specific route, without arguments
        :param route_arguments: A string with the arguments for a specific route's endpoint
        :param mobile: A boolean to select between the 'web' or 'mobile' version of the URL (default: True)
        :return: A string with a full URL, ready to be reached via browser or requests
        """
        if mobile:
            base_url = BASE_MOBILE_URL
        else:
            base_url = BASE_URL
        return '{0}{1}{2}'.format(base_url, route_endpoint, (route_arguments if route_arguments else ''))

    def _get_authenticated_response(self, user_name):
        """Get a Response object with an authenticated session within its cookies.

        :param user_name: A string with the username of the user to be authenticated as
        :return: A Response object
        """
        auth_response = requests.post(BASE_MOBILE_URL + 'login',
                                      {'username': user_name,
                                       'password': user_name,
                                       'database': DB_NAME},
                                      cookies=self.session_resp.cookies)
        return auth_response

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

    def setUp(self):
        super(TestMobileControllerRouting, self).setUp()
        self.session_resp = requests.post(BASE_URL + 'web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self.fail('Cannot retrieve a valid session to be used for the tests!')

        # Routes to skip (a specific case for each of them has to be evaluated)
        self.route_to_skip = [
            'task_form_action',
            'json_task_form_action',
            'patient_form_action',
            'json_patient_form_action',
            'calculate_obs_score',
            'json_take_task',
            'confirm_clinical_notification',
            'cancel_clinical_notification',
            'json_share_patients',
            'json_claim_patients',
            'json_accept_patients',
            'json_reject_patients',
            'confirm_review_frequency',
            'confirm_bed_placement',
            'json_patient_barcode',
            'json_patient_info',
            'js_routes',
            'json_cancel_take_task',
            'json_colleagues_list',
            'json_partial_reasons',
            'ajax_task_cancellation_options',
            'ajax_get_patient_obs',
            'json_invite_patients'
        ]

    def test_reaching_routes_as_authenticated_user(self):  # TODO: split this in one separated method for each role (?)
        users_to_test = {}
        group_list = [
            'NH Clinical HCA Group',
            'NH Clinical Nurse Group',
            'NH Clinical Ward Manager Group'
        ]
        for group_name in group_list:
            login_name = self._get_user_belonging_to_group(group_name)
            users_to_test[login_name] = login_name

        self.assertGreater(len(users_to_test), 0,
                           'Cannot find any user (belonging to any of the groups given) for running the test!')

        route_to_skip = self.route_to_skip + ['logout']

        for u in users_to_test:
            auth_resp = self._get_authenticated_response(u)

            # Check if the login was successful (we should have been redirected to the task list page)
            self.assertEqual(auth_resp.status_code, 200)
            self.assertIn('class="tasklist"', auth_resp.content)

            for route in routes:
                if route['name'] in route_to_skip:
                    continue

                route_arguments = self._parse_route_arguments(route)
                url_to_reach = self._build_url(route['endpoint'], route_arguments)

                # Access the route as an authenticated user
                if route['method'] == 'GET':
                    test_resp = requests.get(url_to_reach, cookies=auth_resp.cookies)
                elif route['method'] == 'POST':
                    test_resp = requests.post(url_to_reach, cookies=auth_resp.cookies)

                self.assertEqual(test_resp.status_code, 200)

    def test_reaching_routes_as_not_authenticated_user(self):
        static_routes_regex = re.compile(r'^src\/')
        route_to_skip = self.route_to_skip

        for route in routes:
            if route['name'] in route_to_skip:
                continue

            route_arguments = self._parse_route_arguments(route)
            url_to_reach = self._build_url(route['endpoint'], route_arguments)

            # Try to access the route as an unauthenticated user, expecting a redirection to the login page
            if route['method'] == 'GET':
                test_resp = requests.get(url_to_reach, cookies=self.session_resp.cookies)
            elif route['method'] == 'POST':
                test_resp = requests.post(url_to_reach, cookies=self.session_resp.cookies)

            if static_routes_regex.search(route['endpoint']) or route['name'] == 'login':
                self.assertEqual(len(test_resp.history), 0)
                self.assertEqual(test_resp.status_code, 200)
            else:
                self.assertEqual(len(test_resp.history), 1)
                self.assertEqual(test_resp.history[0].status_code, 302)
                self.assertIn('web/login?redirect=', test_resp.url)

    def test_response_has_correct_content_type(self):
        # Regex and variables for managing the routes' names and endpoints
        json_routes_regex = re.compile(r'^json_')
        static_routes_regex = re.compile(r'^src\/')
        static_content_types = {
            'png': 'image/png',
            'js': 'text/javascript',
            'css': 'text/css',
            'json': 'application/json'
        }
        route_to_skip = self.route_to_skip + ['logout']

        auth_resp = self._get_authenticated_response('nadine')
        # Check if the login was successful (we should have been redirected to the task list page)
        self.assertEqual(auth_resp.status_code, 200)
        self.assertIn('class="tasklist"', auth_resp.content)

        for route in routes:
            # Parse the route's name, endpoint and arguments
            if route['name'] in route_to_skip:
                continue
            if json_routes_regex.search(route['name']):
                expected_content_type = 'application/json'
            elif static_routes_regex.search(route['endpoint']):
                ext = route['endpoint'].split('.')[-1]
                if ext in static_content_types:
                    expected_content_type = static_content_types.get(ext, None)
            else:
                expected_content_type = None

            route_arguments = self._parse_route_arguments(route)

            # Test the route's response's content type
            url_to_reach = self._build_url(route['endpoint'], route_arguments)
            if route['method'] == 'GET':
                test_resp = requests.get(url_to_reach, cookies=auth_resp.cookies)
            elif route['method'] == 'POST':
                test_resp = requests.post(url_to_reach, cookies=auth_resp.cookies)
            self.assertEqual(test_resp.status_code, 200)
            if expected_content_type:
                self.assertIn(expected_content_type, test_resp.headers['content-type'])

        # Add an extra custom case only for the fonts directory
        url_to_reach = self._build_url('src/fonts/fontawesome-webfont.eot?v=4.0.3', None)
        test_resp = requests.get(url_to_reach, cookies=self.session_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('application/font-woff', test_resp.headers['content-type'])