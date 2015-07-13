__author__ = 'lorenzo'
import jinja2
import json
import logging
import openerp.tests
import requests
from openerp.addons.nh_eobs_api.routing import Route, RouteManager, ResponseJSON
from openerp.modules.module import get_module_path
from unittest import skip

# IMPORTS for @route TEST
from openerp import http
from openerp.tests import DB as DB_NAME
from openerp.tools import config
##

test_logger = logging.getLogger(__name__)


def _generate_route_objects(number=1):
    """Internal utility method to generate multiple Route objects.

    :param number: Number of Route objects to generate
    :return: List of Route objects
    """
    route_list = []
    for n in range(int(number)):
        r = Route('test_route_{}'.format(n), 'api/v1/test/resource_{}'.format(n))
        route_list.append(r)
    return route_list  # TODO: return a generator instead ?


class TestUtilitiesMethods(openerp.tests.BaseCase):
    """Class that tests all the internal utilities methods.

    It inherits from an Odoo's test class, thus it has all its useful features.
    """
    def test_generate_route_objects(self):

        # Scenario 1:
        # Passing NOTHING to the function
        route_list_1 = _generate_route_objects()
        self.assertEqual(len(route_list_1), 1)
        for r in route_list_1:
            self.assertIsInstance(r, Route)

        # Scenario 2:
        # Passing a NUMBER to the function
        objects_number = 10
        route_list_2 = _generate_route_objects(objects_number)
        self.assertEqual(len(route_list_2), objects_number)
        for r in route_list_2:
            self.assertIsInstance(r, Route)

        # Scenario 3:
        # Passing a number as STRING to the function
        route_list_3 = _generate_route_objects("10")
        self.assertEqual(len(route_list_3), 10)
        for r in route_list_3:
            self.assertIsInstance(r, Route)


class TestRoute(openerp.tests.TransactionCase):

    def test_route_creation(self):
        # Set up only the required parameters
        route_name = 'route_name'
        route_url = '/api/v1/test/url/'

        # Scenario 1:
        # Default Route creation
        route = Route(route_name, route_url)
        self.assertEqual(route.name, route_name)
        self.assertEqual(route.url, route_url)

        self.assertIsInstance(route.methods, list)
        self.assertEqual(len(route.methods), 1)
        self.assertIn('GET', route.methods)

        self.assertEqual(route.response_type, 'json')

        self.assertIsInstance(route.headers, dict)
        self.assertEqual(len(route.headers), 0)

        # Scenario 2:
        # Route creation with custom arguments
        test_methods = ['POST', 'HEAD', 'FOO', 'BAR']
        test_response_type = 'foobar'
        test_headers = {'Content-Type': 'text/html', 'Foo-Bar': 'not-even-exist'}

        route = Route(route_name, route_url, response_type=test_response_type, headers=test_headers, methods=test_methods)
        self.assertEqual(route.name, route_name)
        self.assertEqual(route.url, route_url)

        self.assertEqual(route.response_type, test_response_type)

        self.assertIsInstance(route.headers, dict)
        self.assertEqual(len(route.headers), len(test_headers))
        for h in test_headers:
            self.assertIn(h, route.headers)

        self.assertIsInstance(route.methods, list)
        self.assertEqual(len(route.methods), len(test_methods))
        for m in test_methods:
            self.assertIn(m, route.methods)

    def test_get_args_from_url(self):
        self.route = Route('test_route', '')
        self.assertFalse(self.route.args)

        # Scenario 1:
        # Test URL without named argument
        url = '/api/v1/patients/'
        args = self.route.get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

        # Scenario 2:
        # Test URL with one single named argument
        url = '/api/v1/patients/<patient_id>/'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 1)
        self.assertIn('patient_id', args)

        # Scenario 3:
        # Test URL with multiple named arguments
        url = '/api/v1/patients/<patient_id>/observation/<observation_id>/'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertNotIn('<patient_id>', args)
        self.assertIn('observation_id', args)
        self.assertNotIn('<observation_id>', args)

        # Scenario 4:
        # Test URL with wrong-written named arguments
        url = '/api/v1/patients/<_id>/observation/<observation_id_>/'
        args = self.route.get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

        # Scenario 5:
        # Test URL with mix-cased named arguments
        url = '/api/v1/patients/<paTieNT_ID>/observation/<obSERvatioN_iD>/'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('paTieNT_ID', args)
        self.assertNotIn('<paTieNT_ID', args)
        self.assertIn('obSERvatioN_iD', args)
        self.assertNotIn('<obSERvatioN_iD', args)

        # Scenario 6:
        # Test URL with arguments with digits in their names
        url = '/api/v1/patients/<pa7ien7_id>/observation/<ob5ervation_id>/'
        args = self.route.get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

        # Scenario 7:
        # Test URL with underscores and hyphens
        url = '/api/v1/patients/<patient_id>/observation/<observation-id>/'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertNotIn('<patient_id>', args)
        self.assertIn('observation-id', args)
        self.assertNotIn('<observation-id>', args)

        # Scenario 8:
        # Test URL with underscores and hyphens (but without chevrons)
        url = '/api/v1/patients/patient_id/observation/observation-id/'
        args = self.route.get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

        # Scenario 9:
        # Test URL without trailing slash
        url = '/api/v1/patients/<patient_id>/observation/<observation_id>'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertNotIn('<patient_id>', args)
        self.assertIn('observation_id', args)
        self.assertNotIn('<observation_id>', args)

        # Scenario 10:
        # Test URL with every possible VALID combination
        url = '/api/v1/patients/<Patient_strange-ID>/observation/<obserVATion-very_Strange_Id>'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('Patient_strange-ID', args)
        self.assertNotIn('<Patient_strange-ID', args)
        self.assertIn('obserVATion-very_Strange_Id', args)
        self.assertNotIn('<obserVATion-very-Strange_Id>', args)


