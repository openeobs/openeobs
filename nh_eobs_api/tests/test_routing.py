__author__ = 'lorenzo'
import jinja2
import json
import logging
import openerp.tests
import requests

from openerp.addons.nh_eobs_api.routing import Route, RouteManager, ResponseJSON
from openerp.modules.module import get_module_path
from unittest import skip, SkipTest

# IMPORTS for @route TEST
from random import choice as random_choice

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
    def test_method_generate_route_objects_with_no_arguments(self):
        route_list_1 = _generate_route_objects()
        self.assertEqual(len(route_list_1), 1)
        for r in route_list_1:
            self.assertIsInstance(r, Route)

    def test_method_generate_route_objects_with_argument_number(self):
        objects_number = 10
        route_list_2 = _generate_route_objects(objects_number)
        self.assertEqual(len(route_list_2), objects_number)
        for r in route_list_2:
            self.assertIsInstance(r, Route)

    def test_method_generate_route_objects_with_argument_string(self):
        route_list_3 = _generate_route_objects("10")
        self.assertEqual(len(route_list_3), 10)
        for r in route_list_3:
            self.assertIsInstance(r, Route)


class TestRouteObjectCreation(openerp.tests.TransactionCase):
    route_name = 'route_name'
    route_url = '/api/v1/test/url/'

    def test_default_route_object_creation(self):
        route = Route(self.route_name, self.route_url)
        self.assertEqual(route.name, self.route_name)
        self.assertEqual(route.url, self.route_url)
        self.assertIsInstance(route.methods, list)
        self.assertEqual(len(route.methods), 1)
        self.assertIn('GET', route.methods)
        self.assertEqual(route.response_type, 'json')
        self.assertIsInstance(route.headers, dict)
        self.assertEqual(len(route.headers), 0)

    def test_custom_route_object_creation(self):
        test_methods = ['POST', 'HEAD', 'FOO', 'BAR']
        test_response_type = 'foobar'
        test_headers = {'Content-Type': 'text/html', 'Foo-Bar': 'not-even-exist'}
        route = Route(self.route_name, self.route_url, response_type=test_response_type, headers=test_headers, methods=test_methods, url_prefix='/test')
        self.assertEqual(route.name, self.route_name)
        self.assertEqual(route.url, self.route_url)
        self.assertEqual(route.response_type, test_response_type)
        self.assertIsInstance(route.headers, dict)
        self.assertEqual(len(route.headers), len(test_headers))
        for h in test_headers:
            self.assertIn(h, route.headers)
        self.assertIsInstance(route.methods, list)
        self.assertEqual(len(route.methods), len(test_methods))
        for m in test_methods:
            self.assertIn(m, route.methods)


class TestRouteObjectInternalMethodSplitURL(openerp.tests.TransactionCase):

    def setUp(self):
        super(TestRouteObjectInternalMethodSplitURL, self).setUp()
        self.route = Route('test_route', '')

    def test_internal_method_split_url_with_no_trailing_slash(self):
        url = '/api/v1/test/url'
        split_url = self.route._split_url(url)
        self.assertIsInstance(split_url, list)
        self.assertEqual(len(split_url), 4)
        self.assertIn('api', split_url)
        self.assertIn('v1', split_url)
        self.assertIn('test', split_url)
        self.assertIn('url', split_url)

    def test_internal_method_split_url_with_trailing_slash(self):
        url = '/api/v1/url/'
        split_url = self.route._split_url(url)
        self.assertIsInstance(split_url, list)
        self.assertEqual(len(split_url), 3)
        self.assertIn('api', split_url)
        self.assertIn('v1', split_url)
        self.assertIn('url', split_url)

    def test_internal_method_split_url_with_multiple_slashes(self):
        url = '/api//v1/test///url///split'
        split_url = self.route._split_url(url)
        self.assertIsInstance(split_url, list)
        self.assertEqual(len(split_url), 5)
        self.assertIn('api', split_url)
        self.assertIn('v1', split_url)
        self.assertIn('test', split_url)
        self.assertIn('url', split_url)
        self.assertIn('split', split_url)

    def test_internal_method_split_url_with_no_string_argument(self):
        url = 56
        self.assertIsInstance(url, int)
        with self.assertRaises(ValueError):
            split_url = self.route._split_url(url)


