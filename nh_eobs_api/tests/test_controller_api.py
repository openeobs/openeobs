# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.addons.nh_eobs_api.routing import Route
from openerp.addons.nh_eobs_api.routing import ResponseJSON
from openerp.addons.nh_eobs_api.controllers.route_api import route_manager
from . import api_test_common
import logging
import requests

test_logger = logging.getLogger(__name__)


class TestOdooRouteDecoratorIntegration(api_test_common.APITestCommon):

    # Test Observation based routes
    def test_route_calculate_ews_score(self):
        """
        Test the EWS score route, send EWS parameters to route
        and make sure it sends back score.
        """
        # Check if the route under test is actually present in the
        # Route Manager
        route_under_test = route_manager.get_route('calculate_obs_score')
        self.assertIsInstance(route_under_test, Route)

        # Create demo data
        demo_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55,
            'avpu_text': 'A',
            'taskId': 666,
            'startTimestamp': 0,
        }

        # Access the route
        test_resp = requests.post(
            '{0}{1}/observation/score/ews/'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX
            ),
            data=demo_data,
            cookies=self.auth_resp.cookies
        )
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'score': {
                'score': 3,
                'clinical_risk': 'Medium',
                'three_in_one': True
            },
            'modal_vals': {
                'next_action': 'json_task_form_action',
                'title': 'Submit NEWS score of 3',
                'content': '<p><strong>Clinical risk: Medium</strong>'
                           '</p><p>Please confirm you want to '
                           'submit this score</p>'
            },
            'status': 3,
            'next_action': 'json_task_form_action',
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Submit NEWS score of 3',
                                 '<p><strong>Clinical risk: Medium</strong>'
                                 '</p><p>Please confirm you want to '
                                 'submit this score</p>',
                                 expected_json)

    def test_route_calculate_gcs_score(self):
        """
        Test the GCS score route, send GCS parameters to route
        and make sure it sends back score but not clinical risk.
        """
        # check if the route under test is actually present in the
        # Route Manager
        route_under_test = route_manager.get_route('calculate_obs_score')
        self.assertIsInstance(route_under_test, Route)

        # Create demo data
        demo_data = {
            'eyes': '4',
            'verbal': '5',
            'motor': '6',
            'startTimestamp': '0',
        }

        # Access the route
        test_resp = requests.post(
            '{0}{1}/observation/score/gcs/'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX
            ),
            data=demo_data,
            cookies=self.auth_resp.cookies
        )
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'score': {
                'score': 15
            },
            'modal_vals': {
                'next_action': 'json_patient_form_action',
                'title': 'Submit GCS score of 15',
                'content': '<p>Please confirm you want to submit '
                           'this score</p>'
            },
            'status': 3,
            'next_action': 'json_patient_form_action'
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Submit GCS score of 15',
                                 '<p>Please confirm you want to '
                                 'submit this score</p>',
                                 expected_json)

    def test_route_calculate_non_scoring_observation_score(self):
        """
        Test the 'calculate_obs_score' by submitting an observation
        that doesn't contribute to the score calculation.

        The route under test should return a 400 response.
        """
        # check if the route under test is actually present in the
        # Route Manager
        route_under_test = route_manager.get_route('calculate_obs_score')
        self.assertIsInstance(route_under_test, Route)

        # Create demo data
        demo_data = {
            'weight': '4',
            'startTimestamp': '0',
        }

        # Access the route
        test_resp = requests.post(
            '{0}{1}/observation/score/weight/'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX
            ),
            data=demo_data,
            cookies=self.auth_resp.cookies
        )
        self.assertEqual(test_resp.status_code, 400)
        self.assertEqual(test_resp.headers['content-type'], 'text/html')

    def test_route_json_partial_reasons(self):
        """
        Test the partial reasons route attribute of the EWS class
        (set in nh_observations).
        """
        # Check if the route under test is actually present into the
        # Route Manager
        route_under_test = route_manager.get_route('json_partial_reasons')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = route_under_test.url.replace('<observation>', 'ews')

        # Access the route
        test_resp = requests.get(
            '{0}{1}{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                url_under_test
            ),
            cookies=self.auth_resp.cookies
        )
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        ews_reg = self.registry('nh.clinical.patient.observation.ews')
        expected_json = ews_reg._partial_reasons
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Reason for partial observation',
                                 'Please state reason for submitting '
                                 'partial observation',
                                 expected_json)

    # Test Stand-in routes
    def test_route_share_patients(self):
        """
        Test that the 'json_share_patients' route returns
        a list of users who you've invited to follow your patients.
        """
        route_under_test = route_manager.get_route('json_share_patients')
        self.assertIsInstance(route_under_test, Route)

        def mock_nh_eobs_api_follow_invite(*args, **kwargs):
            return 2001

        # Get list of users to share with
        users_login_list = \
            TestOdooRouteDecoratorIntegration.mock_res_users_read()

        # Get a list of patients to share
        patient_list = TestOdooRouteDecoratorIntegration.mock_get_patients()

        # Create demo data
        demo_data = {
            'patient_ids': ','.join([str(p['id']) for p in patient_list]),
            'user_ids': ','.join([str(u['id']) for u in users_login_list])
        }

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        users_pool = self.registry('res.users')

        api_pool._patch_method('follow_invite', mock_nh_eobs_api_follow_invite)
        users_pool._patch_method(
            'read',
            TestOdooRouteDecoratorIntegration.mock_res_users_read
        )

        # Access the route
        test_resp = requests.post(
            '{0}{1}{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                route_under_test.url
            ),
            data=demo_data,
            cookies=self.auth_resp.cookies
        )

        # Stop Odoo's patchers
        api_pool._revert_method('follow_invite')
        users_pool._revert_method('read')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'],
                         'application/json')

        # Actual test
        expected_json = {
            'reason': 'An invite has been sent to follow the '
                      'selected patients.',
            'shared_with': ['John Smith', 'Jane Doe', 'Joe Average']
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Invitation sent',
                                 'An invite has been sent to follow '
                                 'the selected patients to: ',
                                 expected_json)

    def test_route_claim_patients(self):
        """Test the 'json_claim_patients' route.

        Sending a POST request with a list of patients' ids,
        the method under test should return a confirmation
        that you've taken those patients back.
        """
        route_under_test = route_manager.get_route('json_claim_patients')
        self.assertIsInstance(route_under_test, Route)

        # Set up the list of patients to claim back
        patient_list = TestOdooRouteDecoratorIntegration.mock_get_patients()

        # Create demo data
        demo_data = {
            'patient_ids': ','.join([str(p['id']) for p in patient_list])
        }

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method(
            'remove_followers',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )

        # Access the route
        test_resp = requests.post(
            '{0}{1}{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                route_under_test.url
            ),
            data=demo_data,
            cookies=self.auth_resp.cookies
        )

        # Stop Odoo's patchers
        api_pool._revert_method('remove_followers')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Actual test
        expected_json = {
            'reason': 'Followers removed successfully.'
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Patients claimed',
                                 'Followers removed successfully',
                                 expected_json)

    def test_route_colleagues_list(self):
        """
        Test that the 'json_colleagues_list' route returns
        a list of colleagues you can invite to follow your patients.
        """
        route_under_test = route_manager.get_route('json_colleagues_list')
        self.assertIsInstance(route_under_test, Route)

        def mock_get_share_users(*args, **kwargs):
            share_users_list = [
                {
                    'id': 33,
                    'patients': 12,
                    'name': 'John Smith'
                },
                {
                    'id': 34,
                    'patients': 2,
                    'name': 'Jane Doe'
                },
                {
                    'id': 35,
                    'patients': 9,
                    'name': 'Joe Average'
                }
            ]
            return share_users_list

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method('get_share_users', mock_get_share_users)

        # Access the route
        test_resp = requests.get(
            '{0}{1}{2}'.format(
                route_manager.BASE_URL,
                route_manager.URL_PREFIX,
                route_under_test.url
            ),
            cookies=self.auth_resp.cookies
        )

        # Stop Odoo's patchers
        api_pool._revert_method('get_share_users')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        expected_json = {
            'colleagues': mock_get_share_users()
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Colleagues on shift',
                                 'Choose colleagues for stand-in',
                                 expected_json)

    def test_route_invite_user(self):
        """
        Test patients you're invited to follow route,
        The method under test should return a list of patients and
        their activities.
        """
        route_under_test = route_manager.get_route('json_invite_patients')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/staff/invite/2001'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities',
             TestOdooRouteDecoratorIntegration.mock_get_assigned_activities),
            ('get_patients',
             TestOdooRouteDecoratorIntegration.mock_get_patients),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Access the url under test
        test_resp = requests.get(url_under_test,
                                 cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        methods_to_revert = [m[0] for m in methods_patching_list]
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Test that the response is correct
        expected_json = TestOdooRouteDecoratorIntegration.mock_get_patients()
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Patients shared with you',
                                 'These patients have been '
                                 'shared for you to follow',
                                 expected_json)

    def test_route_accept_user(self):
        """Test the route for accepting invitation to follow patient.

        The method under test should return the id of an activity and a 'true'
        status.
        """
        route_under_test = route_manager.get_route('json_accept_patients')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/staff/accept/2001'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities',
             TestOdooRouteDecoratorIntegration.mock_get_assigned_activities),
            ('complete',
             TestOdooRouteDecoratorIntegration.mock_method_returning_true),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Access the url under test
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        methods_to_revert = [m[0] for m in methods_patching_list]
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Test that the response is correct
        expected_json = {
            'id': 2001,
            'user': 'Nurse Nadine',
            'count': 3,
            'patient_ids': [1, 2, 3],
            'message': 'You have been invited to follow 3 patients '
                       'from Nurse Nadine',
            'status': True
            }

        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Successfully accepted stand-in invite',
                                 'You are following 3 patient(s) from '
                                 'Nurse Nadine',
                                 expected_json)

    def test_accept_user_route_manages_exceptn_while_completing_activity(self):
        """
        Test if the route for accepting invitation to follow
        patient manages exceptions.
        """
        route_under_test = route_manager.get_route('json_accept_patients')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/staff/accept/2001'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities',
             TestOdooRouteDecoratorIntegration.mock_get_assigned_activities),
            ('complete',
             TestOdooRouteDecoratorIntegration.
             mock_method_returning_osv_exception),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Access the url under test
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        methods_to_revert = [m[0] for m in methods_patching_list]
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Test that the response is correct
        expected_json = {'reason': 'Unable to complete the activity.'}

        self.check_response_json(test_resp, ResponseJSON.STATUS_ERROR,
                                 'Unable to accept stand-in invite',
                                 'An error occurred when trying to '
                                 'accept the stand-in invite',
                                 expected_json)

    def test_route_reject_user(self):
        """Test the route for rejecting invitation to follow patient.

        The method under test should return the id of an activity
        and a 'true' status.
        """
        route_under_test = route_manager.get_route('json_reject_patients')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/staff/reject/2001'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities',
             TestOdooRouteDecoratorIntegration.mock_get_assigned_activities),
            ('cancel',
             TestOdooRouteDecoratorIntegration.mock_method_returning_true),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Access the url under test
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        methods_to_revert = [m[0] for m in methods_patching_list]
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Test that the response is correct
        expected_json = {
            'id': 2001,
            'user': 'Nurse Nadine',
            'count': 3,
            'patient_ids': [1, 2, 3],
            'message': 'You have been invited to follow 3 patients from '
                       'Nurse Nadine',
            'status': True
            }

        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Successfully rejected stand-in invite',
                                 'You are not following 3 patient(s) from '
                                 'Nurse Nadine',
                                 expected_json)

    def test_reject_user_route_manages_except_while_cancelling_activity(self):
        """
        Test if the route for rejecting invitation to follow patient
        manages exceptions.
        """
        route_under_test = route_manager.get_route('json_reject_patients')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/staff/reject/2001'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Start Odoo's patchers
        eobs_api = self.registry['nh.eobs.api']
        methods_patching_list = [
            ('get_assigned_activities',
             TestOdooRouteDecoratorIntegration.mock_get_assigned_activities),
            ('cancel',
             TestOdooRouteDecoratorIntegration.
             mock_method_returning_osv_exception),
        ]
        self._bulk_patch_odoo_model_method(eobs_api, methods_patching_list)

        # Access the url under test
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        methods_to_revert = [m[0] for m in methods_patching_list]
        self._revert_bulk_patch_odoo_model_method(eobs_api, methods_to_revert)

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Test that the response is correct
        expected_json = {'reason': 'Unable to cancel the activity.'}

        self.check_response_json(test_resp, ResponseJSON.STATUS_ERROR,
                                 'Unable to reject stand-in invite',
                                 'An error occurred when trying to reject '
                                 'the stand-in invite',
                                 expected_json)

    # Test Task routes

    def test_take_task_route(self):
        """Test the 'json_take_task' route, supplying it correct data.

        The method under test should return a successful message.
        """
        route_under_test = route_manager.get_route('json_take_task')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/take_ajax/1002'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )
        auth_user_id = self.user_id

        def mock_nh_activity_read(*args, **kwargs):
            task_detail = {
                'id': 1002,
                'user_id': (auth_user_id, 'Test User')
            }
            return task_detail

        # Start Odoo's patchers
        activity_pool = self.registry('nh.activity')
        api_pool = self.registry('nh.eobs.api')
        activity_pool._patch_method('read', mock_nh_activity_read)
        api_pool._patch_method(
            'assign',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )

        # Access the route
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        activity_pool._revert_method('read')
        api_pool._revert_method('assign')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'reason': 'Task was free to take.'
        }
        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Task successfully taken',
                                 'You can now perform this task',
                                 expected_json)

    def test_take_task_route_with_exception_while_assigning_task(self):
        """Test the 'json_take_task' route, when an exception is raised
        while assigning the task.

        The method under test should return an error message.
        """
        route_under_test = route_manager.get_route('json_take_task')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/take_ajax/1002'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )
        auth_user_id = self.user_id

        def mock_nh_activity_read(*args, **kwargs):
            task_detail = {
                'id': 1002,
                'user_id': (auth_user_id, 'Test User')
            }
            return task_detail

        # Start Odoo's patchers
        activity_pool = self.registry('nh.activity')
        api_pool = self.registry('nh.eobs.api')
        activity_pool._patch_method('read', mock_nh_activity_read)
        api_pool._patch_method(
            'assign',
            TestOdooRouteDecoratorIntegration
                .mock_method_returning_osv_exception
        )

        # Access the route
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        activity_pool._revert_method('read')
        api_pool._revert_method('assign')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'reason': "Unable to assign to user."
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_ERROR,
                                 'Unable to take task',
                                 'An error occurred when trying '
                                 'to take the task',
                                 expected_json)

    def test_take_task_route_w_task_already_assigned_to_different_user(self):
        """Test the 'json_take_task' route, when the task is already
        assigned to a different user.

        The method under test should return a fail message.
        """
        route_under_test = route_manager.get_route('json_take_task')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/take_ajax/1002'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )
        different_user_id = int(self.user_id) + 1

        def mock_nh_activity_read(*args, **kwargs):
            task_detail = {
                'id': 1002,
                'user_id': (different_user_id, 'Test User')
            }
            return task_detail

        # Start Odoo's patchers
        activity_pool = self.registry('nh.activity')
        activity_pool._patch_method('read', mock_nh_activity_read)

        # Access the route
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        activity_pool._revert_method('read')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'reason': "Task assigned to another user."
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_FAIL,
                                 'Unable to take task',
                                 'This task is already assigned to '
                                 'another user',
                                 expected_json)

    def test_cancel_take_task_route(self):
        """Test the 'json_cancel_take_task' route, supplying it correct data.

        The method under test should return a successful message
        that says the task has been put back into the pool.
        """
        route_under_test = route_manager.get_route('json_cancel_take_task')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/cancel_take_ajax/2001'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )
        auth_user_id = self.user_id

        def mock_nh_activity_read(*args, **kwargs):
            task_detail = {
                'id': 1002,
                'user_id': (auth_user_id, 'Test User')
            }
            return task_detail

        # Start Odoo's patchers
        activity_pool = self.registry('nh.activity')
        api_pool = self.registry('nh.eobs.api')
        activity_pool._patch_method('read', mock_nh_activity_read)
        api_pool._patch_method(
            'unassign',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )

        # Access the route
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        activity_pool._revert_method('read')
        api_pool._revert_method('unassign')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'reason': 'Task was successfully unassigned from you.'
        }
        # Check the returned JSON data against the expected one
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Successfully released task',
                                 'The task has now been released '
                                 'back into the task pool',
                                 expected_json)

    def test_cancel_take_task_route_with_except_while_unassigning_task(self):
        """Test the 'json_cancel_take_task' route, when an exception
        is raised while unassigning the task.

        This case occurs, for example, when trying to unassign a
        task that is already unassigned.
        The method under test should return an error message.
        """
        route_under_test = route_manager.get_route('json_cancel_take_task')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/cancel_take_ajax/2001'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )
        auth_user_id = self.user_id

        def mock_nh_activity_read(*args, **kwargs):
            task_detail = {
                'id': 1002,
                'user_id': (auth_user_id, 'Test User')
            }
            return task_detail

        # Start Odoo's patchers
        activity_pool = self.registry('nh.activity')
        api_pool = self.registry('nh.eobs.api')
        activity_pool._patch_method('read', mock_nh_activity_read)
        api_pool._patch_method(
            'unassign',
            TestOdooRouteDecoratorIntegration
                .mock_method_returning_osv_exception
        )

        # Access the route
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        activity_pool._revert_method('read')
        api_pool._revert_method('unassign')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'reason': 'Unable to unassign task.'
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_ERROR,
                                 'Unable to release task',
                                 'An error occurred when trying to '
                                 'release the task back into the task pool',
                                 expected_json)

    def test_cancel_take_route_with_task_assigned_to_different_user(self):
        """Test the 'json_cancel_take_task' route when the task is
        assigned to a different user.

        The method under test should return a fail message.
        """
        route_under_test = route_manager.get_route('json_cancel_take_task')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/cancel_take_ajax/1002'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )
        different_user_id = int(self.user_id) + 1

        def mock_nh_activity_read(*args, **kwargs):
            task_detail = {
                'id': 1002,
                'user_id': (different_user_id, 'Test User')
            }
            return task_detail

        # Start Odoo's patchers
        activity_pool = self.registry('nh.activity')
        activity_pool._patch_method('read', mock_nh_activity_read)

        # Access the route
        test_resp = requests.post(url_under_test,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        activity_pool._revert_method('read')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'reason': "Can't cancel other user's task."
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_FAIL,
                                 'Unable to release task',
                                 'The task you are trying to release '
                                 'is being carried out by another user',
                                 expected_json)

    def test_route_task_form_action(self):
        """Test the form submission route (task side).

        The method under test should return a successful status
        and a list of activities to carry out.
        """
        route_under_test = route_manager.get_route('json_task_form_action')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/submit_ajax/ews/1605'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Test demo for EWS observation.
        # (Supplying specific data which result in an EWS total score
        # less than 4 (according to the default EWS policy).
        # This way, no related tasks are created - does not really matter,
        # due to mocking every Odoo's models calling.
        demo_data = {
            'respiration_rate': 18,
            'indirect_oxymetry_spo2': 100,
            'oxygen_administration_flag': False,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 80,
            'avpu_text': 'A',
            'taskId': 1605,
            'startTimestamp': 0
        }

        def mock_method_returning_converter_function(*args, **kwargs):
            """
            The converter function just returns the same data dictionary
            sent via POST request to the route.
            """
            def converter(*args, **kwargs):
                return demo_data
            return converter

        def mock_method_returning_list_of_ids(*args, **kwargs):
            return [123, 456, 789]

        def mock_method_returning_list_of_activities(*args, **kwargs):
            activities_list = [
                {
                    'id': 123,
                    'data_model': 'nh.clinical.patient.observation.ews',
                    'state': 'new'
                },
                {
                    'id': 456,
                    'data_model': 'nh.clinical.notification.frequency',
                    'state': 'scheduled'
                },
                {
                    'id': 789,
                    'data_model': 'nh.clinical.notification.assessment',
                    'state': 'completed'
                },
            ]
            return activities_list

        # Start Odoo's patchers
        activity_pool = self.registry('nh.activity')
        api_pool = self.registry('nh.eobs.api')
        ir_fields_converter = self.registry('ir.fields.converter')

        activity_pool._patch_method(
            'search',
            mock_method_returning_list_of_ids
        )
        activity_pool._patch_method('read',
                                    mock_method_returning_list_of_activities)
        api_pool._patch_method(
            'complete',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )
        api_pool._patch_method(
            'check_activity_access',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )
        ir_fields_converter._patch_method(
            'for_model',
            mock_method_returning_converter_function
        )

        # Access the route
        test_resp = requests.post(url_under_test,
                                  data=demo_data,
                                  cookies=self.auth_resp.cookies
                                  )

        # Stop Odoo's patchers
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        api_pool._revert_method('complete')
        api_pool._revert_method('check_activity_access')
        ir_fields_converter._revert_method('for_model')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'related_tasks': [
                {
                    'id': 456,
                    'data_model': 'nh.clinical.notification.frequency',
                    'state': 'scheduled'
                }
            ],
            'status': 1
        }

        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Successfully Submitted NEWS Observation',
                                 'Here are related tasks based on the '
                                 'observation',
                                 expected_json)

    def test_route_confirm_notification(self):
        """Test the confirmation submission for notifications.

        The method under test should return a successful status
        and a list of activities to carry out.
        """
        route_under_test = route_manager.get_route(
            'confirm_clinical_notification'
        )
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/confirm_clinical/5061'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Access the route
        demo_data = {
            'taskId': 5061
        }

        def mock_method_returning_list_of_ids(*args, **kwargs):
            return [123, 456, 789]

        def mock_method_returning_list_of_activities(*args, **kwargs):
            activities_list = [
                {
                    'id': 123,
                    'data_model': 'nh.clinical.patient.observation.ews'
                },
                {
                    'id': 456,
                    'data_model': 'nh.clinical.notification.frequency'
                },
                {
                    'id': 789,
                    'data_model': 'nh.clinical.notification.assessment'
                },
            ]
            return activities_list

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        activity_pool = self.registry('nh.activity')

        activity_pool._patch_method(
            'search',
            mock_method_returning_list_of_ids
        )
        activity_pool._patch_method(
            'read',
            mock_method_returning_list_of_activities
        )
        api_pool._patch_method(
            'complete',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )
        api_pool._patch_method(
            'check_activity_access',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )

        test_resp = requests.post(url_under_test,
                                  data=demo_data,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        api_pool._revert_method('complete')
        api_pool._revert_method('check_activity_access')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'related_tasks': [
                {
                    'id': 456,
                    'data_model': 'nh.clinical.notification.frequency'
                },
                {
                    'id': 789,
                    'data_model': 'nh.clinical.notification.assessment'
                },
            ],
            'status': 1
        }

        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Submission successful',
                                 'The notification was successfully submitted',
                                 expected_json)

    def test_19_route_cancel_notification(self):
        """Test the cancel submission for notifications.

        The method under test should return a successful status
        without any other activities to carry out.
        """
        route_under_test = route_manager.get_route(
            'cancel_clinical_notification'
        )
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/cancel_clinical/5061'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        demo_data = {
            'reason': 1
        }

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method(
            'cancel',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )

        test_resp = requests.post(url_under_test,
                                  data=demo_data,
                                  cookies=self.auth_resp.cookies
                                  )

        # Stop Odoo's patchers
        api_pool._revert_method('cancel')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'related_tasks': [],
            'status': 4
        }

        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Cancellation successful',
                                 'The notification was successfully cancelled',
                                 expected_json)

    def test_route_cancel_notification_manages_exceptn_while_cancelling(self):
        """
        Test if the route for cancelling notifications manages exceptions.
        """
        route_under_test = route_manager.get_route(
            'cancel_clinical_notification'
        )
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/tasks/cancel_clinical/5061'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        demo_data = {
            'reason': 1
        }

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method(
            'cancel',
            TestOdooRouteDecoratorIntegration
                .mock_method_returning_osv_exception
        )

        test_resp = requests.post(url_under_test,
                                  data=demo_data,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        api_pool._revert_method('cancel')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'error': 'The server returned an error while trying '
                     'to cancel the task.'
        }

        self.check_response_json(test_resp, ResponseJSON.STATUS_ERROR,
                                 'Cancellation unsuccessful',
                                 'Unable to cancel the notification',
                                 expected_json)

    def test_route_task_cancellation_options(self):
        """Test the route to get the task cancellation options.

        The method under test should return a list of task cancellation options
        """
        route_under_test = route_manager.get_route(
            'ajax_task_cancellation_options'
        )
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}{2}'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX,
            route_under_test.url
        )

        def mock_method_returning_cancel_reasons_list(*args, **kwargs):
            cancel_reasons_list = [
                {
                    'name': 'Cancelled by Ward Manager',
                    'system': True
                },
                {
                    'name': 'Cancelled by System',
                    'system': True
                },
                {
                    'name': 'Already Done',
                    'system': False
                },
                {
                    'name': 'No need to do this task',
                    'system': False
                }
            ]
            return cancel_reasons_list

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method(
            'get_cancel_reasons',
            mock_method_returning_cancel_reasons_list
        )

        test_resp = requests.get(url_under_test,
                                 cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        api_pool._revert_method('get_cancel_reasons')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = mock_method_returning_cancel_reasons_list()

        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Reason for cancelling task?',
                                 'Please state reason for cancelling task',
                                 expected_json)

    # Test Patient routes

    def test_route_patient_info(self):
        """
        Test the route to get patient information.

        The method under test should return a dictionary
        with information on the patient.
        """
        route_under_test = route_manager.get_route('json_patient_info')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/patient/info/2'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method(
            'get_patients',
            TestOdooRouteDecoratorIntegration.mock_get_patients
        )

        test_resp = requests.get(url_under_test,
                                 cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        api_pool._revert_method('get_patients')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = \
            TestOdooRouteDecoratorIntegration.mock_get_patients()[0]

        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Campbell, Bruce',
                                 'Information on Campbell, Bruce',
                                 expected_json)

    def test_patient_info_route_with_not_existing_id(self):
        """Test the route to get information about a patient not in the system.

        To simulate a wrong ID number (i.e. not related to any patient),
        the method that returns a list of patients is replaced
        with a mock object that returns an empty list.
        The method under test should return an error message.
        """
        route_under_test = route_manager.get_route('json_patient_info')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/patient/info/4'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        def mock_get_empty_patients_list(*args, **kwargs):
            return []

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method('get_patients', mock_get_empty_patients_list)

        test_resp = requests.get(url_under_test,
                                 cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        api_pool._revert_method('get_patients')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        expected_json = {
            'error': 'Patient not found.'
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_ERROR,
                                 'Patient not found',
                                 'Unable to get patient with ID provided',
                                 expected_json)

    def test_route_patient_barcode(self):
        """
        Test the route to get patient info when sending a hospital number
        from a barcode.

        The method under test should return a dictionary
        with information on the patient.
        """
        route_under_test = route_manager.get_route('json_patient_barcode')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/patient/barcode/1234567'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        def mock_get_patient_info(*args, **kwargs):
            patient_info = [
                {
                    'activities': [],
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
                }
            ]
            return patient_info

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method('get_patient_info', mock_get_patient_info)

        test_resp = requests.get(url_under_test,
                                 cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        api_pool._revert_method('get_patient_info')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = mock_get_patient_info()[0]

        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Campbell, Bruce',
                                 'Information on Campbell, Bruce',
                                 expected_json)

    def test_patient_barcode_route_with_invalid_hospital_number(self):
        """
        Test the route to get patient information when sending an invalid
        hospital number from a barcode.

        To simulate an invalid hospital number,
        the method that returns the patient info is replaced
        with a mock object that raises an exception.

        The method under test should return an error message.
        """
        route_under_test = route_manager.get_route('json_patient_barcode')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/patient/barcode/1234567'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method(
            'get_patient_info',
            TestOdooRouteDecoratorIntegration
                .mock_method_returning_osv_exception
        )

        # Access the route
        test_resp = requests.get(url_under_test,
                                 cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        api_pool._revert_method('get_patient_info')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'error': 'Patient not found.'
        }

        self.check_response_json(test_resp, ResponseJSON.STATUS_ERROR,
                                 'Patient not found',
                                 'Unable to get patient with ID provided',
                                 expected_json)

    def test_route_patient_obs(self):
        """
        Test the route to get the observation data for a patient.

        The method under test should return an array of dictionaries
        with the observations.
        """
        route_under_test = route_manager.get_route('ajax_get_patient_obs')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/patient/ajax_obs/2'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        def mock_get_activities_for_patient(*args, **kwargs):
            activities_list = [
                {
                    'activity_id': (23, 'NEWS Observation'),
                    'date_terminated': '2010-12-25 08:00:00',
                },
                {
                    'activity_id': (24, 'NEWS Observation'),
                    'create_date': '2011-02-15 18:00:30',
                },
                {
                    'activity_id': (25, 'NEWS Observation'),
                    'write_date': '2011-12-25 11:00:40',
                    'date_started': '2007-12-02 08:13:03'
                },
                {
                    'activity_id': (26, 'NEWS Observation'),
                    'clinical_risk': 'Low'
                }
            ]
            return activities_list

        # Start Odoo's patchers
        api_pool = self.registry('nh.eobs.api')
        api_pool._patch_method(
            'get_patients',
            TestOdooRouteDecoratorIntegration.mock_get_patients
        )
        api_pool._patch_method(
            'get_activities_for_patient',
            mock_get_activities_for_patient
        )

        # Access the route
        test_resp = requests.get(url_under_test,
                                 cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        api_pool._revert_method('get_patients')
        api_pool._revert_method('get_activities_for_patient')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'obs': mock_get_activities_for_patient(),
            'obsType': 'ews'
        }

        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Campbell, Bruce',
                                 'Observations for Campbell, Bruce',
                                 expected_json)

    def test_route_patient_form_action(self):
        """
        Test the route to submit an observation via the patient form.

        The method under test should return a successful message
        and a list of IDs of other activities to carry out.
        """
        route_under_test = route_manager.get_route('json_patient_form_action')
        self.assertIsInstance(route_under_test, Route)
        url_under_test = '{0}{1}/patient/submit_ajax/ews/2'.format(
            route_manager.BASE_URL,
            route_manager.URL_PREFIX
        )

        # test demo for ews observation
        # supplying specific data which result in an EWS total score less
        # than 4 (according to the default EWS policy)
        # this way, no related tasks are created
        demo_data = {
            'respiration_rate': 18,
            'indirect_oxymetry_spo2': 100,
            'oxygen_administration_flag': False,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 80,
            'avpu_text': 'A',
            'startTimestamp': 0
        }

        def mock_method_returning_converter_function(*args, **kwargs):
            """
            The converter function just returns the same data dictionary
            sent via POST request to the route.
            """
            def converter(*args, **kwargs):
                return demo_data
            return converter

        def mock_method_returning_list_of_ids(*args, **kwargs):
            return [123, 456, 789]

        def mock_method_returning_list_of_activities(*args, **kwargs):
            activities_list = [
                {
                    'id': 123,
                    'data_model': 'nh.clinical.patient.observation.ews',
                    'state': 'new'
                },
                {
                    'id': 456,
                    'data_model': 'nh.clinical.notification.frequency',
                    'state': 'scheduled'
                },
                {
                    'id': 789,
                    'data_model': 'nh.clinical.notification.assessment',
                    'state': 'completed'
                },
            ]
            return activities_list

        def mock_create_activity_for_patient(*args, **kwargs):
            return 444

        # Start Odoo's patchers
        activity_pool = self.registry('nh.activity')
        api_pool = self.registry('nh.eobs.api')
        ir_fields_converter = self.registry('ir.fields.converter')

        activity_pool._patch_method(
            'search',
            mock_method_returning_list_of_ids
        )
        activity_pool._patch_method(
            'read',
            mock_method_returning_list_of_activities
        )
        api_pool._patch_method(
            'complete',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )
        api_pool._patch_method(
            'create_activity_for_patient',
            mock_create_activity_for_patient
        )
        api_pool._patch_method(
            'check_activity_access',
            TestOdooRouteDecoratorIntegration.mock_method_returning_true
        )
        ir_fields_converter._patch_method(
            'for_model',
            mock_method_returning_converter_function
        )

        # Access the route
        test_resp = requests.post(url_under_test,
                                  data=demo_data,
                                  cookies=self.auth_resp.cookies)

        # Stop Odoo's patchers
        activity_pool._revert_method('search')
        activity_pool._revert_method('read')
        api_pool._revert_method('complete')
        api_pool._revert_method('create_activity_for_patient')
        api_pool._revert_method('check_activity_access')
        ir_fields_converter._revert_method('for_model')

        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'related_tasks': [
                {
                    'id': 456,
                    'data_model': 'nh.clinical.notification.frequency',
                    'state': 'scheduled'
                }
            ],
            'status': 1
        }

        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Successfully Submitted NEWS Observation',
                                 'Here are related tasks based on the '
                                 'observation',
                                 expected_json)