class TestRouteManager(openerp.tests.TransactionCase):

    def test_route_manager_creation(self):
        # Scenario 1:
        # Default RouteManager creation (no parameters)
        route_manager = RouteManager()
        self.assertEqual(route_manager.ROUTES, {})
        # TODO: Add more "RouteManager creation" scenarios

    def test_add_route_to_manager(self):
        route_manager = RouteManager()
        self.assertEqual(route_manager.ROUTES, {})

        # Route #1 is added
        route_1 = Route('test_route_1', '/api/v1/test/route-1/')
        route_manager.add_route(route_1)

        self.assertEqual(len(route_manager.ROUTES), 1)
        self.assertEqual(route_1.name, 'test_route_1')
        self.assertIn(route_1.name, route_manager.ROUTES.keys())

        # Route #2 - with a DIFFERENT name - is added
        route_2 = Route('test_route_2', '/api/v1/test/route-2/')
        route_manager.add_route(route_2)

        self.assertEqual(len(route_manager.ROUTES), 2)
        self.assertEqual(route_2.name, 'test_route_2')
        self.assertIn(route_2.name, route_manager.ROUTES.keys())

        # Route #3 - with the SAME name of Route #2 - is added
        route_3 = Route('test_route_2', '/api/v1/test/route-3/')
        self.assertEqual(route_3.name, 'test_route_2')

        with self.assertRaises(KeyError):
            route_manager.add_route(route_3)

        self.assertEqual(len(route_manager.ROUTES), 2)
        self.assertIsNot(route_3, route_manager.ROUTES['test_route_2'])

        # Route #3 - with the SAME name of Route #2 - is added AGAIN & AGAIN
        for i in range(10):
            with self.assertRaises(KeyError):
                route_manager.add_route(route_3)

        self.assertEqual(len(route_manager.ROUTES), 2)
        self.assertIsNot(route_3, route_manager.ROUTES['test_route_2'])

        # Route #4 - with a DIFFERENT name - is added
        route_4 = Route('test_route_4', '/api/v1/test/route-4/')
        route_manager.add_route(route_4)

        self.assertEqual(len(route_manager.ROUTES), 3)
        self.assertEqual(route_4.name, 'test_route_4')
        self.assertIn(route_4.name, route_manager.ROUTES.keys())

    @skip('Unfinished test here! Please, complete me =)')
    def test_remove_route(self):
        # Create the RouteManager and feed it with some initial data
        objects_number = 5
        generated_route_list = _generate_route_objects(objects_number)
        route_manager = RouteManager()
        for r in generated_route_list:
            route_manager.add_route(r)

        # Check that the RouteManager has been properly created and fed
        self.assertEqual(len(route_manager.ROUTES), objects_number)
        for r in route_manager.ROUTES.values():
            self.assertIsInstance(r, Route)

        # Check that a specific Route actually is in the RouteManager and then remove it (and check the removal)
        self.assertIn('test_route_3', route_manager.ROUTES)
        route_manager.remove_route('test_route_3')
        self.assertNotIn('test_route_3', route_manager.ROUTES)
        self.assertEqual(len(route_manager.ROUTES), (objects_number - 1))

    def test_get_route(self):
        route_manager = RouteManager()

        route_name_list = ['route_{}'.format(n) for n in range(10)]

        for route_name in route_name_list:
            r = Route(route_name, '/api/v1/test/')
            route_manager.add_route(r)
            self.assertIn(route_name, route_manager.ROUTES.keys())

        self.assertEqual(len(route_manager.ROUTES), len(route_name_list))

        for route_name in route_name_list:
            r = route_manager.get_route(route_name)
            self.assertIsInstance(r, Route)
            self.assertEqual(r.name, route_name)

        not_existing_route = route_manager.get_route('non_existing_route_name')
        self.assertNotIsInstance(not_existing_route, Route)
        self.assertIsNone(not_existing_route)


