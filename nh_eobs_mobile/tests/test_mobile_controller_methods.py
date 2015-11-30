__author__ = 'lorenzo'
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import logging
import mock
import re
import requests
from random import choice as random_choice

from openerp import tests
from openerp.addons.nh_eobs_mobile.controllers.urls import routes, URLS
from openerp.http import HttpRequest
from openerp.osv.orm import except_orm
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

        :param route: all the necessary route data
        :type route: dict
        :returns: a URL-formatted string with a value for each argument, or None if the route doesn't required any argument
        :rtype: str
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

        :param route_endpoint: endpoint of a specific route, without arguments
        :type route_endpoint: str
        :param route_arguments: arguments for a specific route's endpoint
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
        return '{0}{1}{2}'.format(base_url, route_endpoint, (route_arguments if route_arguments else ''))

    def _get_authenticated_response(self, user_name):
        """Get a Response object with an authenticated session within its cookies.

        :param user_name: username of the user to be authenticated as
        :type user_name: str
        :returns: a Response object
        """
        auth_response = requests.post(BASE_MOBILE_URL + 'login',
                                      {'username': user_name,
                                       'password': user_name,
                                       'database': DB_NAME},
                                      cookies=self.session_resp.cookies)
        return auth_response

    def _get_user_belonging_to_group(self, group_name):
        """Get the 'id' and the 'login' name of a user belonging to a specific group.

        :param group_name: name of the group from which retrieving a user (belonging to it)
        :type group_name: str
        :returns: a dictionary with 2 key-value couples:
            - 'login': the login name of the retrieved user (belonging to the group passed as argument)
            - 'id': the id of the retrieved user (belonging to the group passed as argument)
        :rtype: dict
        :returns: None if there isn't any user belonging to that group
        """
        users_pool = self.registry['res.users']
        users_login_list = users_pool.search_read(self.cr, self.uid,
                                                  domain=[('groups_id.name', '=', group_name)],
                                                  fields=['login', 'id'])
        try:
            user_data = random_choice(users_login_list)
        except IndexError:
            user_data = None
        return user_data

    def _bulk_patch_odoo_model_method(self, odoo_model, methods_patching):
        """Patch a list of methods related to an Odoo's model.

        :param odoo_model: a valid Odoo's model instance (e.g. fetched by 'self.registry()')
        :param methods_patching: list of two-values tuples, each containing:
            - the method to be patched (string)
            - the function that will substitute the method to be patched (the actual name of the function)
        :type methods_patching: list
        :return: True (if no errors were raised during the patching)
        :rtype: bool
        """
        for method_to_patch, substituting_function in methods_patching:
            odoo_model._patch_method(method_to_patch, substituting_function)
        return True

    def _revert_bulk_patch_odoo_model_method(self, odoo_model, methods_to_be_reverted):
        """Revert the Odoo's patching of a list of methods.

        :param odoo_model: A valid Odoo's model instance (e.g. fetched by 'self.registry()')
        :param methods_to_be_reverted: list of model's 'original' methods to be reactivated back (string)
        :type methods_to_be_reverted: list
        :return: True (if no errors were raised during the patching)
        :rtype: bool
        """
        for m in methods_to_be_reverted:
            odoo_model._revert_method(m)
        return True

    def setUp(self):
        super(TestMobileControllerMethods, self).setUp()
        self.session_resp = requests.post(BASE_URL + 'web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self.fail('Cannot retrieve a valid session to be used for the tests!')

        user_data = self._get_user_belonging_to_group('NH Clinical Nurse Group')
        self.login_name = user_data.get('login')
        self.user_id = user_data.get('id')
        self.assertNotEqual(self.login_name, False,
                            "Cannot find any 'nurse' user for authentication before running the test!")
        self.auth_resp = self._get_authenticated_response(self.login_name)
        self.assertEqual(self.auth_resp.status_code, 200)
        self.assertIn('class="tasklist"', self.auth_resp.content)

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

    def test_method_take_patient_observation_returns_404_when_list_of_related_patients_is_empty(self):
        """
        Test that the method returns a '404 Not Found' response,
        if the list of patients (internally fetched) is empty.
        (e.g. this could happen when a user tries
        to submit an observation for a non-existing patient,
        by manually inputting a wrong patient ID in the URL).
        In such a case, searching a patient will return an empty list.
        """
        def mock_get_assigned_activities(*args, **kwargs):
            fake_activities_list = [
                'this',
                'will',
                'not',
                'be',
                'used',
                'at',
                'all'
            ]
            return fake_activities_list

        def mock_get_patients(*args, **kwargs):
            empty_list = []
            return empty_list

        take_patient_obs_route = [r for r in routes if r['name'] == 'patient_ob']
        self.assertEqual(len(take_patient_obs_route), 1,
                         "Endpoint to the 'patient_ob' route not unique. Cannot run the test!")

        # Retrieve only observations existing as model, but not as active observations
        test_observation = random_choice(list(self.active_observation_types))

        patient_obs_url = self._build_url(take_patient_obs_route[0]['endpoint'], '{}/1'.format(test_observation))

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', mock_get_assigned_activities),
            ('get_patients', mock_get_patients)
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Actually reach the 'single task' page
        try:
            test_resp = requests.get(patient_obs_url, cookies=self.auth_resp.cookies)
        finally:
            # Just the first element of every tuple is needed for reverting the patchers
            methods_to_revert = [m[0] for m in methods_patching_list]

            # Stop Odoo's patchers
            self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        self.assertEqual(test_resp.status_code, 404)

    def test_method_mobile_logout_redirects_to_login_page(self):
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

    def test_method_get_patients_list(self):
        get_patients_route = [r for r in routes if r['name'] == 'patient_list']
        self.assertEqual(len(get_patients_route), 1,
                         "Endpoint to the 'patient_list' route not unique. Cannot run the test!")
        get_patients_url = self._build_url(get_patients_route[0]['endpoint'], None, mobile=True)

        # Odoo-patch models' methods to make them returning test data
        def mock_unassign_my_activities(*args, **kwargs):
            return True

        def mock_get_assigned_activities(*args, **kwargs):
            """Return a list of dictionaries (one for each assigned activity)."""
            assigned_activities_list = [
                {
                    'id': 1,
                    'user': 'Nurse Nadine',
                    'count': 2,
                    'patient_ids': [47, 49],
                    'message': 'You have been invited to follow 2 patients from Nurse Nadine'
                }
            ]
            return assigned_activities_list

        def mock_get_patients(*args, **kwargs):
            """Return a list of dictionaries (one for each patient)."""
            patients_list = [
                {
                    'clinical_risk': 'None',
                    'dob': '1980-12-25 08:00:00',
                    'ews_score': '0',
                    'ews_trend': 'down',
                    'frequency': 720,
                    'full_name': 'Campbell, Bruce',
                    'gender': 'M',
                    'id': 2,
                    'location': 'Bed 3',
                    'next_ews_time': 'overdue: 12:00 hours',
                    'other_identifier': '1234567',
                    'parent_location': 'Ward E',
                    'patient_identifier': '908 475 1234',
                    'sex': 'M'
                }
            ]
            return patients_list

        def mock_get_patient_followers(*args, **kwargs):
            for p in args[3]:
                p['followers'] = [
                    {
                        'id': 3,
                        'name': 'Nurse Nathaniel'
                    }
                ]
            return True

        def mock_get_followed_patients(*args, **kwargs):
            """Return a list of dictionaries (one for each patient 'followed' by the user)."""
            followed_patients_list = []
            return followed_patients_list

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('unassign_my_activities', mock_unassign_my_activities),
            ('get_assigned_activities', mock_get_assigned_activities),
            ('get_patients', mock_get_patients),
            ('get_patient_followers', mock_get_patient_followers),
            ('get_followed_patients', mock_get_followed_patients),
        ]

        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Setup and use a mocked version of the render() method
        def mock_httprequest_render(*args, **kwargs):
            test_logger.debug('Mock of HttpRequest.render() method called during the test.')

        with mock.patch.object(HttpRequest, 'render', side_effect=mock_httprequest_render) as mocked_method:
            test_resp = requests.get(get_patients_url, cookies=self.auth_resp.cookies)

        # Just the first element of every tuple is needed for reverting the patchers
        methods_to_revert = [m[0] for m in methods_patching_list]

        # Stop Odoo's patchers
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        # Test the render() method was called with the rightly processed arguments
        mocked_method.assert_called_once_with(
            'nh_eobs_mobile.patient_task_list',
            qcontext={
                'notifications': [
                    {
                        'id': 1,
                        'user': 'Nurse Nadine',
                        'count': 2,
                        'patient_ids': [47, 49],
                        'message': 'You have been invited to follow 2 patients from Nurse Nadine'
                    }
                ],
                'items': [
                    {
                        'clinical_risk': 'None',
                        'dob': '1980-12-25 08:00:00',
                        'ews_score': '0',
                        'ews_trend': 'down',
                        'frequency': 720,
                        'full_name': 'Campbell, Bruce',
                        'gender': 'M',
                        'id': 2,
                        'location': 'Bed 3',
                        'next_ews_time': 'overdue: 12:00 hours',
                        'other_identifier': '1234567',
                        'parent_location': 'Ward E',
                        'patient_identifier': '908 475 1234',
                        'sex': 'M',
                        # Keys added by the controller's method under test
                        'url': '/mobile/patient/2',
                        'color': 'level-none',
                        'deadline_time': 'overdue: 12:00 hours',
                        'summary': False,

                        'followers': [
                            {
                                'id': 3,
                                'name': 'Nurse Nathaniel'
                            }
                        ]
                    }
                ],
                'notification_count': 1,
                'followed_items': [],
                'section': 'patient',
                'username': self.login_name,
                'urls': URLS
            }
        )

    def test_method_get_tasks_list(self):
        get_tasks_route = [r for r in routes if r['name'] == 'task_list']
        self.assertEqual(len(get_tasks_route), 1,
                         "Endpoint to the 'task_list' route not unique. Cannot run the test!")
        get_tasks_url = self._build_url(get_tasks_route[0]['endpoint'], None, mobile=True)

        # Odoo-patch models' methods to make them returning test data
        def mock_unassign_my_activities(*args, **kwargs):
            return True

        def mock_get_assigned_activities(*args, **kwargs):
            """Return a list of dictionaries (one for each assigned activity)."""
            assigned_activities_list = [
                {
                    'id': 1,
                    'user': 'Nurse Nadine',
                    'count': 2,
                    'patient_ids': [47, 49],
                    'message': 'You have been invited to follow 2 patients from Nurse Nadine'
                }
            ]
            return assigned_activities_list

        def mock_get_activities(*args, **kwargs):
            """Return a list of dictionaries (one for each activity)."""
            activities_list = [
                {
                    'clinical_risk': 'None',
                    'deadline': '2015-03-29 08:00:00',
                    'deadline_time': 'overdue: 04:14 hours',
                    'ews_score': '0',
                    'ews_trend': 'same',
                    'full_name': 'Campbell, Naomi',
                    'id': 1890,
                    'location': 'Bed 3',
                    'notification': False,
                    'patient_id': 9,
                    'parent_location': 'Ward E',
                    'summary': 'Assess Patient'
                }
            ]
            return activities_list

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('unassign_my_activities', mock_unassign_my_activities),
            ('get_assigned_activities', mock_get_assigned_activities),
            ('get_activities', mock_get_activities),
        ]

        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Setup and use a mocked version of the render() method
        def mock_httprequest_render(*args, **kwargs):
            test_logger.debug('Mock of HttpRequest.render() method called during the test.')

        with mock.patch.object(HttpRequest, 'render', side_effect=mock_httprequest_render) as mocked_method:
            test_resp = requests.get(get_tasks_url, cookies=self.auth_resp.cookies)

        # Just the first element of every tuple is needed for reverting the patchers
        methods_to_revert = [m[0] for m in methods_patching_list]

        # Stop Odoo's patchers
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        # Test the render() method was called with the rightly processed arguments
        mocked_method.assert_called_once_with(
            'nh_eobs_mobile.patient_task_list',
            qcontext={
                'items': [
                    {
                        'clinical_risk': 'None',
                        'deadline': '2015-03-29 08:00:00',
                        'deadline_time': 'overdue: 04:14 hours',
                        'ews_score': '0',
                        'ews_trend': 'same',
                        'full_name': 'Campbell, Naomi',
                        'id': 1890,
                        'location': 'Bed 3',
                        'notification': False,
                        'patient_id': 9,
                        'parent_location': 'Ward E',
                        'summary': 'Assess Patient',
                        # Keys added by the controller's method under test
                        'url': '/mobile/task/1890',
                        'color': 'level-none',
                    }
                ],
                'section': 'task',
                'username': self.login_name,
                'notification_count': 1,
                'urls': URLS
            }
        )

    def test_method_get_single_patient_data(self):
        get_patient_route = [r for r in routes if r['name'] == 'single_patient']
        self.assertEqual(len(get_patient_route), 1,
                         "Endpoint to the 'single_patient' route not unique. Cannot run the test!")
        get_patient_url = self._build_url(get_patient_route[0]['endpoint'], '2', mobile=True)

        # Odoo-patch models' methods to make them returning test data
        def mock_get_assigned_activities(*args, **kwargs):
            """Return a list of dictionaries (one for each assigned activity)."""
            assigned_activities_list = [
                {
                    'id': 1,
                    'user': 'Nurse Nadine',
                    'count': 2,
                    'patient_ids': [47, 49],
                    'message': 'You have been invited to follow 2 patients from Nurse Nadine'
                }
            ]
            return assigned_activities_list

        def mock_get_patients(*args, **kwargs):
            """Return a list of dictionaries (one for each patient)."""
            patients_list = [
                {
                    'clinical_risk': 'None',
                    'dob': '1980-12-25 08:00:00',
                    'ews_score': '0',
                    'ews_trend': 'down',
                    'frequency': 720,
                    'full_name': 'Campbell, Bruce',
                    'gender': 'M',
                    'id': 2,
                    'location': 'Bed 3',
                    'next_ews_time': 'overdue: 12:00 hours',
                    'other_identifier': '1234567',
                    'parent_location': 'Ward E',
                    'patient_identifier': '908 475 1234',
                    'sex': 'M'
                }
            ]
            return patients_list

        def mock_get_active_observations(*args, **kwargs):
            """Return a list of dictionaries (one for each observation)."""
            active_obs_list = [
                {
                    'name': 'Glasgow Coma Scale (GCS)',
                    'type': 'gcs'
                },
                {
                    'name': 'NEWS',
                    'type': 'ews'
                },
                {
                    'name': 'Blood Sugar',
                    'type': 'blood_sugar'
                }
            ]
            return active_obs_list

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', mock_get_assigned_activities),
            ('get_patients', mock_get_patients),
            ('get_active_observations', mock_get_active_observations)
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Setup and use a mocked version of the render() method
        def mock_httprequest_render(*args, **kwargs):
            test_logger.debug('Mock of HttpRequest.render() method called during the test.')

        with mock.patch.object(HttpRequest, 'render', side_effect=mock_httprequest_render) as mocked_method:
            test_resp = requests.get(get_patient_url, cookies=self.auth_resp.cookies)

        # Just the first element of every tuple is needed for reverting the patchers
        methods_to_revert = [m[0] for m in methods_patching_list]

        # Stop Odoo's patchers
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        # Test the render() method was called with the rightly processed arguments
        mocked_method.assert_called_once_with(
            'nh_eobs_mobile.patient',
            qcontext={
                'patient': {
                    'clinical_risk': 'None',
                    'dob': '1980-12-25 08:00:00',
                    'ews_score': '0',
                    'ews_trend': 'down',
                    'frequency': 720,
                    'full_name': 'Campbell, Bruce',
                    'gender': 'M',
                    'id': 2,
                    'location': 'Bed 3',
                    'next_ews_time': 'overdue: 12:00 hours',
                    'other_identifier': '1234567',
                    'parent_location': 'Ward E',
                    'patient_identifier': '908 475 1234',
                    'sex': 'M'
                },
                'urls': URLS,
                'section': 'patient',
                'obs_list': [  # the observations list was sorted by the controller's method under test
                    {
                        'name': 'NEWS',
                        'type': 'ews'
                    },
                    {
                        'name': 'Glasgow Coma Scale (GCS)',
                        'type': 'gcs'
                    },
                    {
                        'name': 'Blood Sugar',
                        'type': 'blood_sugar'
                    }
                ],
                'notification_count': 1,
                'username': self.login_name
            }
        )

    def test_method_get_single_patient_returns_404_when_no_patient_is_found(self):
        get_patient_route = [r for r in routes if r['name'] == 'single_patient']
        self.assertEqual(len(get_patient_route), 1,
                         "Endpoint to the 'single_patient' route not unique. Cannot run the test!")
        get_patient_url = self._build_url(get_patient_route[0]['endpoint'], '47', mobile=True)

        def mock_method_returning_empty_list(*args, **kwargs):
            return []

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        eobs_api._patch_method('get_patients', mock_method_returning_empty_list)

        # Reach the route under tests
        test_resp = requests.get(get_patient_url, cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        eobs_api._revert_method('get_patients')

        self.assertEqual(test_resp.status_code, 404)

    def test_method_get_share_patients(self):
        get_share_patients_route = [r for r in routes if r['name'] == 'share_patient_list']
        self.assertEqual(len(get_share_patients_route), 1,
                         "Endpoint to the 'share_patient_list' route not unique. Cannot run the test!")
        get_share_patients_url = self._build_url(get_share_patients_route[0]['endpoint'], None, mobile=True)

        # Odoo-patch models' methods to make them returning test data
        def mock_unassign_my_activities(*args, **kwargs):
            return True

        def mock_get_patients(*args, **kwargs):
            """Return a list of dictionaries (one for each patient)."""
            patients_list = [
                {
                    'clinical_risk': 'None',
                    'dob': '1980-12-25 08:00:00',
                    'ews_score': '0',
                    'ews_trend': 'down',
                    'frequency': 720,
                    'full_name': 'Campbell, Bruce',
                    'gender': 'M',
                    'id': 2,
                    'location': 'Bed 3',
                    'next_ews_time': 'overdue: 12:00 hours',
                    'other_identifier': '1234567',
                    'parent_location': 'Ward E',
                    'patient_identifier': '908 475 1234',
                    'sex': 'M'
                }
            ]
            return patients_list

        def mock_get_patient_followers(*args, **kwargs):
            for p in args[3]:
                p['followers'] = [
                    {
                        'id': 3,
                        'name': 'Nurse Nathaniel'
                    }
                ]
            return True

        def mock_get_invited_users(*args, **kwargs):
            for p in args[3]:
                p['invited_users'] = [
                    {
                        'id': 19,
                        'name': 'Nurse Natalia'
                    }
                ]
            return True

        def mock_get_assigned_activities(*args, **kwargs):
            """Return a list of dictionaries (one for each assigned activity)."""
            assigned_activities_list = [
                {
                    'id': 1,
                    'user': 'Nurse Nadine',
                    'count': 2,
                    'patient_ids': [47, 49],
                    'message': 'You have been invited to follow 2 patients from Nurse Nadine'
                }
            ]
            return assigned_activities_list

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('unassign_my_activities', mock_unassign_my_activities),
            ('get_patients', mock_get_patients),
            ('get_patient_followers', mock_get_patient_followers),
            ('get_invited_users', mock_get_invited_users),
            ('get_assigned_activities', mock_get_assigned_activities),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Setup and use a mocked version of the render() method
        def mock_httprequest_render(*args, **kwargs):
            test_logger.debug('Mock of HttpRequest.render() method called during the test.')

        with mock.patch.object(HttpRequest, 'render', side_effect=mock_httprequest_render) as mocked_method:
            test_resp = requests.get(get_share_patients_url, cookies=self.auth_resp.cookies)

        # Just the first element of every tuple is needed for reverting the patchers
        methods_to_revert = [m[0] for m in methods_patching_list]

        # Stop Odoo's patchers
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        # Test the render() method was called with the rightly processed arguments
        mocked_method.assert_called_once_with(
            'nh_eobs_mobile.share_patients_list',
            qcontext={
                'items': [
                    {
                        'clinical_risk': 'None',
                        'dob': '1980-12-25 08:00:00',
                        'ews_score': '0',
                        'ews_trend': 'down',
                        'frequency': 720,
                        'full_name': 'Campbell, Bruce',
                        'gender': 'M',
                        'id': 2,
                        'location': 'Bed 3',
                        'next_ews_time': 'overdue: 12:00 hours',
                        'other_identifier': '1234567',
                        'parent_location': 'Ward E',
                        'patient_identifier': '908 475 1234',
                        'sex': 'M',
                        'url': '/mobile/patient/2',
                        'color': 'level-none',
                        'trend_icon': 'icon-down-arrow',
                        'deadline_time': 'overdue: 12:00 hours',
                        'summary': False,
                        'followers': 'Nurse Nathaniel',
                        'follower_ids': [3],
                        'invited_users': 'Nurse Natalia'
                    }
                ],
                'section': 'patient',
                'username': self.login_name,
                'share_list': True,
                'notification_count': 1,
                'urls': URLS,
                'user_id': self.user_id
            }
        )


class TestGetSingleTaskMethod(tests.common.HttpCase):

    def _build_url(self, route_endpoint, route_arguments, mobile=True):
        """Build a URL from the endpoint and the arguments provided.

        :param route_endpoint: endpoint of a specific route, without arguments
        :type route_endpoint: str
        :param route_arguments: arguments for a specific route's endpoint
        :type route_arguments: str
        :param mobile: select between the 'web' or 'mobile' version of the URL (default: True)
        :type mobile: bool
        :returns: full URL, ready to be reached via browser or requests
        :rtype: str
        """
        if mobile:
            base_url = BASE_MOBILE_URL
        else:
            base_url = BASE_URL
        return '{0}{1}{2}'.format(base_url, route_endpoint, (route_arguments if route_arguments else ''))

    def _get_authenticated_response(self, user_name):
        """Get a Response object with an authenticated session within its cookies.

        :param user_name: username of the user to be authenticated as
        :type user_name: str
        :returns: a Response object
        """
        auth_response = requests.post(BASE_MOBILE_URL + 'login',
                                      {'username': user_name,
                                       'password': user_name,
                                       'database': DB_NAME},
                                      cookies=self.session_resp.cookies)
        return auth_response

    def _get_user_belonging_to_group(self, group_name):
        """Get the 'id' and the 'login' name of a user belonging to a specific group.

        :param group_name: name of the group from which retrieving a user (belonging to it)
        :type group_name: str
        :returns: a dictionary with 2 key-value couples:
            - 'login': the login name of the retrieved user (belonging to the group passed as argument)
            - 'id': the id of the retrieved user (belonging to the group passed as argument)
        :rtype: dict
        :returns: None if there isn't any user belonging to that group
        """
        users_pool = self.registry['res.users']
        users_login_list = users_pool.search_read(self.cr, self.uid,
                                                  domain=[('groups_id.name', '=', group_name)],
                                                  fields=['login', 'id'])
        try:
            user_data = random_choice(users_login_list)
        except IndexError:
            user_data = None
        return user_data

    def _bulk_patch_odoo_model_method(self, odoo_model, methods_patching):
        """Patch a list of methods related to an Odoo's model.

        :param odoo_model: a valid Odoo's model instance (e.g. fetched by 'self.registry()')
        :param methods_patching: list of two-values tuples, each containing:
            - the method to be patched (string)
            - the function that will substitute the method to be patched (the actual name of the function)
        :type methods_patching: list
        :return: True (if no errors were raised during the patching)
        :rtype: bool
        """
        for method_to_patch, substituting_function in methods_patching:
            odoo_model._patch_method(method_to_patch, substituting_function)
        return True

    def _revert_bulk_patch_odoo_model_method(self, odoo_model, methods_to_be_reverted):
        """Revert the Odoo's patching of a list of methods.

        :param odoo_model: A valid Odoo's model instance (e.g. fetched by 'self.registry()')
        :param methods_to_be_reverted: list of model's 'original' methods to be reactivated back (string)
        :type methods_to_be_reverted: list
        :return: True (if no errors were raised during the patching)
        :rtype: bool
        """
        for m in methods_to_be_reverted:
            odoo_model._revert_method(m)
        return True

    # Odoo-patch models' methods to make them returning test data
    @staticmethod
    def mock_get_assigned_activities(*args, **kwargs):
        """Return a list of dictionaries (one for each assigned activity)."""
        assigned_activities_list = [
            {
                'id': 1,
                'user': 'Nurse Nadine',
                'count': 2,
                'patient_ids': [47, 49],
                'message': 'You have been invited to follow 2 patients from Nurse Nadine'
            }
        ]
        return assigned_activities_list

    @staticmethod
    def mock_nh_activity_read(*args, **kwargs):
        task_data = {
            'id': 1942,
            'data_model': 'nh.clinical.patient.observation.ews',
            'patient_id': (2, 'Campbell, Bruce'),
            'summary': 'NEWS Observation',
            'user_id': False
        }
        return task_data

    @staticmethod
    def mock_get_patients(*args, **kwargs):
        """Return a list of dictionaries (one for each patient)."""
        patients_list = [
            {
                'clinical_risk': 'None',
                'dob': '1980-12-25 08:00:00',
                'ews_score': '0',
                'ews_trend': 'down',
                'frequency': 720,
                'full_name': 'Campbell, Bruce',
                'gender': 'M',
                'id': 2,
                'location': 'Bed 3',
                'next_ews_time': 'overdue: 12:00 hours',
                'other_identifier': '1234567',
                'parent_location': 'Ward E',
                'patient_identifier': '908 475 1234',
                'sex': 'M'
            }
        ]
        return patients_list

    @staticmethod
    def mock_unassign_my_activities(*args, **kwargs):
        return True

    @staticmethod
    def mock_nh_eobs_api_assign(*args, **kwargs):
        return True

    @staticmethod
    def mock_nh_eobs_api_get_form_description(*args, **kwargs):
        form_description = [
            {
                'name': 'meta',
                'type': 'meta',
                'score': True
            },
            {
                'name': 'test_integer',
                'type': 'integer',
                'label': 'Test Integer',
                'min': 1,
                'max': 59,
                'initially_hidden': False
            },
            {
                'name': 'test_float',
                'type': 'float',
                'label': 'Test Float',
                'min': 1,
                'max': 35.9,
                'digits': [2, 1],
                'initially_hidden': False
            },
            {
                'name': 'test_text',
                'type': 'text',
                'label': 'Test Text',
                'initially_hidden': False
            },
            {
                'name': 'test_select',
                'type': 'selection',
                'label': 'Test Select',
                'selection_type': 'text',
                'selection': [
                    ['an', 'An'],
                    ['option', 'Option'],
                    ['from', 'From'],
                    ['the', 'The'],
                    ['list', 'List']
                ],
                'initially_hidden': False
            }
        ]
        return form_description

    def _safely_exit_test_during_setup(self, exit_type='skip', reason=''):
        """
        Provide a safe way to skip a test or make it fail
        during the ``setUp()`` phase.

        Rationale:
        Calling ``TestCase.skipTest()`` or ``TestCase.fail()`` from the
        ``setUp()``method, abort the test and prevent the ``tearDown()``
        method to be run.
        This make every following test fail, because Odoo test cases rely on
        the ``tearDown()`` to properly close the DB test cursor and set the
        test mode flag as ``False``.

        :param exit_type: type of exit for the test method
        (can be 'skip' or 'fail' - the default value is 'skip')
        :type exit_type: str
        :param reason: reason for skipping the test (or making it fail).
        It will be passed to the exiting function (default to empty string)
        :type reason: str
        """
        super(self.__class__, self).tearDown()
        if exit_type.lower() == 'skip':
            self.skipTest(reason)
        elif exit_type.lower() == 'fail':
            self.fail(reason)

    def setUp(self):
        super(TestGetSingleTaskMethod, self).setUp()
        self.session_resp = requests.post(BASE_URL + 'web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self._safely_exit_test_during_setup(
                exit_type='skip',
                reason='Cannot retrieve a valid session to be used '
                       'for the test.'
            )

        user_data = self._get_user_belonging_to_group('NH Clinical Nurse Group')
        if user_data:
            self.login_name = user_data.get('login')
        else:
            self._safely_exit_test_during_setup(
                exit_type='skip',
                reason='Cannot retrieve any user for authentication '
                       'before running the test.'
            )
        if not self.login_name:
            self._safely_exit_test_during_setup(
                exit_type='skip',
                reason='Cannot retrieve the login name for authentication '
                       'before running the test.'
            )
        self.auth_resp = self._get_authenticated_response(self.login_name)

        # Check the right page was reached successfully
        self.assertEqual(self.auth_resp.status_code, 200)

        task_list_route = [r for r in routes if r['name'] == 'task_list']
        if len(task_list_route) != 1:
            self._safely_exit_test_during_setup(
                exit_type='skip',
                reason="Cannot retrieve the 'task list' route to be used "
                       "during the tests."
            )
        self.task_list_url = self._build_url(task_list_route[0]['endpoint'],
                                             None)
        self.assertIn(self.task_list_url, self.auth_resp.url)

        get_task_route = [r for r in routes if r['name'] == 'single_task']
        if len(get_task_route) != 1:
            self._safely_exit_test_during_setup(
                exit_type='skip',
                reason="Endpoint to the 'single_task' route not unique."
            )
        self.get_task_url = self._build_url(get_task_route[0]['endpoint'], '1942', mobile=True)

    def test_method_get_single_task_of_type_observation(self):
        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', TestGetSingleTaskMethod.mock_get_assigned_activities),
            ('get_patients', TestGetSingleTaskMethod.mock_get_patients),
            ('unassign_my_activities', TestGetSingleTaskMethod.mock_unassign_my_activities),
            ('assign', TestGetSingleTaskMethod.mock_nh_eobs_api_assign),
            ('get_form_description', TestGetSingleTaskMethod.mock_nh_eobs_api_get_form_description),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)
        self.registry['nh.activity']._patch_method('read', TestGetSingleTaskMethod.mock_nh_activity_read)

        # Setup and use a mocked version of the render() method
        def mock_httprequest_render(*args, **kwargs):
            test_logger.debug('Mock of HttpRequest.render() method called during the test.')

        with mock.patch.object(HttpRequest, 'render', side_effect=mock_httprequest_render) as mocked_method:
            # Mock the 'datetime' class to force it to return a constant value.
            # N.B. the 'datetime' class MUST BE the one imported from the code under test, otherwise the mocking process won't work
            # datetime.now() and datetime.strftime() are the methods actually used in the code under test, hence they must be mocked.
            with mock.patch('openerp.addons.nh_eobs_mobile.controllers.main.datetime') as patched_datetime:
                patched_now_method = patched_datetime.now.return_value
                patched_now_method.strftime.return_value = '1400000000'

                test_resp = requests.get(self.get_task_url, cookies=self.auth_resp.cookies)

        # Just the first element of every tuple is needed for reverting the patchers
        methods_to_revert = [m[0] for m in methods_patching_list]

        # Stop Odoo's patchers
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)
        self.registry['nh.activity']._revert_method('read')

        # Test the render() method was called with the rightly processed arguments
        expected_form = {
            'action': '/mobile/task/submit/1942',
            'type': 'ews',
            'task-id': 1942,
            'patient-id': 2,
            'source': 'task',
            'start': '1400000000',
            'obs_needs_score': True
        }
        expected_inputs = [
            {
                'name': 'test_integer',
                'type': 'number',
                'label': 'Test Integer',
                'min': '1',
                'max': 59,
                'step': 1,
                'initially_hidden': False,
                'number': True,
                'info': '',
                'errors': ''
            },
            {
                'name': 'test_float',
                'type': 'number',
                'label': 'Test Float',
                'min': '1',
                'max': 35.9,
                'step': 0.1,
                'digits': [2, 1],
                'initially_hidden': False,
                'number': True,
                'info': '',
                'errors': ''
            },
            {
                'name': 'test_text',
                'type': 'text',
                'label': 'Test Text',
                'initially_hidden': False,
                'info': '',
                'errors': ''
            },
            {
                'name': 'test_select',
                'type': 'selection',
                'label': 'Test Select',
                'selection_type': 'text',
                'selection': [
                    ['an', 'An'],
                    ['option', 'Option'],
                    ['from', 'From'],
                    ['the', 'The'],
                    ['list', 'List']
                ],
                'initially_hidden': False,
                'info': '',
                'errors': '',
                'selection_options': [
                    {
                        'value': 'an',
                        'label': 'An'
                    },
                    {
                        'value': 'option',
                        'label': 'Option'
                    },
                    {
                        'value': 'from',
                        'label': 'From'
                    },
                    {
                        'value': 'the',
                        'label': 'The'
                    },
                    {
                        'value': 'list',
                        'label': 'List'
                    }
                ]
            }
        ]
        mocked_method.assert_called_once_with(
            'nh_eobs_mobile.observation_entry',
            qcontext={
                'inputs': expected_inputs,
                'name': 'NEWS Observation',
                'patient': {
                    'id': 2,
                    'name': 'Campbell, Bruce',
                    'url': '/mobile/patient/2'
                },
                'form': expected_form,
                'section': 'task',
                'username': self.login_name,
                'notification_count': 1,
                'urls': URLS
            }
        )

    def test_method_get_single_task_of_type_placement(self):
        def mock_nh_activity_read(*args, **kwargs):
            task_data = {
                'id': 1942,
                'data_model': 'nh.clinical.patient.placement',
                'patient_id': (2, 'Campbell, Bruce'),
                'summary': 'Assess Patient',
                'user_id': False
            }
            return task_data

        def mock_nh_eobs_api_get_form_description(*args, **kwargs):
            form_description = [
                {
                    'name': 'test_integer',
                    'type': 'integer',
                    'label': 'Test Integer',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False
                },
                {
                    'name': 'test_float',
                    'type': 'float',
                    'label': 'Test Float',
                    'min': 1,
                    'max': 35.9,
                    'digits': [2, 1],
                    'initially_hidden': False
                },
                {
                    'name': 'test_text',
                    'type': 'text',
                    'label': 'Test Text',
                    'initially_hidden': False
                },
                {
                    'name': 'test_select',
                    'type': 'selection',
                    'label': 'Test Select',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': False
                }
            ]
            return form_description

        def mock_nh_eobs_api_is_cancellable(*args, **kwargs):
            return False

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', TestGetSingleTaskMethod.mock_get_assigned_activities),
            ('get_patients', TestGetSingleTaskMethod.mock_get_patients),
            ('unassign_my_activities', TestGetSingleTaskMethod.mock_unassign_my_activities),
            ('assign', TestGetSingleTaskMethod.mock_nh_eobs_api_assign),
            ('get_form_description', mock_nh_eobs_api_get_form_description),
            ('is_cancellable', mock_nh_eobs_api_is_cancellable),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)
        self.registry['nh.activity']._patch_method('read', mock_nh_activity_read)

        # Setup and use a mocked version of the render() method
        def mock_httprequest_render(*args, **kwargs):
            test_logger.debug('Mock of HttpRequest.render() method called during the test.')

        with mock.patch.object(HttpRequest, 'render', side_effect=mock_httprequest_render) as mocked_method:
            # Mock the 'datetime' class to force it to return a constant value.
            # N.B. the 'datetime' class MUST BE the one imported from the code under test, otherwise the mocking process won't work
            # datetime.now() and datetime.strftime() are the methods actually used in the code under test, hence they must be mocked.
            with mock.patch('openerp.addons.nh_eobs_mobile.controllers.main.datetime') as patched_datetime:
                patched_now_method = patched_datetime.now.return_value
                patched_now_method.strftime.return_value = '1400000000'

                test_resp = requests.get(self.get_task_url, cookies=self.auth_resp.cookies)

        # Just the first element of every tuple is needed for reverting the patchers
        methods_to_revert = [m[0] for m in methods_patching_list]

        # Stop Odoo's patchers
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)
        self.registry['nh.activity']._revert_method('read')

        # Test the render() method was called with the rightly processed arguments
        expected_form = {
            'action': '/mobile/tasks/confirm_clinical/1942',
            'type': 'placement',
            'task-id': 1942,
            'patient-id': 2,
            'source': 'task',
            'start': '1400000000',
            'confirm_url': '/mobile/tasks/confirm_clinical/1942'
        }
        expected_inputs = [
            {
                'name': 'test_integer',
                'type': 'number',
                'label': 'Test Integer',
                'min': '1',
                'max': 59,
                'step': 1,
                'initially_hidden': False,
                'number': True,
            },
            {
                'name': 'test_float',
                'type': 'number',
                'label': 'Test Float',
                'min': '1',
                'max': 35.9,
                'step': 0.1,
                'digits': [2, 1],
                'initially_hidden': False,
                'number': True,
            },
            {
                'name': 'test_text',
                'type': 'text',
                'label': 'Test Text',
                'initially_hidden': False,
            },
            {
                'name': 'test_select',
                'type': 'selection',
                'label': 'Test Select',
                'selection_type': 'text',
                'selection': [
                    ['an', 'An'],
                    ['option', 'Option'],
                    ['from', 'From'],
                    ['the', 'The'],
                    ['list', 'List']
                ],
                'initially_hidden': False,
                'selection_options': [
                    {
                        'value': 'an',
                        'label': 'An'
                    },
                    {
                        'value': 'option',
                        'label': 'Option'
                    },
                    {
                        'value': 'from',
                        'label': 'From'
                    },
                    {
                        'value': 'the',
                        'label': 'The'
                    },
                    {
                        'value': 'list',
                        'label': 'List'
                    }
                ]
            }
        ]
        mocked_method.assert_called_once_with(
            'nh_eobs_mobile.notification_confirm_cancel',
            qcontext={
                'name': 'Assess Patient',
                'inputs': expected_inputs,
                'cancellable': False,
                'patient': {
                    'id': 2,
                    'name': 'Campbell, Bruce',
                    'url': '/mobile/patient/2'
                },
                'form': expected_form,
                'section': 'task',
                'username': self.login_name,
                'notification_count': 1,
                'urls': URLS
            }
        )

    def test_method_get_single_task_of_type_notification_cancellable(self):
        def mock_nh_activity_read(*args, **kwargs):
            task_data = {
                'id': 1942,
                'data_model': 'nh.clinical.notification.medical_team',
                'patient_id': (2, 'Campbell, Bruce'),
                'summary': 'Inform Medical Team?',
                'user_id': False
            }
            return task_data

        def mock_nh_eobs_api_get_form_description(*args, **kwargs):
            form_description = [
                {
                    'name': 'test_integer',
                    'type': 'integer',
                    'label': 'Test Integer',
                    'min': 1,
                    'max': 59,
                    'initially_hidden': False
                },
                {
                    'name': 'test_float',
                    'type': 'float',
                    'label': 'Test Float',
                    'min': 1,
                    'max': 35.9,
                    'digits': [2, 1],
                    'initially_hidden': False
                },
                {
                    'name': 'test_text',
                    'type': 'text',
                    'label': 'Test Text',
                    'initially_hidden': False
                },
                {
                    'name': 'test_select',
                    'type': 'selection',
                    'label': 'Test Select',
                    'selection_type': 'text',
                    'selection': [
                        ['an', 'An'],
                        ['option', 'Option'],
                        ['from', 'From'],
                        ['the', 'The'],
                        ['list', 'List']
                    ],
                    'initially_hidden': False
                }
            ]
            return form_description

        def mock_nh_eobs_api_is_cancellable(*args, **kwargs):
            return True

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', TestGetSingleTaskMethod.mock_get_assigned_activities),
            ('get_patients', TestGetSingleTaskMethod.mock_get_patients),
            ('unassign_my_activities', TestGetSingleTaskMethod.mock_unassign_my_activities),
            ('assign', TestGetSingleTaskMethod.mock_nh_eobs_api_assign),
            ('get_form_description', mock_nh_eobs_api_get_form_description),
            ('is_cancellable', mock_nh_eobs_api_is_cancellable),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)
        self.registry['nh.activity']._patch_method('read', mock_nh_activity_read)

        # Setup and use a mocked version of the render() method
        def mock_httprequest_render(*args, **kwargs):
            test_logger.debug('Mock of HttpRequest.render() method called during the test.')

        with mock.patch.object(HttpRequest, 'render', side_effect=mock_httprequest_render) as mocked_method:
            # Mock the 'datetime' class to force it to return a constant value.
            # N.B. the 'datetime' class MUST BE the one imported from the code under test, otherwise the mocking process won't work
            # datetime.now() and datetime.strftime() are the methods actually used in the code under test, hence they must be mocked.
            with mock.patch('openerp.addons.nh_eobs_mobile.controllers.main.datetime') as patched_datetime:
                patched_now_method = patched_datetime.now.return_value
                patched_now_method.strftime.return_value = '1400000000'

                test_resp = requests.get(self.get_task_url, cookies=self.auth_resp.cookies)

        # Just the first element of every tuple is needed for reverting the patchers
        methods_to_revert = [m[0] for m in methods_patching_list]

        # Stop Odoo's patchers
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)
        self.registry['nh.activity']._revert_method('read')

        # Test the render() method was called with the rightly processed arguments
        expected_form = {
            'action': '/mobile/tasks/confirm_clinical/1942',
            'type': 'medical_team',
            'task-id': 1942,
            'patient-id': 2,
            'source': 'task',
            'start': '1400000000',
            'confirm_url': '/mobile/tasks/confirm_clinical/1942',
            'cancel_url': '/mobile/tasks/cancel_clinical/1942'
        }
        expected_inputs = [
            {
                'name': 'test_integer',
                'type': 'number',
                'label': 'Test Integer',
                'min': '1',
                'max': 59,
                'step': 1,
                'initially_hidden': False,
                'number': True,
            },
            {
                'name': 'test_float',
                'type': 'number',
                'label': 'Test Float',
                'min': '1',
                'max': 35.9,
                'step': 0.1,
                'digits': [2, 1],
                'initially_hidden': False,
                'number': True,
            },
            {
                'name': 'test_text',
                'type': 'text',
                'label': 'Test Text',
                'initially_hidden': False,
            },
            {
                'name': 'test_select',
                'type': 'selection',
                'label': 'Test Select',
                'selection_type': 'text',
                'selection': [
                    ['an', 'An'],
                    ['option', 'Option'],
                    ['from', 'From'],
                    ['the', 'The'],
                    ['list', 'List']
                ],
                'initially_hidden': False,
                'selection_options': [
                    {
                        'value': 'an',
                        'label': 'An'
                    },
                    {
                        'value': 'option',
                        'label': 'Option'
                    },
                    {
                        'value': 'from',
                        'label': 'From'
                    },
                    {
                        'value': 'the',
                        'label': 'The'
                    },
                    {
                        'value': 'list',
                        'label': 'List'
                    }
                ]
            }
        ]
        mocked_method.assert_called_once_with(
            'nh_eobs_mobile.notification_confirm_cancel',
            qcontext={
                'name': 'Inform Medical Team?',
                'inputs': expected_inputs,
                'cancellable': True,
                'patient': {
                    'id': 2,
                    'name': 'Campbell, Bruce',
                    'url': '/mobile/patient/2'
                },
                'form': expected_form,
                'section': 'task',
                'username': self.login_name,
                'notification_count': 1,
                'urls': URLS
            }
        )

    def test_method_get_single_task_of_not_valid_type(self):
        # Override the class' static method to make it return an invalid observation type
        def mock_nh_activity_read(*args, **kwargs):
            task_data = {
                'id': 1942,
                'data_model': 'nh.clinical.fake_task_type',
                'patient_id': (2, 'Campbell, Bruce'),
                'summary': 'NEWS Observation',
                'user_id': False
            }
            return task_data

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', TestGetSingleTaskMethod.mock_get_assigned_activities),
            ('get_patients', TestGetSingleTaskMethod.mock_get_patients),
            ('unassign_my_activities', TestGetSingleTaskMethod.mock_unassign_my_activities),
            ('assign', TestGetSingleTaskMethod.mock_nh_eobs_api_assign),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)
        self.registry['nh.activity']._patch_method('read', mock_nh_activity_read)

        # Setup and use a mocked version of the render() method
        def mock_httprequest_render(*args, **kwargs):
            test_logger.debug('Mock of HttpRequest.render() method called during the test.')

        with mock.patch.object(HttpRequest, 'render', side_effect=mock_httprequest_render) as mocked_method:
            test_resp = requests.get(self.get_task_url, cookies=self.auth_resp.cookies)

        # Just the first element of every tuple is needed for reverting the patchers
        methods_to_revert = [m[0] for m in methods_patching_list]

        # Stop Odoo's patchers
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)
        self.registry['nh.activity']._revert_method('read')

        # Test the render() method was called with the rightly processed arguments
        mocked_method.assert_called_once_with(
            'nh_eobs_mobile.error',
            qcontext={
                'error_string': 'Task is neither a notification nor an observation',
                'section': 'task',
                'username': self.login_name,
                'urls': URLS
            }
        )

    def test_method_get_single_task_manages_specific_exception_while_assigning_task(self):
        # Override the class' static method to make it raise an exception
        def mock_nh_eobs_api_assign(*args, **kwargs):
            raise except_orm('Expected exception!', 'Expected exception raised during the test.')

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', TestGetSingleTaskMethod.mock_get_assigned_activities),
            ('get_patients', TestGetSingleTaskMethod.mock_get_patients),
            ('unassign_my_activities', TestGetSingleTaskMethod.mock_unassign_my_activities),
            ('assign', mock_nh_eobs_api_assign),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)
        self.registry['nh.activity']._patch_method('read', TestGetSingleTaskMethod.mock_nh_activity_read)

        try:
            test_resp = requests.get(self.get_task_url, cookies=self.auth_resp.cookies)
        except except_orm:
            self.fail('Method under test raised an exception it is supposed to manage!')
        finally:
            # Just the first element of every tuple is needed for reverting the patchers
            methods_to_revert = [m[0] for m in methods_patching_list]

            # Stop Odoo's patchers
            self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)
            self.registry['nh.activity']._revert_method('read')

        self.assertEqual(len(test_resp.history), 1, 'Method under test did not redirect after the exception.')
        self.assertEqual(test_resp.history[0].status_code, 303,
                         'HTTP code during the redirection was not the expected one.')
        self.assertIn('tasks', test_resp.url)
        self.assertIn(self.task_list_url, test_resp.url, 'Method under test did not redirect to the expected page.')

    def test_method_get_task_first_unassign_and_then_try_assigning_task(self):
        mocked_method_calling_list = []

        # Two different mocking methods are needed, despite they are identical:
        # in fact, if two different methods are being mocked by one single function,
        # the system cannot understand which one is meant to be called, and could raise errors.
        def register_mock_unassign_calling(*args, **kwargs):
            mocked_method_calling_list.append(('ARGS = {}'.format(args), 'KWARGS = {}'.format(kwargs)))
            return True

        def register_mock_assign_calling(*args, **kwargs):
            mocked_method_calling_list.append(('ARGS = {}'.format(args), 'KWARGS = {}'.format(kwargs)))
            return True

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', TestGetSingleTaskMethod.mock_get_assigned_activities),
            ('get_patients', TestGetSingleTaskMethod.mock_get_patients),
            ('unassign_my_activities', register_mock_unassign_calling),
            ('assign', register_mock_assign_calling),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)
        self.registry['nh.activity']._patch_method('read', TestGetSingleTaskMethod.mock_nh_activity_read)

        # Actually reach the 'single task' page
        try:
            test_resp = requests.get(self.get_task_url, cookies=self.auth_resp.cookies)
        finally:
            # Just the first element of every tuple is needed for reverting the patchers
            methods_to_revert = [m[0] for m in methods_patching_list]

            # Stop Odoo's patchers
            self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)
            self.registry['nh.activity']._revert_method('read')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(len(mocked_method_calling_list), 2)

    def test_method_single_task_returns_404_when_task_has_no_patient_related_to_it(self):
        """
        Test that the method returns a '404 Not Found' response
        if the task doesn't have a patient related to it.
        (e.g. this could happen when a user tries
        to reach a non-existing task,
        by manually inputting a wrong task ID in the URL).
        In such a case, the search among activities will return False.
        """
        def mock_nh_activity_read(*args, **kwargs):
            return False

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', TestGetSingleTaskMethod.mock_get_assigned_activities),
            ('get_patients', TestGetSingleTaskMethod.mock_get_patients),
            ('unassign_my_activities', TestGetSingleTaskMethod.mock_unassign_my_activities),
            ('assign', TestGetSingleTaskMethod.mock_nh_eobs_api_assign),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)
        self.registry['nh.activity']._patch_method('read', mock_nh_activity_read)

        # Actually reach the 'single task' page
        try:
            test_resp = requests.get(self.get_task_url, cookies=self.auth_resp.cookies)
        finally:
            # Just the first element of every tuple is needed for reverting the patchers
            methods_to_revert = [m[0] for m in methods_patching_list]

            # Stop Odoo's patchers
            self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)
            self.registry['nh.activity']._revert_method('read')

        self.assertEqual(test_resp.status_code, 404)

    def test_method_single_task_returns_404_when_list_of_related_patients_is_empty(self):
        """
        Test that the method returns a '404 Not Found' response,
        if the list of patients related to the task is empty.

        Despite this edge case is theoretically impossible
        in a real world scenario, this test assures that the code
        properly manages such an edge-case value.
        """
        def mock_get_patients(*args, **kwargs):
            empty_list = []
            return empty_list

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities', TestGetSingleTaskMethod.mock_get_assigned_activities),
            ('get_patients', mock_get_patients),
            ('unassign_my_activities', TestGetSingleTaskMethod.mock_unassign_my_activities),
            ('assign', TestGetSingleTaskMethod.mock_nh_eobs_api_assign),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)
        self.registry['nh.activity']._patch_method('read', TestGetSingleTaskMethod.mock_nh_activity_read)

        # Actually reach the 'single task' page
        try:
            test_resp = requests.get(self.get_task_url, cookies=self.auth_resp.cookies)
        finally:
            # Just the first element of every tuple is needed for reverting the patchers
            methods_to_revert = [m[0] for m in methods_patching_list]

            # Stop Odoo's patchers
            self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)
            self.registry['nh.activity']._revert_method('read')

        self.assertEqual(test_resp.status_code, 404)