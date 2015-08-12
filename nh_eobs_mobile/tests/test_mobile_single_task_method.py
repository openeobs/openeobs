__author__ = 'lorenzo'

import logging
import requests
from random import choice as random_choice

from openerp import tests
from openerp.addons.nh_eobs_mobile.controllers.urls import routes
from openerp.osv import orm
from openerp.tests import DB as DB_NAME
from openerp.tools import config


SERVER_PROTOCOL = "http"
SERVER_ADDRESS = "localhost"
SERVER_PORT = "{0}".format(config['xmlrpc_port'])
MOBILE_URL_PREFIX = 'mobile/'
BASE_URL = SERVER_PROTOCOL + '://' + SERVER_ADDRESS + ':' + SERVER_PORT + '/'
BASE_MOBILE_URL = BASE_URL + MOBILE_URL_PREFIX

test_logger = logging.getLogger(__name__)


class TestMobileControllerTaskMethods(tests.common.HttpCase):

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
        super(TestMobileControllerTaskMethods, self).setUp()
        self.session_resp = requests.post(BASE_URL + 'web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self.fail('Cannot retrieve a valid session to be used for the tests!')

        login_name = self._get_user_belonging_to_group('NH Clinical Nurse Group')
        self.assertNotEqual(login_name, False,
                            "Cannot find any 'nurse' user for authentication before running the test!")
        self.auth_resp = self._get_authenticated_response(login_name)
        self.assertEqual(self.auth_resp.status_code, 200)
        self.assertIn('class="tasklist"', self.auth_resp.content)

    def test_02_method_get_task_first_unassign_and_then_try_assigning_task(self):
        mocked_method_calling_list = []

        def register_mock_calling_list(*args, **kwargs):
            mocked_method_calling_list.append(('ARGS = {}'.format(args), 'KWARGS = {}'.format(kwargs)))

        # Try to retrieve an activity with no user related to it (skip the test if cannot find any)
        activity_registry = self.registry['nh.activity']
        task_id_list = activity_registry.search(self.cr, self.uid, [], limit=1)
        if len(task_id_list) == 0:
            self.skipTest('Cannot find an activity that has no user related to it. Cannot run the test!')

        # Retrieve the 'single_task' route and build the complete URL for it
        single_task = [r for r in routes if r['name'] == 'single_task']
        self.assertEqual(len(single_task), 1,
                         "Endpoint to the 'single_task' route not unique. Cannot run the test!")
        single_task_url = self._build_url(single_task[0]['endpoint'], task_id_list[0], mobile=True)

        # Start the Odoo's patchers
        self.registry('nh.eobs.api')._patch_method('unassign_my_activities', register_mock_calling_list)
        self.registry('nh.eobs.api')._patch_method('assign', register_mock_calling_list)

        # Actually reach the 'single task' page
        test_resp = requests.get(single_task_url, cookies=self.auth_resp.cookies)

        # Stop the Odoo's patchers
        self.registry('nh.eobs.api')._revert_method('unassign_my_activities')
        self.registry('nh.eobs.api')._revert_method('assign')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(len(mocked_method_calling_list), 2)

    def test_01_method_get_task_catches_right_exception(self):
        self.assertEqual(1+2, 3)

        # Try to retrieve an activity with no user related to it (skip the test if cannot find any)
        activity_registry = self.registry['nh.activity']
        task_id_list = activity_registry.search(self.cr, self.uid, [], limit=1)
        if len(task_id_list) == 0:
            self.skipTest('Cannot find an activity that has no user related to it. Cannot run the test!')

        def mock_unassign_activities(*args, **kwargs):
            pass

        def mock_assign(*args, **kwargs):
            raise orm.except_orm('Expected exception!', 'Expected exception raised during the test.')

        # Retrieve the 'single_task' route and build the complete URL for it
        single_task = [r for r in routes if r['name'] == 'single_task']
        self.assertEqual(len(single_task), 1,
                         "Endpoint to the 'single_task' route not unique. Cannot run the test!")
        single_task_url = self._build_url(single_task[0]['endpoint'], task_id_list[0], mobile=True)

        # Start the Odoo's patchers
        self.registry('nh.eobs.api')._patch_method('unassign_my_activities', mock_unassign_activities)
        self.registry('nh.eobs.api')._patch_method('assign', mock_assign)

        # Actually reach the 'single task' page
        test_resp = requests.get(single_task_url, cookies=self.auth_resp.cookies)

        # Stop the Odoo's patchers
        self.registry('nh.eobs.api')._revert_method('unassign_my_activities')
        self.registry('nh.eobs.api')._revert_method('assign')

        self.assertEqual(len(test_resp.history), 1)
        self.assertEqual(test_resp.history[0].status_code, 303)
        self.assertIn('tasks', test_resp.url)