class TestRouteManagerJavascriptGeneration(openerp.tests.HttpCase):
    """Test the JavaScript generation powers of the RouteManager class!"""
    def test_jinja_templating_system(self):
        """Test that Jinja can perform simple string template rendering."""
        template = jinja2.Template("Crazy little thing called {{ thing }}")
        rendered_template = template.render(thing="Love")
        expected_string = "Crazy little thing called Love"
        self.assertEqual(rendered_template, expected_string, 'Jinja is not working as expected.')

    def test_get_javascript_routes(self):
        # Create the RouteManager and feed it with some initial data
        objects_number = 5
        generated_route_list = _generate_route_objects(objects_number)
        route_manager = RouteManager()
        for r in generated_route_list:
            route_manager.add_route(r)

        # Check that the RouteManager has been properly created and fed
        self.assertEqual(len(route_manager.ROUTES), objects_number)
        for r in route_manager.ROUTES.values():
            self.assertIsInstance(r, Route)

        # Let's start (eventually!)
        name_of_template = 'template_test.js'
        path_to_template = get_module_path('nh_eobs_mobile') + '/tests/'
        all_route_list = route_manager.ROUTES.values()
        self.assertIsInstance(all_route_list, list)

        # Scenario 1:
        # NO CONTEXT is passed to the function
        js_string_1 = route_manager.get_javascript_routes(name_of_template, path_to_template)
        for r in all_route_list:
            self.assertIn(r.name, js_string_1, 'Route object "{}" was not rendered in the template.'.format(r.name))

        # Scenario 2:
        # A list with ALL the Route objects is passed to the function
        r_list_2 = all_route_list
        js_string_2 = route_manager.get_javascript_routes(name_of_template, path_to_template, route_list=r_list_2)
        for r_2 in r_list_2:
            self.assertIn(r_2.name, js_string_2, 'Route object "{}" was not rendered in the template.'.format(r_2.name))

        # Scenario 3:
        # A list with only SOME Route objects is passed to the function
        r_list_3 = all_route_list[2:objects_number]
        self.assertLess(len(r_list_3), len(all_route_list))
        js_string_3 = route_manager.get_javascript_routes(name_of_template, path_to_template, route_list=r_list_3)
        for r_3 in r_list_3:
            self.assertIn(r_3.name, js_string_3, 'Route object "{}" was not rendered in the template.'.format(r_3.name))

        # Scenario 4:
        # An additional context is passed to the function
        add_ctx = {'foo': 'BAR'}
        js_string_4 = route_manager.get_javascript_routes(name_of_template, path_to_template, additional_context=add_ctx)
        for k in add_ctx:
            self.assertIn(add_ctx[k], js_string_4, 'The key "{}" of the additional context was not rendered in the template'.format(k))

        # Scenario 5:
        # A wrong template name is passed to the function
        with self.assertRaises(jinja2.exceptions.TemplateNotFound):
            route_manager.get_javascript_routes('fake_template.js', path_to_template)

        # Scenario 6:
        # Injection of Javascript code, generated from a template rendered by Jinja
        route_name_list = [r.name for r in all_route_list]
        javascript_code = route_manager.get_javascript_routes('template_script_test.js',
                                                              path_to_template,
                                                              additional_context={'route_name_list': route_name_list})
        self.phantom_js('/', javascript_code)


