__author__ = 'lorenzo'
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
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

    # Create a dictionary where the keys are the names of the routes
    # and the values are the routes themselves.
    # Thus, it is easier and faster to get a specific route
    # searching it by its name.
    routes_dictionary = {r['name']: r for r in routes}

    def _build_url(self, route_endpoint, route_arguments='', mobile=True):
        """
        Build a URL from the endpoint and the arguments provided.

        :param route_endpoint: endpoint of a specific route, without arguments
        :type route_endpoint: str
        :param route_arguments: arguments for a specific route's endpoint
        (default to empty string)
        :type route_arguments: str
        :param mobile: select between the 'web' or 'mobile' version of the URL
        (default: ``True``)
        :type mobile: bool
        :returns: full URL, ready to be reached via browser or requests
        :rtype: str
        """
        if mobile:
            base_url = BASE_MOBILE_URL
        else:
            base_url = BASE_URL
        return '{0}{1}{2}'.format(base_url, route_endpoint,
                                  (route_arguments if route_arguments else ''))

    def _get_authenticated_response(self, user_name):
        """
        Get a Response object with an authenticated session within its cookies.

        :param user_name: username of the user to be authenticated as
        :type user_name: str
        :returns: a Response object
        :rtype: :class:`http.Response<openerp.http.Response>`
        """
        auth_response = requests.post(BASE_MOBILE_URL + 'login',
                                      {'username': user_name,
                                       'password': user_name,
                                       'database': DB_NAME},
                                      cookies=self.session_resp.cookies)
        self.assertEqual(auth_response.status_code, 200,
                         "Cannot retrieve an authenticated session as user "
                         "'{}' to be used for the test.".format(user_name))
        return auth_response

    def _get_user_belonging_to_group(self, group_name):
        """
        Get the 'login' name of a user belonging to a specific group.

        :param group_name: name of the group from which retrieve a user
        :type group_name: str
        :returns: 'login' of the user belonging to the group passed as argument
        (or None if there isn't any user belonging to that group)
        :rtype: str
        """
        users_pool = self.registry['res.users']
        users_login_list = users_pool.search_read(self.cr, self.uid,
                                                  domain=[('groups_id.name', '=', group_name)],
                                                  fields=['login'])
        login_name = random_choice(users_login_list).get('login')
        return login_name

    @staticmethod
    def _reach_endpoint(url_to_reach, method, cookies):
        if method.upper() == 'GET':
            resp = requests.get(url_to_reach, cookies=cookies)
        elif method.upper() == 'POST':
            resp = requests.post(url_to_reach, cookies=cookies)
        return resp

    def _check_response_status(self, response, redirection_expected=False):
        """
        Check the response's status through assertions.

        :param response: a Response object
        :type response: :class:`http.Response<openerp.http.Response>`
        :param redirection_expected: whether a redirection is expected
        to be found in the response's history
        :type redirection_expected: bool
        """
        if redirection_expected:
            self.assertEqual(len(response.history), 1)
            self.assertEqual(response.history[0].status_code, 302)
            self.assertIn('web/login?redirect=', response.url)
        else:
            self.assertEqual(len(response.history), 0)
            self.assertEqual(response.status_code, 200)

    def setUp(self):
        super(TestMobileControllerRouting, self).setUp()
        self.session_resp = requests.post(BASE_URL + 'web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self.fail('Cannot retrieve a valid session to be used for the tests!')

    def test_login_endpoint_is_reachable_as_not_authenticated_user(self):
        login_route = self.routes_dictionary['login']
        url_to_reach = self._build_url(login_route['endpoint'])
        test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                         cookies=self.session_resp.cookies)
        self._check_response_status(test_resp, redirection_expected=False)

    def test_patient_list_endpoint_is_not_reachable_as_not_authenticated_user(self):
        patient_list_route = self.routes_dictionary['patient_list']
        url_to_reach = self._build_url(patient_list_route['endpoint'])
        test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                         cookies=self.session_resp.cookies)
        self._check_response_status(test_resp, redirection_expected=True)

    def test_patient_list_endpoint_is_reachable_as_authenticated_user(self):
        patient_list_route = self.routes_dictionary['patient_list']
        url_to_reach = self._build_url(patient_list_route['endpoint'])
        users_to_test = []
        group_list = [
            'NH Clinical HCA Group',
            'NH Clinical Nurse Group',
            'NH Clinical Ward Manager Group'
        ]
        for group_name in group_list:
            login_name = self._get_user_belonging_to_group(group_name)
            users_to_test.append(login_name)
        self.assertGreater(len(users_to_test), 0,
                           'Cannot find any user (belonging to any of the '
                           'groups given) for authentication to run the test.')
        for u in users_to_test:
            auth_resp = self._get_authenticated_response(u)
            test_logger.debug("Authenticated as user '{}'".format(u))
            test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                             cookies=auth_resp.cookies)
            self._check_response_status(test_resp, redirection_expected=False)

    def test_task_list_endpoint_is_not_reachable_as_not_authenticated_user(self):
        task_list_route = self.routes_dictionary['task_list']
        url_to_reach = self._build_url(task_list_route['endpoint'])
        test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                         cookies=self.session_resp.cookies)
        self._check_response_status(test_resp, redirection_expected=True)

    def test_task_list_endpoint_is_reachable_as_authenticated_user(self):
        task_list_route = self.routes_dictionary['task_list']
        url_to_reach = self._build_url(task_list_route['endpoint'])
        users_to_test = []
        group_list = [
            'NH Clinical HCA Group',
            'NH Clinical Nurse Group',
            'NH Clinical Ward Manager Group'
        ]
        for group_name in group_list:
            login_name = self._get_user_belonging_to_group(group_name)
            users_to_test.append(login_name)
        self.assertGreater(len(users_to_test), 0,
                           'Cannot find any user (belonging to any of the '
                           'groups given) for authentication to run the test.')
        for u in users_to_test:
            auth_resp = self._get_authenticated_response(u)
            test_logger.debug("Authenticated as user '{}'".format(u))
            test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                             cookies=auth_resp.cookies)
            self._check_response_status(test_resp, redirection_expected=False)

    def test_share_patient_list_endpoint_is_not_reachable_as_not_authenticated_user(self):
        share_patients_route = self.routes_dictionary['share_patient_list']
        url_to_reach = self._build_url(share_patients_route['endpoint'])
        test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                         cookies=self.session_resp.cookies)
        self._check_response_status(test_resp, redirection_expected=True)

    def test_share_patient_list_endpoint_is_reachable_as_authenticated_user(self):
        share_patients_route = self.routes_dictionary['share_patient_list']
        url_to_reach = self._build_url(share_patients_route['endpoint'])
        users_to_test = []
        group_list = [
            'NH Clinical HCA Group',
            'NH Clinical Nurse Group',
            'NH Clinical Ward Manager Group'
        ]
        for group_name in group_list:
            login_name = self._get_user_belonging_to_group(group_name)
            users_to_test.append(login_name)
        self.assertGreater(len(users_to_test), 0,
                           'Cannot find any user (belonging to any of the '
                           'groups given) for authentication to run the test.')
        for u in users_to_test:
            auth_resp = self._get_authenticated_response(u)
            test_logger.debug("Authenticated as user '{}'".format(u))
            test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                             cookies=auth_resp.cookies)
            self._check_response_status(test_resp, redirection_expected=False)

    def test_single_patient_endpoint_is_not_reachable_as_not_authenticated_user(self):
        single_patient_route = self.routes_dictionary['single_patient']
        url_to_reach = self._build_url(single_patient_route['endpoint'], '1')
        test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                         cookies=self.session_resp.cookies)
        self._check_response_status(test_resp, redirection_expected=True)

    def test_single_task_endpoint_is_not_reachable_as_not_authenticated_user(self):
        single_task_route = self.routes_dictionary['single_task']
        url_to_reach = self._build_url(single_task_route['endpoint'], '1')
        test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                         cookies=self.session_resp.cookies)
        self._check_response_status(test_resp, redirection_expected=True)

    def test_task_form_action_endpoint_is_not_reachable_as_not_authenticated_user(self):
        task_form_action_route = self.routes_dictionary['task_form_action']
        url_to_reach = self._build_url(task_form_action_route['endpoint'], '1')
        test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                         cookies=self.session_resp.cookies)
        self._check_response_status(test_resp, redirection_expected=True)

    def test_patient_ob_endpoint_is_not_reachable_as_not_authenticated_user(self):
        patient_ob_route = self.routes_dictionary['patient_ob']
        url_to_reach = self._build_url(patient_ob_route['endpoint'],
                                       'ews/1')
        test_resp = self._reach_endpoint(url_to_reach, 'GET',
                                         cookies=self.session_resp.cookies)
        self._check_response_status(test_resp, redirection_expected=True)