class TestRouteObjectGetURLComponents(openerp.tests.TransactionCase):

    def setUp(self):
        super(TestRouteObjectGetURLComponents, self).setUp()
        self.route = Route('test_route', '')

    def test_get_url_components_from_url_with_no_argument(self):
        url = '/api/v1/patients/'

        # Create a generator to check each different components of the URL in the assertions below
        name_check_generator = (t for t in ['api', 'v1', 'patients'])

        # Fetch the components list from the method under test
        components_list = self.route._get_url_components(url)

        self.assertEqual(len(components_list), 3)
        for c in components_list:
            self.assertIsInstance(c, dict)
            self.assertEqual(len(c), 2)
            self.assertIn('type', c)
            self.assertIn('name', c)
            self.assertEqual(c['type'], 'string')
            self.assertEqual(c['name'], name_check_generator.next())

    def test_get_url_components_from_url_with_single_argument(self):
        url = '/api/v1/patients/<id>'

        # Create generators to check each different components of the URL in the assertions below
        type_check_generator = (t for t in ['string', 'string', 'string', 'func'])
        name_check_generator = (n for n in ['api', 'v1', 'patients', 'id'])

        # Fetch the components list from the method under test
        components_list = self.route._get_url_components(url)

        self.assertEqual(len(components_list), 4)
        for c in components_list:
            self.assertIsInstance(c, dict)
            self.assertEqual(len(c), 2)
            self.assertIn('type', c)
            self.assertIn('name', c)
            self.assertEqual(c['type'], type_check_generator.next())
            self.assertEqual(c['name'], name_check_generator.next())

    def test_get_url_components_from_url_with_multiple_arguments(self):
        url = '/api/<version_number>/location/<ward_code>/<bed_number>/'

        # Create generators to check each different components of the URL in the assertions below
        type_check_generator = (t for t in ['string', 'func', 'string', 'func', 'func'])
        name_check_generator = (n for n in ['api', 'version_number', 'location', 'ward_code', 'bed_number'])

        # Fetch the components list from the method under test
        components_list = self.route._get_url_components(url)

        self.assertEqual(len(components_list), 5)
        for c in components_list:
            self.assertIsInstance(c, dict)
            self.assertEqual(len(c), 2)
            self.assertIn('type', c)
            self.assertIn('name', c)
            self.assertEqual(c['type'], type_check_generator.next())
            self.assertEqual(c['name'], name_check_generator.next())

    def test_get_url_components_from_url_with_multiple_slashes(self):
        url = 'api///<version_number>/location/<ward_code>///<bed_number>//'

        # Create generators to check each different components of the URL in the assertions below
        type_check_generator = (t for t in ['string', 'func', 'string', 'func', 'func'])
        name_check_generator = (n for n in ['api', 'version_number', 'location', 'ward_code', 'bed_number'])

        # Fetch the components list from the method under test
        components_list = self.route._get_url_components(url)

        self.assertEqual(len(components_list), 5)
        for c in components_list:
            self.assertIsInstance(c, dict)
            self.assertEqual(len(c), 2)
            self.assertIn('type', c)
            self.assertIn('name', c)
            self.assertEqual(c['type'], type_check_generator.next())
            self.assertEqual(c['name'], name_check_generator.next())