class TestResponseJSON(openerp.tests.SingleTransactionCase):

    def test_get_json_data(self):
        response_json = ResponseJSON()

        # Scenario 1:
        # Pass ALL the required arguments, along with a SUCCESSFUL status
        status = response_json.STATUS_SUCCESS
        title = 'Operation executed'
        description = 'The operation required via API was successful executed'
        data = {
            'patient_list': [
                'patient_1',
                'patient_2',
                'patient_3',
                'patient_4'
            ],
            'related_action_list': [
                'admission',
                'observation',
                'discharge'
            ]
        }
        json_data = response_json.get_json_data(status, title=title, description=description, data=data)

        self.assertIn(status, json_data)
        self.assertIn(title, json_data)
        self.assertIn(description, json_data)
        for k, v in data.iteritems():
            self.assertIn(k, json_data)
            for e in v:
                self.assertIn(e, json_data)

        python_data = json.loads(json_data)  # Convert the data back to Python

        self.assertIsInstance(python_data, dict)
        self.assertEqual(len(python_data), 4)

        self.assertIn('status', python_data)
        self.assertIsInstance(python_data['status'], basestring)
        self.assertEqual(python_data['status'], status)

        self.assertIn('title', python_data)
        self.assertIsInstance(python_data['title'], basestring)
        self.assertEqual(python_data['title'], title)

        self.assertIn('description', python_data)
        self.assertIsInstance(python_data['description'], basestring)
        self.assertEqual(python_data['description'], description)

        self.assertIn('data', python_data)
        self.assertIsInstance(python_data['data'], dict)
        for k, v in data.iteritems():
            self.assertIn(k, python_data['data'])
            for e in v:
                self.assertIn(e, python_data['data'][k])

        # Scenario 2:
        # Pass ONLY the STATUS
        status_2 = response_json.STATUS_FAIL
        json_data_2 = response_json.get_json_data(status_2)
        self.assertIn(status_2, json_data_2)

        python_data_2 = json.loads(json_data_2)  # Convert the data back to Python

        self.assertIsInstance(python_data_2, dict)
        self.assertEqual(len(python_data_2), 4)

        self.assertIn('status', python_data_2)
        self.assertIsInstance(python_data_2['status'], basestring)
        self.assertEqual(python_data_2['status'], status_2)

        ## Test that the DEFAULT value for ALL THE KEYS (except 'status') is 'False'
        self.assertIn('title', python_data_2)
        self.assertEqual(python_data_2['title'], False)
        self.assertIn('description', python_data_2)
        self.assertEqual(python_data_2['description'], False)
        self.assertIn('data', python_data_2)
        self.assertEqual(python_data_2['data'], False)

        # Scenario 3:
        # Pass NO arguments
        json_data_3 = response_json.get_json_data()
        self.assertIn(response_json.STATUS_ERROR, json_data_3)

        python_data_3 = json.loads(json_data_3)  # Convert the data back to Python

        self.assertIsInstance(python_data_3, dict)
        self.assertEqual(len(python_data_3), 4)
        self.assertIn('title', python_data_3)
        self.assertIn('description', python_data_3)
        self.assertIn('data', python_data_3)

        self.assertIn('status', python_data_3)
        self.assertIsInstance(python_data_3['status'], basestring)
        self.assertEqual(python_data_3['status'], response_json.STATUS_ERROR)  # Test that the DEFAULT STATUS is 'error'

######################
# ROUTING SYSTEM TESTS
######################

# Define server's routing constants to be used for the routing tests
SERVER_PROTOCOL = "http"
SERVER_ADDRESS = "localhost"
SERVER_PORT = "{0}".format(config['xmlrpc_port'])
MOBILE_URL_PREFIX = '/mobile'  # TODO: add a leading slash (DONE)
BASE_URL = SERVER_PROTOCOL + '://' + SERVER_ADDRESS + ':' + SERVER_PORT  # TODO: remove the trailing slash (DONE)
BASE_MOBILE_URL = BASE_URL + MOBILE_URL_PREFIX

# Create the RouteManager and the Route objects for the tests
route_manager_test = RouteManager()

no_args_route = Route('no_args_route', '/no/args/route/', auth='none')
no_args_route_only_post = Route('no_args_route_only_post', '/no/args/route/post/', auth='none', methods=['POST'])
no_args_route_auth_as_user = Route('no_args_route_auth_as_user', '/no/args/route/auth/user/', auth='user')

