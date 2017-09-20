from random import choice as random_choice
from openerp.addons.nh_eobs_api.controllers.route_api import route_manager
from openerp.tests import DB as DB_NAME
from openerp.osv import osv
import json
import logging
import openerp.tests
import requests

test_logger = logging.getLogger(__name__)


class APITestCommon(openerp.tests.common.HttpCase):

    json_response_structure_keys = ['status', 'title', 'description', 'data']

    def _get_user_belonging_to_group(self, group_name):
        """Get the 'id' and the 'login' name of a user belonging to a
        specific group.

        :param group_name: name of the group from which retrieve a user
        (belonging to it)
        :type group_name: str
        :returns: A dictionary with 2 key-value couples:
            - 'login': the login name of the retrieved user
            (belonging to the group passed as argument)
            - 'id': the id of the retrieved user
            (belonging to the group passed as argument)
        :rtype: dict
        :returns: ``None`` if there isn't any user belonging to that group
        """
        users_pool = self.registry['res.users']
        users_login_list = users_pool.search_read(
            self.cr, self.uid,
            domain=[('groups_id.name', '=', group_name)],
            fields=['login', 'id'])
        try:
            user_data = random_choice(users_login_list)
        except IndexError:
            user_data = None
        return user_data

    def _get_authenticated_response(self, user_name):
        """Get a Response object with an authenticated session
        within its cookies.

        :param user_name: username of the user to be authenticated as
        :type user_name: str
        :returns: A Response object
        """
        auth_response = requests.post(route_manager.BASE_URL + '/web/login',
                                      {'login': user_name,
                                       'password': user_name,
                                       'database': DB_NAME},
                                      cookies=self.session_resp.cookies)
        return auth_response

    def check_response_json(self, response, status, title, description, data):
        """
        Wraps `check_json` to handle passing of a response, performs the
        additional step of converting the response into a dictionary before
        passing it on to the wrapped method.

        :param response: Raw response from requests
        :param status: The expected status code for the response
        :param title: The title to be shown on the popup on Frontend
        :param description: The description to be used in the popup on Frontend
        :param data: Data the be sent to the Frontend to show in popup
        :returns: ``True`` cos the tests will cause the thing to fail anyways
        """
        response_json_str = response.read()
        response_json_dict = json.loads(response_json_str)
        return self.check_json(response_json_dict, status, title, description, data)

    def check_json(self, json_data, status, title, description, data):
        """
        Test the response JSON for correct status, title, desc and
        data values.

        :param json_data: JSON data.
        :type json_data: dict
        :param status: The expected status code for the response
        :param title: The title to be shown on the popup on Frontend
        :param description: The description to be used in the popup on Frontend
        :param data: Data the be sent to the Frontend to show in popup
        :returns: ``True`` cos the tests will cause the thing to fail anyways
        """
        for k in self.json_response_structure_keys:
            self.assertIn(k, json_data)

        self.assertEqual(json_data['status'], status)
        self.assertEqual(json_data['title'], title)
        self.assertEqual(json_data['description'], description)
        returned_data = json.dumps(json_data['data'])
        json_data = json.dumps(data)
        self.assertEqual(json.loads(returned_data), json.loads(json_data))
        return True

    def _bulk_patch_odoo_model_method(self, odoo_model, methods_patching):
        """Patch a list of methods related to an Odoo's model.

        :param odoo_model: A valid Odoo's model instance
        (e.g. fetched by 'self.registry()')
        :param methods_patching: A list of two-values tuples, each containing:
            - the method to be patched (string)
            - the function that will substitute the method to be patched
            (the actual name of the function)
        :type methods_patching: tuple
        :returns: ``True`` (if no errors were raised during the patching)
        :rtype: bool
        """
        for method_to_patch, substituting_function in methods_patching:
            odoo_model._patch_method(method_to_patch, substituting_function)
        return True

    def _revert_bulk_patch_odoo_model_method(self, odoo_model,
                                             methods_to_be_reverted):
        """Revert the Odoo's patching of a list of methods.

        :param odoo_model: A valid Odoo's model instance
        (e.g. fetched by 'self.registry()')
        :param methods_to_be_reverted: A list of model's 'original' methods
        to be reactivated back (string)
        :type methods_to_be_reverted: list of str
        :returns: ``True`` (if no errors were raised during the patching)
        :rtype: bool
        """
        for m in methods_to_be_reverted:
            odoo_model._revert_method(m)
        return True

    # Mock Odoo's models' methods
    @staticmethod
    def mock_get_assigned_activities(*args, **kwargs):
        """Return a list of dictionaries (one for each assigned activity)."""
        assigned_activities_list = [
            {
                'id': 2001,
                'user': 'Nurse Nadine',
                'count': 3,
                'patient_ids': [1, 2, 3],
                'message': 'You have been invited to follow 3 '
                           'patients from Nurse Nadine'
            }
        ]
        return assigned_activities_list

    @staticmethod
    def mock_get_patients(*args, **kwargs):
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
                'next_ews_time': '04:00 hours',
                'other_identifier': '1234567',
                'parent_location': 'Ward E',
                'patient_identifier': '908 475 1234',
                'sex': 'M'
            },
            {
                'clinical_risk': 'Low',
                'dob': '1980-08-31 18:00:00',
                'ews_score': '2',
                'ews_trend': 'down',
                'frequency': 240,
                'full_name': 'Franklin, Donna',
                'gender': 'F',
                'id': 1,
                'location': 'Bed 2',
                'next_ews_time': 'overdue: 02:00 hours',
                'other_identifier': '4867593',
                'parent_location': 'Ward E',
                'patient_identifier': '494 333 0012',
                'sex': 'F'
            },
            {
                'clinical_risk': 'Medium',
                'dob': '1980-04-25 12:00:00',
                'ews_score': '5',
                'ews_trend': 'up',
                'frequency': 60,
                'full_name': 'Hasselhoff, David',
                'gender': 'M',
                'id': 3,
                'location': 'Bed 1',
                'next_ews_time': '01:00 hours',
                'other_identifier': '3958684',
                'parent_location': 'Ward E',
                'patient_identifier': '112 009 007',
                'sex': 'M'
            }
        ]
        return patients_list

    @staticmethod
    def mock_res_users_read(*args, **kwargs):
        users_list = [
            {
                'id': 33,
                'login': 'john',
                'display_name': 'John Smith'
            },
            {
                'id': 34,
                'login': 'jane',
                'display_name': 'Jane Doe'
            },
            {
                'id': 35,
                'login': 'joe',
                'display_name': 'Joe Average'
            },
        ]
        return users_list

    @staticmethod
    def mock_method_returning_true(*args, **kwargs):
        return True

    @staticmethod
    def mock_method_returning_osv_exception(*args, **kwargs):
        raise osv.except_osv('Expected exception!',
                             'Expected exception raised during the test.')

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
        """
        Get an authenticated response from the server so we can reuse
        the session cookie for subsequent calls.
        """
        super(APITestCommon, self).setUp()

        # TODO [EOBS-1462] Stop Using demo data in HTTP test cases
        self.login_name = 'nasir'
        self.user_id = 40

        self.authenticate(self.login_name, self.login_name)