class TestGetArgumentsFromRouteURL(openerp.tests.TransactionCase):

    def setUp(self):
        super(TestGetArgumentsFromRouteURL, self).setUp()
        self.route = Route('test_route', '')
        self.assertFalse(self.route.args)

    def test_get_args_from_url_with_no_arguments(self):
        url = '/api/v1/patients/'
        args = self.route._get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

    def test_get_args_from_url_with_one_single_argument(self):
        url = '/api/v1/patients/<patient_id>/'
        args = self.route._get_args(url)
        self.assertEqual(len(args), 1)
        self.assertIn('patient_id', args)

    def test_get_args_from_url_with_multiple_arguments(self):
        url = '/api/v1/patients/<patient_id>/observation/<observation_id>/'
        args = self.route._get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertNotIn('<patient_id>', args)
        self.assertIn('observation_id', args)
        self.assertNotIn('<observation_id>', args)

    def test_get_args_from_url_with_two_consecutive_arguments(self):
        url = '/api/v1/patient/submit_ajax/<observation_type>/<patient_id>/'
        args = self.route._get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertNotIn('<patient_id>', args)
        self.assertIn('observation_type', args)
        self.assertNotIn('<observation_type>', args)

    def test_get_args_from_url_with_multiple_consecutive_arguments(self):
        url = '/api/v1/<multiple>/<consecutive_parameters>/<in_this>/<url>/test/'
        args = self.route._get_args(url)
        self.assertEqual(len(args), 4)
        self.assertIn('multiple', args)
        self.assertNotIn('<multiple>', args)
        self.assertIn('consecutive_parameters', args)
        self.assertNotIn('<consecutive_parameters>', args)
        self.assertIn('in_this', args)
        self.assertNotIn('<in_this>', args)
        self.assertIn('url', args)
        self.assertNotIn('<url>', args)

    def test_get_args_from_url_with_wrong_written_arguments(self):
        url = '/api/v1/patients/<_id>/observation/<observation_id_>/'
        args = self.route._get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

    def test_get_args_from_url_with_mix_cased_arguments(self):
        url = '/api/v1/patients/<paTieNT_ID>/observation/<obSERvatioN_iD>/'
        args = self.route._get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('paTieNT_ID', args)
        self.assertNotIn('<paTieNT_ID>', args)
        self.assertIn('obSERvatioN_iD', args)
        self.assertNotIn('<obSERvatioN_iD>', args)

    def test_get_args_from_url_with_arguments_having_digits(self):
        url = '/api/v1/patients/<pa7ien7_id>/observation/<ob5ervation_id>/'
        args = self.route._get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

    def test_get_args_from_url_with_arguments_having_underscores_and_hyphens(self):
        url = '/api/v1/patients/<patient_id>/observation/<observation-id>/'
        args = self.route._get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertNotIn('<patient_id>', args)
        self.assertIn('observation-id', args)
        self.assertNotIn('<observation-id>', args)

    def test_get_args_from_url_with_arguments_having_underscores_and_hyphens_but_no_chevrons(self):
        url = '/api/v1/patients/patient_id/observation/observation-id/'
        args = self.route._get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

    def test_get_args_from_url_with_no_trailing_slash(self):
        url = '/api/v1/patients/<patient_id>/observation/<observation_id>'
        args = self.route._get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertNotIn('<patient_id>', args)
        self.assertIn('observation_id', args)
        self.assertNotIn('<observation_id>', args)

    def test_get_args_from_url_with_every_possible_VALID_combination(self):
        url = '/api/v1/patients/<Patient_strange-ID>/observation/<obSERvation_typE>/<obserVATion-very_Strange_Id>'
        args = self.route._get_args(url)
        self.assertEqual(len(args), 3)
        self.assertIn('obSERvation_typE', args)
        self.assertNotIn('<obSERvation_typE>', args)
        self.assertIn('Patient_strange-ID', args)
        self.assertNotIn('<Patient_strange-ID>', args)
        self.assertIn('obserVATion-very_Strange_Id', args)
        self.assertNotIn('<obserVATion-very-Strange_Id>', args)


class TestRouteManagerCreation(openerp.tests.TransactionCase):

    def test_default_route_manager_creation(self):
        route_manager = RouteManager()
        self.assertEqual(route_manager.ROUTES, {})

    # TODO: Add more "RouteManager creation" tests