single_arg_route = Route('single_arg_route', '/single/arg/<arg_id>/', auth='none')
single_arg_route_only_post = Route('single_arg_route_only_post', '/single/arg/<arg_id>/post/', auth='none', methods=['POST'])

custom_keywords_route = Route('custom_keywords_route', '/custom/keywords/route/', auth='none')

expose_route_2 = Route('expose_route_2', '/expose/route2/', auth='none')

# Add the Route objects to the RouteManager (mandatory to them being considered by the routing workflow)
route_manager_test.add_route(no_args_route)
route_manager_test.add_route(no_args_route_auth_as_user)
route_manager_test.add_route(no_args_route_only_post)

route_manager_test.add_route(single_arg_route)
route_manager_test.add_route(single_arg_route_only_post)

route_manager_test.add_route(custom_keywords_route)

route_manager_test.add_route(expose_route_2)


class ControllerForTesting(http.Controller):

    #test_logger.warning(route_manager_test.expose_route('single_arg_route', url_prefix=MOBILE_URL_PREFIX))

    @http.route(**route_manager_test.expose_route('no_args_route', url_prefix=MOBILE_URL_PREFIX))
    def route_with_no_arguments(self, *args, **kwargs):
        return http.request.make_response('Successfully reached the "route without arguments" page.')

    @http.route(**route_manager_test.expose_route('no_args_route_auth_as_user', url_prefix=MOBILE_URL_PREFIX))
    def route_with_no_arguments_auth_as_user(self, *args, **kwargs):
        return http.request.make_response('Successfully reached the "route without arguments" page as an authenticated user.')

    @http.route(**route_manager_test.expose_route('no_args_route_only_post', url_prefix=MOBILE_URL_PREFIX))
    def route_with_no_arguments_only_post(self, *args, **kwargs):
        return http.request.make_response('Successfully reached the "route without arguments (only POST)" page.')

    ####@http.route(MOBILE_URL_PREFIX + single_arg_route.url, auth='none', lol='asd', headers={'ctype': 'html'})
    @http.route(**route_manager_test.expose_route('single_arg_route', url_prefix=MOBILE_URL_PREFIX))
    def route_with_single_argument(self, *args, **kwargs):
        #test_logger.warning(args)
        #test_logger.warning(kwargs)
        #test_logger.warning(http.request.endpoint.routing)
        passed_arg = kwargs.get('arg_id', 'Argument not found!')
        return http.request.make_response('This page has received this argument: {}'.format(passed_arg))

    @http.route(**route_manager_test.expose_route('single_arg_route_only_post', url_prefix=MOBILE_URL_PREFIX))
    def route_with_single_argument_only_post(self, *args, **kwargs):
        passed_arg = kwargs.get('arg_id', 'Argument not found!')
        return http.request.make_response('This page (accessible only by POST requests) has received this argument: {}'.format(passed_arg))

    @http.route(foo='bar', spam='eggs', **route_manager_test.expose_route('custom_keywords_route', url_prefix=MOBILE_URL_PREFIX))
    def route_with_custom_keywords(self, *args, **kwargs):
        #test_logger.warning(http.request.endpoint.routing)
        return http.request.make_response('Received from the @http.route decorator these keywords: {}'.format(http.request.endpoint.routing))

    # TODO: is this useful ???
    @http.route(**route_manager_test.expose_route2('expose_route_2', url_prefix=MOBILE_URL_PREFIX, additional_parameters={'baz': 'ham'}))
    def expose_route_2(self, *args, **kwargs):
        test_logger.warning(http.request.endpoint.routing)
        return http.request.make_response('Expose route 2 has received these keywords: {}'.format(http.request.endpoint.routing))


