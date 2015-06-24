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


class TestMobileControllerMethods(tests.common.HttpCase):

    model_observation_types = {
        'height',
        'weight',
        'blood_product',
        'blood_sugar',
        'pain',
        'urine_output',
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

    def _parse_route_arguments(self, route):
        """Parse route arguments according to specific rules.

        :param route: A dictionary with all the necessary route data
        :return: A URL-formatted string with a value for each argument, or None if the route doesn't required any argument
        """
        # Regex and variables for managing the route's arguments
        index_argument_regex = re.compile(r'_id$')
        observation_argument_regex = re.compile(r'^observation$')

        # Use only observation's types present in both the sets
        usable_observation_types = list(self.model_observation_types & self.active_observation_types)

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
        super(TestMobileControllerMethods, self).setUp()
        self.session_resp = requests.post(BASE_URL + 'web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self.fail('Cannot retrieve a valid session to be used for the tests!')

        login_name = self._get_user_belonging_to_group('NH Clinical Nurse Group')
        self.assertNotEqual(login_name, False,
                            "Cannot find any 'nurse' user for authentication before running the test!")
        self.auth_resp = self._get_authenticated_response(login_name)
        self.assertEqual(self.auth_resp.status_code, 200)
        self.assertIn('class="tasklist"', self.auth_resp.content)

    def test_method_take_task_ajax(self):
        take_task_ajax_route = [r for r in routes if r['name'] == 'json_take_task']
        self.assertEqual(len(take_task_ajax_route), 1,
                         "Endpoint to the 'json_take_task' route not unique. Cannot run the test!")

        # Try to retrieve an activity with no user related to it (skip the test if cannot find any)
        activity_registry = self.registry['nh.activity']
        task_id_list = activity_registry.search(self.cr, self.uid, [('user_id', '=', False)], limit=1)
        if len(task_id_list) == 0:
            self.skipTest('Cannot find an activity that has no user related to it. Cannot run the test!')

        task_ajax_url = self._build_url(take_task_ajax_route[0]['endpoint'], task_id_list[0])
        test_resp = requests.post(task_ajax_url, cookies=self.auth_resp.cookies)

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')
        self.assertIn('status', test_resp.content)

    def test_method_get_font(self):
        font_url = self._build_url('src/fonts/{}'.format('non-existing-font'), None, mobile=True)
        test_resp = requests.get(font_url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 404)

    def test_method_take_patient_observation(self):
        take_patient_obs_route = [r for r in routes if r['name'] == 'patient_ob']
        self.assertEqual(len(take_patient_obs_route), 1,
                         "Endpoint to the 'patient_ob' route not unique. Cannot run the test!")

        # Retrieve only observations existing as model, but not as active observations
        non_active_observation_types = list(self.model_observation_types - self.active_observation_types)
        test_observation = random_choice(non_active_observation_types)

        patient_obs_url = self._build_url(take_patient_obs_route[0]['endpoint'], '{}/1'.format(test_observation))
        test_resp = requests.get(patient_obs_url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 404)

    def test_method_calculate_obs_score(self):
        """Pass to the method an observation type which doesn't allow a score calculation."""
        calculate_obs_score_route = [r for r in routes if r['name'] == 'calculate_obs_score']
        self.assertEqual(len(calculate_obs_score_route), 1,
                         "Endpoint to the 'calculate_obs_score' route not unique. Cannot run the test!")

        # Assure that neither 'ews' nor 'gcs' observations are used for the test
        failing_score_observation_types = self.model_observation_types - {'ews', 'gcs'}
        test_observation = random_choice(list(failing_score_observation_types))
        obs_score_url = self._build_url(calculate_obs_score_route[0]['endpoint'], '{}'.format(test_observation))
        test_resp = requests.post(obs_score_url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 400)

    def test_method_mobile_logout(self):
        # Retrieve the 'logout' route and build the complete URL for it
        logout_route = [r for r in routes if r['name'] == 'logout']
        self.assertEqual(len(logout_route), 1,
                         "Endpoint to the 'logout' route not unique. Cannot run the test!")
        logout_url = self._build_url(logout_route[0]['endpoint'], None, mobile=True)

        # Retrieve the 'login' route and build the complete URL for it
        login_route = [r for r in routes if r['name'] == 'login']
        self.assertEqual(len(login_route), 1,
                         "Endpoint to the 'login' route not unique. Cannot run the test!")
        login_url = self._build_url(login_route[0]['endpoint'], None, mobile=True)

        # Actually logout and test the response
        test_resp = requests.get(logout_url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.url, login_url)

    def test_method_get_colleagues(self):
        """Get the colleagues list while being authenticated as a user not belonging to any 'share group'.

        The 'share groups' are defined inside the 'get_colleagues' method, and they are:
            - 'NH Clinical Ward Manager Group'
            - 'NH Clinical Nurse Group'
            - 'NH Clinical HCA Group'
        """
        # Authenticate as a 'doctor' user (that is, a user NOT belonging to any 'share group')
        login_name = self._get_user_belonging_to_group('NH Clinical Doctor Group')
        auth_resp = self._get_authenticated_response(login_name)
        self.assertEqual(self.auth_resp.status_code, 200, "Cannot authenticate as 'doctor' user for running this test!")

        colleagues_list_route = [r for r in routes if r['name'] == 'json_colleagues_list']
        self.assertEqual(len(colleagues_list_route), 1,
                         "Endpoint to the 'json_colleagues_list' route not unique. Cannot run the test!")
        colleagues_list_url = self._build_url(colleagues_list_route[0]['endpoint'], None, mobile=True)

        test_resp = requests.get(colleagues_list_url, cookies=auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)