class TestRouteManagerMethods(openerp.tests.TransactionCase):

    def test_method_add_route(self):
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
    def test_method_remove_route(self):
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

    def test_method_get_route(self):
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

    def setUp(self):
        super(TestRouteManagerJavascriptGeneration, self).setUp()

        # Create the RouteManager and feed it with some initial data
        self.objects_number = 5
        generated_route_list = _generate_route_objects(self.objects_number)
        self.route_manager = RouteManager()
        for r in generated_route_list:
            self.route_manager.add_route(r)

        # Check that the RouteManager has been properly created and fed
        self.assertEqual(len(self.route_manager.ROUTES), self.objects_number)
        for r in self.route_manager.ROUTES.values():
            self.assertIsInstance(r, Route)

        # Let's start (eventually!)
        self.name_of_template = 'template_test.js'
        self.path_to_template = get_module_path('nh_eobs_mobile') + '/tests/'
        self.all_route_list = self.route_manager.ROUTES.values()
        self.assertIsInstance(self.all_route_list, list)

    def test_jinja_templating_system(self):
        """Test that Jinja can perform simple string template rendering."""
        template = jinja2.Template("Crazy little thing called {{ thing }}")
        rendered_template = template.render(thing="Love")
        expected_string = "Crazy little thing called Love"
        self.assertEqual(rendered_template, expected_string, 'Jinja is not working as expected.')

    def test_get_javascript_routes_with_only_template_arguments(self):
        js_string = self.route_manager.get_javascript_routes(self.name_of_template, self.path_to_template)
        for r in self.all_route_list:
            self.assertIn(r.name, js_string, 'Route object "{}" was not rendered in the template.'.format(r.name))

    def test_get_javascript_routes_passing_full_list_of_routes(self):
        r_list = self.all_route_list
        js_string = self.route_manager.get_javascript_routes(self.name_of_template, self.path_to_template, route_list=r_list)
        for r in r_list:
            self.assertIn(r.name, js_string, 'Route object "{}" was not rendered in the template.'.format(r.name))

    def test_get_javascript_routes_passing_partial_list_of_routes(self):
        r_list = self.all_route_list[2:self.objects_number]
        self.assertLess(len(r_list), len(self.all_route_list))
        js_string = self.route_manager.get_javascript_routes(self.name_of_template, self.path_to_template, route_list=r_list)
        for r in r_list:
            self.assertIn(r.name, js_string, 'Route object "{}" was not rendered in the template.'.format(r.name))

    def test_get_javascript_routes_passing_additional_context(self):
        add_ctx = {'foo': 'BAR'}
        js_string = self.route_manager.get_javascript_routes(self.name_of_template, self.path_to_template, additional_context=add_ctx)
        for k in add_ctx:
            self.assertIn(add_ctx[k], js_string, 'The key "{}" of the additional context was not rendered in the template'.format(k))

    def test_get_javascript_routes_passing_wrong_template_name(self):
        with self.assertRaises(jinja2.exceptions.TemplateNotFound):
            self.route_manager.get_javascript_routes('fake_template.js', self.path_to_template)

    def test_injection_of_javascript_generated_from_rendered_template(self):
        route_name_list = [r.name for r in self.all_route_list]
        javascript_code = self.route_manager.get_javascript_routes('template_script_test.js',
                                                                   self.path_to_template,
                                                                   additional_context={'route_name_list': route_name_list})
        self.phantom_js('/', javascript_code)  # the actual test and assertions are inside the injected Javascript code!

    def test_get_javascript_routes_passing_two_url_prefixes(self):
        diff_prefix_route = Route('prefix', '/prefix/', url_prefix='/test/url/')
        self.route_manager.add_route(diff_prefix_route)
        r_list = self.all_route_list
        js_string = self.route_manager.get_javascript_routes(self.name_of_template, self.path_to_template, route_list=r_list)
        # need to make sure url prefix is done properly
        for r in r_list:
            self.assertIn(r.name, js_string, 'Route object "{}" was not rendered in the template.'.format(r.name))


class TestResponseJSON(openerp.tests.SingleTransactionCase):

    def setUp(self):
        super(TestResponseJSON, self).setUp()
        self.response_json = ResponseJSON()

    def test_method_get_json_data_passing_all_arguments(self):
        status = self.response_json.STATUS_SUCCESS
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
        json_data = self.response_json.get_json_data(status, title=title, description=description, data=data)

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

    def test_method_get_json_data_passing_only_status(self):
        status = self.response_json.STATUS_FAIL
        json_data = self.response_json.get_json_data(status)
        self.assertIn(status, json_data)

        python_data = json.loads(json_data)  # Convert the data back to Python

        self.assertIsInstance(python_data, dict)
        self.assertEqual(len(python_data), 4)
        self.assertIn('status', python_data)
        self.assertIsInstance(python_data['status'], basestring)
        self.assertEqual(python_data['status'], status)

        ## Test that the DEFAULT value for ALL THE KEYS (except 'status') is 'False'
        self.assertIn('title', python_data)
        self.assertEqual(python_data['title'], False)
        self.assertIn('description', python_data)
        self.assertEqual(python_data['description'], False)
        self.assertIn('data', python_data)
        self.assertEqual(python_data['data'], False)

    def test_method_get_json_data_passing_no_arguments(self):
        json_data = self.response_json.get_json_data()
        self.assertIn(self.response_json.STATUS_ERROR, json_data)

        python_data = json.loads(json_data)  # Convert the data back to Python

        self.assertIsInstance(python_data, dict)
        self.assertEqual(len(python_data), 4)
        self.assertIn('title', python_data)
        self.assertIn('description', python_data)
        self.assertIn('data', python_data)
        self.assertIn('status', python_data)
        self.assertIsInstance(python_data['status'], basestring)
        self.assertEqual(python_data['status'], self.response_json.STATUS_ERROR)  # Test that the DEFAULT STATUS is 'error'

