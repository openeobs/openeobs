__author__ = 'lorenzo'
import json
import logging
import openerp.tests
import requests
from openerp.addons.nh_eobs_api.routing import Route, RouteManager, ResponseJSON
from openerp.addons.nh_eobs_api.controllers.route_api import route_manager
from openerp.tests import DB as DB_NAME
from random import choice as random_choice
from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import datetime

test_logger = logging.getLogger(__name__)


class TestOdooRouteDecoratorIntegration(openerp.tests.common.HttpCase):

    json_response_structure_keys = ['status', 'title', 'description', 'data']

    def _get_user_belonging_to_group(self, group_name):
        """Get the 'login' name of a user belonging to a specific group.

        :param group_name: A string with the name of the group from which retrieve a user (belonging to it)
        :return: A string with the 'login' of the user belonging to the group passed as argument (or None if there isn't any user belonging to that group)
        """
        users_pool = self.registry['res.users']
        #users_login_list = users_pool.search_read(self.cr, self.uid,
        #                                          domain=[('groups_id.name', '=', group_name)],
        #                                          fields=['login'])
        #login_name = random_choice(users_login_list).get('login')
        login_name = 'norah'
        login_uid = users_pool.search(self.cr, self.uid, [['login', '=', login_name]])
        if login_uid:
            self.auth_uid = login_uid[0]
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

    def check_response_json(self, resp, status, title, description, data):
        """Test the response JSON for correct status, title, desc and data values

        :param resp: Raw response from requests
        :param status: The expected status code for the response
        :param title: The title to be shown on the popup on Frontend
        :param description: The description to be used in the popup on Frontend
        :param data: Data the be sent to the Frontend to show in popup
        :return: True cos the tests will cause the thing to fail anyways
        """
        returned_json = json.loads(resp.text)
        for k in self.json_response_structure_keys:
            self.assertIn(k, returned_json)

        self.assertEqual(returned_json['status'], status)
        self.assertEqual(returned_json['title'], title)
        self.assertEqual(returned_json['description'], description)
        returned_data = json.dumps(returned_json['data'])
        json_data = json.dumps(data)
        self.assertEqual(json.loads(returned_data), json.loads(json_data))
        return True

    def setUp(self):
        """Get an authenticated response from the server so we can half-inch the session cookie for subsequent calls

        """
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

    # Test Observation based routes
    def test_01_route_calculate_ews_score(self):
        """Test the EWS score route, send EWS parameters to route and make
        sure it sends back score
        :return:
        """
        # check if the route under test is actually present in the Route Manager
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
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/observation/score/ews/',
                                  data=json.dumps(demo_data),
                                  cookies=self.auth_resp.cookies)
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
                'title': 'Submit NEWS of 3',
                'content': '<p><strong>Clinical risk: Medium</strong></p><p>Please confirm you want to submit this score</p>'
            }
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Submit NEWS of 3',
                                 '<p><strong>Clinical risk: Medium</strong></p><p>Please confirm you want to submit this score</p>',
                                 expected_json)

    def test_02_route_calculate_gcs_score(self):
        """ Test the GCS score route, send GCS parameters to route and make sure
        it sends back score but not clinical risk
        :return:
        """
        # check if the route under test is actually present in the Route Manager
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
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/observation/score/gcs/',
                                  data=json.dumps(demo_data),
                                  cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'score': {
                'score': 15
            },
            'modal_vals': {
                'next_action': 'json_patient_form_action',
                'title': 'Submit GCS of 15',
                'content': '<p>Please confirm you want to submit this score</p>'
            }
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Submit GCS of 15',
                                 '<p>Please confirm you want to submit this score</p>',
                                 expected_json)

    def test_03_route_calculate_non_scoring_observation_score(self):
        """ Test the GCS score route, send GCS parameters to route and make sure
        it sends back score but not clinical risk
        :return:
        """
        # check if the route under test is actually present in the Route Manager
        route_under_test = route_manager.get_route('calculate_obs_score')
        self.assertIsInstance(route_under_test, Route)

        # Create demo data
        demo_data = {
            'weight': '4',
            'startTimestamp': '0',
        }

        # Access the route
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/observation/score/weight/',
                                  data=json.dumps(demo_data),
                                  cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 400)
        self.assertEqual(test_resp.headers['content-type'], 'text/html')

    def test_04_route_json_partial_reasons(self):
        """ Test the partial reasons route attribute of the EWS class
        (set in nh_observations)
        :return:
        """
        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_partial_reasons')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.get(route_manager.BASE_URL + route_manager.URL_PREFIX + route_under_test.url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        expected_json = self.registry('nh.clinical.patient.observation.ews')._partial_reasons
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Reason for partial observation',
                                 'Please select an option from the list',
                                 expected_json)

    # Test Stand-in routes
    def test_05_route_share_patients(self):
        """ Test the share patients route, a post request with user_ids and
        patient_ids should return a list of users who you've invited to
        follow your patients
        :return:
        """
        # get list of users to share with
        users_pool = self.registry['res.users']
        users_login_list = users_pool.search_read(self.cr, self.uid,
                                                  domain=[('groups_id.name', '=', 'NH Clinical Nurse Group'),
                                                          ('id', 'not in', [self.uid, self.auth_uid])],
                                                  fields=['login', 'display_name'])[:3]
        # get list of patients to share
        api_pool = self.registry('nh.eobs.api')
        patient_list = api_pool.get_patients(self.cr, self.auth_uid, [])[:3]
        patient_ids = [p['id'] for p in patient_list]
        # check if the route under test is actually present in the Route Manager
        route_under_test = route_manager.get_route('json_share_patients')
        self.assertIsInstance(route_under_test, Route)

        # Create demo data
        demo_data = {
            'patient_ids': ','.join([str(p['id']) for p in patient_list]),
            'user_ids': ','.join([str(u['id']) for u in users_login_list])
        }

        # Access the route
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + route_under_test.url,
                                  data=json.dumps(demo_data),
                                  cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # actual test
        expected_json = {
            'reason': 'An invite has been sent to follow the selected patients.',
            'shared_with': [user['display_name'] for user in users_login_list]
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Invitation sent',
                                 'An invite has been sent to follow the selected patients',
                                 expected_json)

        return api_pool.remove_followers(self.cr, self.auth_uid, patient_ids)

    def test_06_route_claim_patients(self):
        """ Test the claim patients route, a post request with patient_ids
        should return a confirmation that you've taken those patients back
        :return:
        """
        api_pool = self.registry('nh.eobs.api')
        # set up the list of patients to claim
        users_pool = self.registry['res.users']
        users_login_list = users_pool.search_read(self.cr, self.uid,
                                                  domain=[('groups_id.name', '=', 'NH Clinical Nurse Group'),
                                                          ('id', 'not in', [self.uid, self.auth_uid])],
                                                  fields=['login'])[:3]
        patient_list = api_pool.get_patients(self.cr, self.auth_uid, [])[:3]
        patient_ids = [p['id'] for p in patient_list]
        for user_id in users_login_list:
            api_pool.follow_invite(self.cr, self.auth_uid, patient_ids, user_id['id'])

        # check if the route under test is actually present in the Route Manager
        route_under_test = route_manager.get_route('json_claim_patients')
        self.assertIsInstance(route_under_test, Route)

        # Create demo data
        demo_data = {
            'patient_ids': ','.join([str(p['id']) for p in patient_list])
        }

        # Access the route
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + route_under_test.url,
                                  data=json.dumps(demo_data),
                                  cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # actual test
        expected_json = {
            'reason': 'Followers removed successfully.'
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Patients claimed',
                                 'Followers removed successfully',
                                 expected_json)

    def test_07_route_colleagues_list(self):
        """ Test the colleagues list route, should return a list of colleagues
        you can invite to follow your patients
        :return:
        """
        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_colleagues_list')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.get(route_manager.BASE_URL + route_manager.URL_PREFIX + route_under_test.url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        expected_json = self.registry('nh.eobs.api').get_share_users(self.cr, self.auth_uid)
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Colleagues on shift',
                                 'Choose colleagues for stand-in',
                                 expected_json)

    def test_08_route_invite_user(self):
        """ Test patients you're invited to follow route, should return a list
        of patients that you've been invited to follow and their activities
        :return:
        """
    #     cr, uid = self.cr, self.uid
    #     # Set up the invited user list
    #     api_pool = self.registry('nh.eobs.api')
    #     users_pool = self.registry['res.users']
    #
    #     other_login = users_pool.search_read(cr, uid,
    #                                          domain=[('groups_id.name', '=', 'NH Clinical Nurse Group'),
    #                                                  ('id', 'not in', [uid, self.auth_uid])],
    #                                          fields=['login'])[0]
    #
    #     resp_all_pool = self.registry['nh.clinical.user.responsibility.allocation']
    #     activity_pool = self.registry['nh.activity']
    #     location_pool = self.registry['nh.clinical.location']
    #     demo_patient_list = api_pool.get_patients(cr, self.auth_uid, [])[:3]
    #     location_ids = location_pool.search(cr, uid, [['name', 'in', [l['location'] for l in demo_patient_list]]])
    #     resp_act = resp_all_pool.create_activity(cr, uid, {}, {
    #         'responsible_user_id': other_login['id'],
    #         'location_ids': [[6, 0, location_ids]]
    #     })
    #     activity_pool.complete(cr, uid, resp_act)
    #     patient_list = api_pool.get_patients(cr, other_login['id'], [])[:3]
    #     patient_ids = [p['id'] for p in patient_list]
    #     follow_act_id = api_pool.follow_invite(cr, other_login['id'], patient_ids, self.auth_uid)
    #
    #     # check if the route under test is actually present in the Route Manager
    #     route_under_test = route_manager.get_route('json_invite_patients')
    #     self.assertIsInstance(route_under_test, Route)
    #
    #     # Access the route
    #     url = route_manager.BASE_URL + route_manager.URL_PREFIX + '/staff/invite/' + str(follow_act_id)
    #     test_resp = requests.get(url, cookies=self.auth_resp.cookies)
    #     self.assertEqual(test_resp.status_code, 200)
    #     self.assertEqual(test_resp.headers['content-type'], 'application/json')
    #
    #     # actual test
    #     expected_json = patient_list
    #     self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
    #                              'Patients shared with you',
    #                              'These patients have been shared for you to follow',
    #                              [])
    #
    #     return api_pool.remove_followers(cr, other_login['id'], patient_ids)
        self.assertEqual(False, True, 'Test currently not working due to inability to create concurrent sessions')

    def test_09_route_accept_user(self):
        """ Test accept invitation to follow patient route, should return an id
        of an activity and a true status
        :return:
        """
        self.assertEqual(False, True, 'Test not implemented due issue with test 06')

    def test_10_route_reject_user(self):
        """ Test rejection of invitation to follow patient route, should return
        an activity id and a true status
        :return:
        """
        self.assertEqual(False, True, 'Test not implemented due issue with test 06')


    # Test Task routes

    def test_11_route_take_task(self):
        """ Test the take task route, Depending on the elligability to take the
        task should return a status or an error
        :return:
        """
        api_pool = self.registry('nh.eobs.api')
        task = api_pool.get_activities(self.cr, self.auth_uid, [])[0]

        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_take_task')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/tasks/take_ajax/' + str(task['id']), cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'reason': 'Task was free to take'
        }
        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Task successfully taken',
                                 'You can now perform this task',
                                 expected_json)
        try:
            api_pool.unassign(self.cr, self.auth_uid, task['id'])
        except Exception:
            test_logger.info('test_09 seeems to have been unable to unassign task, potential nh.eobs.api issue?')

    def test_12_route_cancel_take_task(self):
        """ Test the cancel take task route, Should return a status to say have
        put the task back into the pool
        :return:
        """
        api_pool = self.registry('nh.eobs.api')
        task = api_pool.get_activities(self.cr, self.auth_uid, [])[0]

        # Take a task
        route_under_test = route_manager.get_route('json_take_task')
        self.assertIsInstance(route_under_test, Route)
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/tasks/take_ajax/' + str(task['id']), cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')
        expected_json = {
            'reason': 'Task was free to take'
        }
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Task successfully taken',
                                 'You can now perform this task',
                                 expected_json)

        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_cancel_take_task')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/tasks/cancel_take_ajax/' + str(task['id']), cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'reason': 'Task was successfully unassigned from you'
        }
        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Successfully released task',
                                 'The task has now been released back into the task pool',
                                 expected_json)

    def test_13_route_task_form_action(self):
        """ Test the form submission route (task side), Should return a status
        and other activities to carry out
        :return:
        """
        # api_pool = self.registry('nh.eobs.api')
        # tasks = api_pool.get_activities(self.cr, self.auth_uid, [])
        # task = [t for t in tasks if t['summary'] == 'NEWS Observation'][0]
        #
        # # test demo for ews observation
        # demo_data = {
        #     'respiration_rate': 40,
        #     'indirect_oxymetry_spo2': 100,
        #     'oxygen_administration_flag': False,
        #     'body_temperature': 37.5,
        #     'blood_pressure_systolic': 120,
        #     'blood_pressure_diastolic': 80,
        #     'pulse_rate': 80,
        #     'avpu_text': 'A',
        #     'taskId': task['id'],
        #     'startTimestamp': 0
        # }
        #
        # # Check if the route under test is actually present into the Route Manager
        # route_under_test = route_manager.get_route('json_task_form_action')
        # self.assertIsInstance(route_under_test, Route)
        #
        # # Access the route
        # test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/tasks/submit_ajax/ews/' + str(task['id']),
        #                           data=json.dumps(demo_data),
        #                           cookies=self.auth_resp.cookies)
        # self.assertEqual(test_resp.status_code, 200)
        # self.assertEqual(test_resp.headers['content-type'], 'application/json')
        #
        # expected_json = {
        #     'related_tasks': []
        # }
        #
        # self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
        #                          'Observation successfully submitted',
        #                          'Here are related tasks based on the observation',
        #                          expected_json)
        self.assertEqual(False, True, 'Test currently not working due to bug after submitting observation')

    def test_14_route_confirm_notification(self):
        """ Test the confirmation submission for notifications, should return a
        status and other activities to carry out
        :return:
        """
        # api_pool = self.registry('nh.eobs.api')
        # activity_api = self.registry('nh.activity')
        # tasks = api_pool.get_activities(self.cr, self.auth_uid, [])
        # task = [t for t in tasks if t['summary'] in ['Assess Patient', 'Urgently inform medical team', 'Immediately inform medical team']][0]
        # #
        # # Check if the route under test is actually present into the Route Manager
        # route_under_test = route_manager.get_route('confirm_clinical_notification')
        # self.assertIsInstance(route_under_test, Route)
        #
        # # Access the route
        # demo_data = {
        #     'taskId': task['id']
        # }
        # test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/tasks/confirm_clinical/' + str(task['id']),
        #                           data=json.dumps(demo_data),
        #                           cookies=self.auth_resp.cookies)
        # self.assertEqual(test_resp.status_code, 200)
        # self.assertEqual(test_resp.headers['content-type'], 'application/json')
        #
        # triggered_ids = activity_api.search(self.cr, self.auth_uid, [['creator_id', '=', task['id']]])
        # triggered_tasks = activity_api.read(self.cr, self.auth_uid, triggered_ids, [])
        # triggered_tasks = [v for v in triggered_tasks if 'ews' not in v['data_model'] and api_pool.check_activity_access(self.cr, self.auth_uid, v['id'])]
        #
        # expected_json = {
        #     'related_tasks': triggered_tasks
        # }
        #
        # self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
        #                          'Submission successful',
        #                          'The notification was successfully submitted',
        #                          expected_json)
        self.assertEqual(False, True, 'Test currently not working due to not being able to get triggered tasks to assert against')

    def test_15_route_cancel_notification(self):
        """ Test the cancel submission for notifications, should return a status
        and other activities to carry out
        :return:
        """
        api_pool = self.registry('nh.eobs.api')
        activity_api = self.registry('nh.activity')
        tasks = api_pool.get_activities(self.cr, self.auth_uid, [])
        task = [t for t in tasks if t['summary'] in ['Assess Patient', 'Urgently inform medical team', 'Immediately inform medical team']][0]
        #
        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('cancel_clinical_notification')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        demo_data = {
            'reason': 1
        }
        test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/tasks/cancel_clinical/' + str(task['id']),
                                  data=json.dumps(demo_data),
                                  cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = {
            'related_tasks': []
        }

        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Cancellation successful',
                                 'The notification was successfully cancelled',
                                 expected_json)
        # self.assertEqual(False, True, 'Test currently not working due to not being able to get triggered tasks to assert against')

    def test_16_route_task_cancellation_options(self):
        """ Test the route to get the task cancellation options, should return
        a list of task cancellation options
        :return:
        """
        api_pool = self.registry('nh.eobs.api')

        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('ajax_task_cancellation_options')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.get(route_manager.BASE_URL + route_manager.URL_PREFIX + route_under_test.url, cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        expected_json = api_pool.get_cancel_reasons(self.cr, self.auth_uid)
        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 'Reason for cancelling task?',
                                 'Please select an option from the dropdown',
                                 expected_json)

    # Test Patient routes

    def test_17_route_patient_info(self):
        """ Test the route to get patient information, should return a dict of
        information on the patient
        :return:
        """
        api_pool = self.registry('nh.eobs.api')
        patient = api_pool.get_patients(self.cr, self.auth_uid, [])[0]

        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_patient_info')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.get(route_manager.BASE_URL + route_manager.URL_PREFIX + '/patient/info/' + str(patient['id']), cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 '{0}'.format(patient['full_name']),
                                 'Information on {0}'.format(patient['full_name']),
                                 patient)

    def test_18_route_patient_barcode(self):
        """ Test the route to get patient information when sent a hospital no
        from a barcode, should return a dict of information on the patient
        :return:
        """
        api_pool = self.registry('nh.eobs.api')
        patient = api_pool.get_patients(self.cr, self.auth_uid, [])[0]

        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('json_patient_barcode')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.get(route_manager.BASE_URL + route_manager.URL_PREFIX + '/patient/barcode/' + str(patient['other_identifier']), cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        patient_info = api_pool.get_patient_info(self.cr, self.auth_uid, [patient['other_identifier']])[0]
        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 '{0}'.format(patient['full_name']),
                                 'Information on {0}'.format(patient['full_name']),
                                 patient_info)

    def test_19_route_patient_obs(self):
        """ Test the route to get the observation data for a patient, should
        return an array of dictionaries with the observations
        :return:
        """
        api_pool = self.registry('nh.eobs.api')
        patient = api_pool.get_patients(self.cr, self.auth_uid, [])[0]

        # Check if the route under test is actually present into the Route Manager
        route_under_test = route_manager.get_route('ajax_get_patient_obs')
        self.assertIsInstance(route_under_test, Route)

        # Access the route
        test_resp = requests.get(route_manager.BASE_URL + route_manager.URL_PREFIX + '/patient/ajax_obs/' + str(patient['id']), cookies=self.auth_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertEqual(test_resp.headers['content-type'], 'application/json')

        ews = api_pool.get_activities_for_patient(self.cr, self.auth_uid, patient_id=int(patient['id']), activity_type='ews')
        for ew in ews:
            for e in ew:
                if e in ['date_terminated', 'create_date', 'write_date', 'date_started']:
                    ew[e] = fields.datetime.context_timestamp(self.cr, self.auth_uid, datetime.strptime(ew[e], DTF)).strftime(DTF)

        expected_json = {
            'obs': ews,
            'obsType': 'ews'
        }
        # Check the returned JSON data against the expected ones
        self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
                                 '{0}'.format(patient['full_name']),
                                 'Observations for {0}'.format(patient['full_name']),
                                 expected_json)

    def test_20_route_patient_form_action(self):
        """ Test the route to submit an observation via the patient form, should
        return a status and the ids of other activities to carry out
        :return:
        """
        # api_pool = self.registry('nh.eobs.api')
        # patient = api_pool.get_patients(self.cr, self.auth_uid, [])[0]
        #
        # # test demo for ews observation
        # demo_data = {
        #     'respiration_rate': 40,
        #     'indirect_oxymetry_spo2': 100,
        #     'oxygen_administration_flag': False,
        #     'body_temperature': 37.5,
        #     'blood_pressure_systolic': 120,
        #     'blood_pressure_diastolic': 80,
        #     'pulse_rate': 80,
        #     'avpu_text': 'A',
        #     'startTimestamp': 0
        # }
        #
        # # Check if the route under test is actually present into the Route Manager
        # route_under_test = route_manager.get_route('json_patient_form_action')
        # self.assertIsInstance(route_under_test, Route)
        #
        # # Access the route
        # test_resp = requests.post(route_manager.BASE_URL + route_manager.URL_PREFIX + '/patient/submit_ajax/ews/' + str(patient['id']),
        #                           data=json.dumps(demo_data),
        #                           cookies=self.auth_resp.cookies)
        # self.assertEqual(test_resp.status_code, 200)
        # self.assertEqual(test_resp.headers['content-type'], 'application/json')
        #
        # expected_json = {
        #     'related_tasks': []
        # }
        #
        # self.check_response_json(test_resp, ResponseJSON.STATUS_SUCCESS,
        #                          'Observation successfully submitted',
        #                          'Here are related tasks based on the observation',
        #                          expected_json)
        self.assertEqual(False, True, 'Test currently not working due to bug after submitting observation')