class TestOdooRouteDecoratorIntegration(openerp.tests.common.HttpCase):

    def _get_authenticated_response(self, user_name):
        """Get a Response object with an authenticated session within its cookies.

        :param user_name: A string with the username of the user to be authenticated as
        :return: A Response object
        """
        auth_response = requests.post(BASE_MOBILE_URL + '/login',
                                      {'username': user_name,
                                       'password': user_name,
                                       'database': DB_NAME},
                                      cookies=self.session_resp.cookies)
        return auth_response

    def setUp(self):
        super(TestOdooRouteDecoratorIntegration, self).setUp()
        self.session_resp = requests.post(BASE_URL + '/web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self.fail('Cannot retrieve a valid session to be used for the tests!')
    """
        login_name = self._get_user_belonging_to_group('NH Clinical Nurse Group')
        self.assertNotEqual(login_name, False,
                            "Cannot find any 'nurse' user for authentication before running the test!")
        self.auth_resp = self._get_authenticated_response(login_name)
        self.assertEqual(self.auth_resp.status_code, 200)
        self.assertIn('class="tasklist"', self.auth_resp.content)
    """

    def test_route_with_no_arguments(self):
        test_resp = requests.get(BASE_MOBILE_URL + no_args_route.url, cookies=self.session_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('Successfully reached the "route without arguments" page.', test_resp.text)

    def test_route_with_no_arguments_auth_as_user(self):
        # Try to access the route as an unauthenticated user, expecting a redirection to the login page
        test_resp = requests.get(BASE_MOBILE_URL + no_args_route_auth_as_user.url, cookies=self.session_resp.cookies)
        #test_logger.warning('STATUS CODE NOT AUTH = {}'.format(test_resp.status_code))
        self.assertEqual(len(test_resp.history), 1)
        self.assertEqual(test_resp.history[0].status_code, 302)
        self.assertIn('web/login?redirect=', test_resp.url)

        # Authenticate and check the login was successful
        auth_resp = self._get_authenticated_response('nadine')
        self.assertEqual(auth_resp.status_code, 200)
        self.assertIn('class="tasklist"', auth_resp.content)

        # Try again to access the route, this time expecting a success
        test_resp = requests.get(BASE_MOBILE_URL + no_args_route_auth_as_user.url, cookies=auth_resp.cookies)
        #test_logger.warning('STATUS CODE AUTH= {}'.format(test_resp.status_code))
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('Successfully reached the "route without arguments" page as an authenticated user.', test_resp.text)

    def test_route_with_no_arguments_only_post(self):
        test_resp_get = requests.get(BASE_MOBILE_URL + no_args_route_only_post.url, cookies=self.session_resp.cookies)
        self.assertNotEqual(test_resp_get.status_code, 200)
        self.assertEqual(test_resp_get.status_code, 405)

        test_resp_post = requests.post(BASE_MOBILE_URL + no_args_route_only_post.url, cookies=self.session_resp.cookies)
        self.assertEqual(test_resp_post.status_code, 200)
        self.assertIn('Successfully reached the "route without arguments (only POST)" page.', test_resp_post.text)

    def test_route_with_single_argument(self):
        test_resp = requests.get(BASE_MOBILE_URL + '/single/arg/47/', cookies=self.session_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('This page has received this argument: 47', test_resp.text)
        self.assertNotIn('Argument not found!', test_resp.text)

    def test_route_with_single_argument_only_post(self):
        test_resp_get = requests.get(BASE_MOBILE_URL + '/single/arg/314/post/', cookies=self.session_resp.cookies)
        #test_logger.warning(test_resp_get.status_code)
        self.assertNotEqual(test_resp_get.status_code, 200)
        self.assertEqual(test_resp_get.status_code, 405)

        test_resp_post = requests.post(BASE_MOBILE_URL + '/single/arg/314/post/', cookies=self.session_resp.cookies)
        self.assertEqual(test_resp_post.status_code, 200)
        self.assertIn('This page (accessible only by POST requests) has received this argument: 314', test_resp_post.text)
        self.assertNotIn('Argument not found!', test_resp_post.text)

    def test_route_with_custom_keywords(self):
        """Test hacking the @http.route decorator by passing custom keywords to it."""
        test_resp = requests.get(BASE_MOBILE_URL + custom_keywords_route.url, cookies=self.session_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('@http.route', test_resp.text)
        self.assertIn('foo', test_resp.text)
        self.assertIn('bar', test_resp.text)
        self.assertIn('spam', test_resp.text)
        self.assertIn('eggs', test_resp.text)

    def test_expose_route_2(self):  # TODO: is this useful ???
        """Test an alternative version of the 'expose_route' method that accepts custom keywords."""
        test_resp = requests.get(BASE_MOBILE_URL + expose_route_2.url, cookies=self.session_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('Expose route 2', test_resp.text)
        self.assertIn('baz', test_resp.text)
        self.assertIn('ham', test_resp.text)