######################
# ROUTING SYSTEM TESTS
######################

# Define server's routing constants to be used for the routing tests
SERVER_PROTOCOL = "http"
SERVER_ADDRESS = "localhost"
SERVER_PORT = "{0}".format(config['xmlrpc_port'])
MOBILE_URL_PREFIX = '/mobile'
BASE_URL = SERVER_PROTOCOL + '://' + SERVER_ADDRESS + ':' + SERVER_PORT
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
diff_prefix_route = Route('prefix', '/prefix/', url_prefix='/test/url', auth='none')

# Add the Route objects to the RouteManager (mandatory to them being considered by the routing workflow)
route_manager_test.add_route(no_args_route)
route_manager_test.add_route(no_args_route_auth_as_user)
route_manager_test.add_route(no_args_route_only_post)

route_manager_test.add_route(single_arg_route)
route_manager_test.add_route(single_arg_route_only_post)

route_manager_test.add_route(custom_keywords_route)

route_manager_test.add_route(expose_route_2)
route_manager_test.add_route(diff_prefix_route)


class ControllerForTesting(http.Controller):

    @http.route(**route_manager_test.expose_route('no_args_route', url_prefix=MOBILE_URL_PREFIX))
    def route_with_no_arguments(self, *args, **kwargs):
        return http.request.make_response('Successfully reached the "route without arguments" page.')

    @http.route(**route_manager_test.expose_route('no_args_route_auth_as_user', url_prefix=MOBILE_URL_PREFIX))
    def route_with_no_arguments_auth_as_user(self, *args, **kwargs):
        return http.request.make_response('Successfully reached the "route without arguments" page as an authenticated user.')

    @http.route(**route_manager_test.expose_route('no_args_route_only_post', url_prefix=MOBILE_URL_PREFIX))
    def route_with_no_arguments_only_post(self, *args, **kwargs):
        return http.request.make_response('Successfully reached the "route without arguments (only POST)" page.')

    @http.route(**route_manager_test.expose_route('single_arg_route', url_prefix=MOBILE_URL_PREFIX))
    def route_with_single_argument(self, *args, **kwargs):
        passed_arg = kwargs.get('arg_id', 'Argument not found!')
        return http.request.make_response('This page has received this argument: {}'.format(passed_arg))

    @http.route(**route_manager_test.expose_route('single_arg_route_only_post', url_prefix=MOBILE_URL_PREFIX))
    def route_with_single_argument_only_post(self, *args, **kwargs):
        passed_arg = kwargs.get('arg_id', 'Argument not found!')
        return http.request.make_response('This page (accessible only by POST requests) has received this argument: {}'.format(passed_arg))

    @http.route(foo='bar', spam='eggs', **route_manager_test.expose_route('custom_keywords_route', url_prefix=MOBILE_URL_PREFIX))
    def route_with_custom_keywords(self, *args, **kwargs):
        return http.request.make_response('Received from the @http.route decorator these keywords: {}'.format(http.request.endpoint.routing))

    @http.route(**route_manager_test.expose_route('prefix'))
    def route_with_prefix_on_route(self, *args, **kwargs):
        return http.request.make_response('Received with url prefix defined on route not route manager')

    @http.route(**route_manager_test.expose_route('prefix', url_prefix=MOBILE_URL_PREFIX))
    def route_with_prefix_on_expose_route(self, *args, **kwargs):
        return http.request.make_response('Received with url prefix defined on expose_route not route manager')

    # TODO: is this useful ???
    @http.route(**route_manager_test.expose_route2('expose_route_2', url_prefix=MOBILE_URL_PREFIX, additional_parameters={'baz': 'ham'}))
    def expose_route_2(self, *args, **kwargs):
        return http.request.make_response('Expose route 2 has received these keywords: {}'.format(http.request.endpoint.routing))


class TestOdooRouteDecoratorIntegration(openerp.tests.common.HttpCase):

    def _get_user_belonging_to_group(self, group_name):
        """Get the 'login' name of a user belonging to a specific group.

        :param group_name: name of the group from which retrieve a user (belonging to it)
        :type group_name: str
        :return: the login name of the retrieved user (belonging to the group passed as argument)
        :rtype: str
        :return: None if there isn't any user belonging to that group
        """
        users_pool = self.registry['res.users']
        users_login_list = users_pool.search_read(self.cr, self.uid,
                                                  domain=[('groups_id.name', '=', group_name)],
                                                  fields=['login'])
        # The search result is a list of dictionaries,
        # so if at least one of them exists in the list,
        # just its 'login' value must be returned
        try:
            login_name = random_choice(users_login_list)
        except IndexError:
            login_name = None

        # Here is where just the 'login' value is returned,
        # instead of the whole dictionary
        return login_name.get('login', None)

    def _get_authenticated_response(self, user_name):
        """Get a Response object with an authenticated session within its cookies.

        :param user_name: username of the user to be authenticated as
        :type user_name: str
        :return: A Response object

        Within this test suite, only the basic Odoo routes
        and the ones defined above in this very file are available
        (that is, these tests cannot rely on the mobile controller routes).

        Hence, the authentication must be done against the base Odoo system
        (and NOT against the mobile controller routes).
        """
        auth_response = requests.post(BASE_URL + '/web/login',
                                      {'login': user_name,
                                       'password': user_name,
                                       'db': DB_NAME},
                                      cookies=self.session_resp.cookies)
        return auth_response

    def setUp(self):
        super(TestOdooRouteDecoratorIntegration, self).setUp()
        self.session_resp = requests.post(BASE_URL + '/web', {'db': DB_NAME})
        if 'session_id' not in self.session_resp.cookies:
            self.fail('Cannot retrieve a valid session to be used for the tests!')

    def test_route_with_no_arguments(self):
        test_resp = requests.get(BASE_MOBILE_URL + no_args_route.url, cookies=self.session_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('Successfully reached the "route without arguments" page.', test_resp.text)

    def test_route_with_no_arguments_auth_as_user(self):
        # Try to access the route as an unauthenticated user, expecting a redirection to the login page.
        test_resp = requests.get(BASE_MOBILE_URL + no_args_route_auth_as_user.url, cookies=self.session_resp.cookies)
        self.assertEqual(len(test_resp.history), 1)
        self.assertEqual(test_resp.history[0].status_code, 302)
        self.assertIn('web/login?redirect=', test_resp.url)

        # To correctly execute this test,
        # the route under test must be accessed as an authenticated user.
        # Hence, this test will be skipped if the authentication fails.
        login_name = self._get_user_belonging_to_group('NH Clinical Nurse Group')
        self.assertIsNotNone(login_name, "Cannot find any 'nurse' user for authentication!")
        auth_resp = self._get_authenticated_response(login_name)
        if auth_resp.status_code != 200:
            self.skipTest('Error during the authenticating (status code: {}).'.format(auth_resp.status_code))

        # Try again to access the route using cookies
        # from an authenticated session, this time expecting a success.
        test_resp = requests.get(BASE_MOBILE_URL + no_args_route_auth_as_user.url, cookies=auth_resp.cookies)
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

    def test_route_with_url_prefix_on_route(self):
        test_resp = requests.get(BASE_URL + '/test/url/prefix/', cookies=self.session_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('Received with url prefix defined on route not route manager', test_resp.text)
        self.assertNotIn('URL Prefix did not work on route!', test_resp.text)

    def test_route_with_url_prefix_on_expose_route(self):
        test_resp = requests.get(BASE_MOBILE_URL + '/prefix/', cookies=self.session_resp.cookies)
        self.assertEqual(test_resp.status_code, 200)
        self.assertIn('Received with url prefix defined on expose_route not route manager', test_resp.text)
        self.assertNotIn('URL Prefix did not work expose_route!', test_resp.text)