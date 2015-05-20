__author__ = 'lorenzo'
import jinja2
import logging
import openerp.tests
from openerp.addons.nh_eobs_mobile.controllers.urls_api import Route, RouteManager
from openerp.modules.module import get_module_path


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
        route_url = 'api/v1/test/url/'

        # Scenario 1:
        # Default Route creation
        route = Route(route_name, route_url)
        self.assertEqual(route.name, route_name)
        self.assertEqual(route.url, route_url)

        self.assertIsInstance(route.methods, list)
        self.assertEqual(len(route.methods), 1)
        self.assertIn('GET', route.methods)

        self.assertEqual(route.response_type, 'json')

        self.assertIsInstance(route.headers, list)
        self.assertEqual(len(route.headers), 0)

        # Scenario 2:
        # Route creation with custom arguments
        test_method_list = ['POST', 'HEAD', 'FOO', 'BAR']
        test_response_type = 'foobar'
        test_header_list = ['Content-Type: text/html;', 'Foo-Bar: not-even-exist;']

        route = Route(route_name, route_url, response_type=test_response_type, headers=test_header_list, methods=test_method_list)
        self.assertEqual(route.name, route_name)
        self.assertEqual(route.url, route_url)

        self.assertEqual(route.response_type, test_response_type)

        self.assertIsInstance(route.headers, list)
        self.assertEqual(len(route.headers), len(test_header_list))
        for h in test_header_list:
            self.assertIn(h, route.headers)

        self.assertIsInstance(route.methods, list)
        self.assertEqual(len(route.methods), len(test_method_list))
        for m in test_method_list:
            self.assertIn(m, route.methods)

    def test_get_args_from_url(self):
        self.route = Route('test_route', '')
        self.assertFalse(self.route.args)

        # Scenario 1:
        # Test URL without named argument
        url = 'api/v1/patients/'
        args = self.route.get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

        # Scenario 2:
        # Test URL with one single named argument
        url = 'api/v1/patients/<patient_id>/'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 1)
        self.assertIn('patient_id', args)

        # Scenario 3:
        # Test URL with multiple named arguments
        url = 'api/v1/patients/<patient_id>/observation/<observation_id>/'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertIn('observation_id', args)

        # Scenario 4:
        # Test URL with wrong-written named arguments
        url = 'api/v1/patients/<_id>/observation/<observation_id_>/'
        args = self.route.get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

        # Scenario 5:
        # Test URL with mix-cased named arguments
        url = 'api/v1/patients/<paTieNT_ID>/observation/<obSERvatioN_iD>/'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('paTieNT_ID', args)
        self.assertIn('obSERvatioN_iD', args)

        # Scenario 6:
        # Test URL with arguments with digits in their names
        url = 'api/v1/patients/<pa7ien7_id>/observation/<ob5ervation_id>/'
        args = self.route.get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

        # Scenario 7:
        # Test URL with underscores and hyphens
        url = 'api/v1/patients/<patient_id>/observation/<observation-id>/'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertIn('observation-id', args)

        # Scenario 8:
        # Test URL with underscores and hyphens (but without chevrons)
        url = 'api/v1/patients/patient_id/observation/observation-id/'
        args = self.route.get_args(url)
        self.assertNotIsInstance(args, list)
        self.assertEqual(args, False)

        # Scenario 9:
        # Test URL without trailing slash
        url = 'api/v1/patients/<patient_id>/observation/<observation_id>'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('patient_id', args)
        self.assertIn('observation_id', args)

        # Scenario 10:
        # Test URL with every possible VALID combination
        url = 'api/v1/patients/<Patient_strange-ID>/observation/<obserVATion-very_Strange_Id>'
        args = self.route.get_args(url)
        self.assertEqual(len(args), 2)
        self.assertIn('Patient_strange-ID', args)
        self.assertIn('obserVATion-very_Strange_Id', args)


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
        route_1 = Route('test_route_1', 'api/v1/test/route-1/')
        route_manager.add_route(route_1)

        self.assertEqual(len(route_manager.ROUTES), 1)
        self.assertEqual(route_1.name, 'test_route_1')
        self.assertIn(route_1.name, route_manager.ROUTES.keys())

        # Route #2 - with a DIFFERENT name - is added
        route_2 = Route('test_route_2', 'api/v1/test/route-2/')
        route_manager.add_route(route_2)

        self.assertEqual(len(route_manager.ROUTES), 2)
        self.assertEqual(route_2.name, 'test_route_2')
        self.assertIn(route_2.name, route_manager.ROUTES.keys())

        # Route #3 - with the SAME name of Route #2 - is added
        route_3 = Route('test_route_2', 'api/v1/test/route-3/')
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
        route_4 = Route('test_route_4', 'api/v1/test/route-4/')
        route_manager.add_route(route_4)

        self.assertEqual(len(route_manager.ROUTES), 3)
        self.assertEqual(route_4.name, 'test_route_4')
        self.assertIn(route_4.name, route_manager.ROUTES.keys())
    """
    def test_remove_route(self):  # TODO: Complete this test !!!
        self.fail('Unfinished test here! Please, complete me =)')
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
    """

    def test_get_route(self):
        route_manager = RouteManager()

        route_name_list = ['route_{}'.format(n) for n in range(10)]

        for route_name in route_name_list:
            r = Route(route_name, 'api/v1/test/')
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
        #test_logger.info("js_string_1: {}".format(js_string_1))
        for r in all_route_list:
            self.assertIn(r.name, js_string_1, 'Route object "{}" was not rendered in the template.'.format(r.name))

        # Scenario 2:
        # A list with ALL the Route objects is passed to the function
        r_list_2 = all_route_list
        js_string_2 = route_manager.get_javascript_routes(name_of_template, path_to_template, route_list=r_list_2)
        #test_logger.info("js_string_2: {}".format(js_string_2))
        for r_2 in r_list_2:
            self.assertIn(r_2.name, js_string_2, 'Route object "{}" was not rendered in the template.'.format(r_2.name))

        # Scenario 3:
        # A list with only SOME Route objects is passed to the function
        r_list_3 = all_route_list[2:objects_number]
        self.assertLess(len(r_list_3), len(all_route_list))
        js_string_3 = route_manager.get_javascript_routes(name_of_template, path_to_template, route_list=r_list_3)
        #test_logger.info("js_string_3: {}".format(js_string_3))
        for r_3 in r_list_3:
            self.assertIn(r_3.name, js_string_3, 'Route object "{}" was not rendered in the template.'.format(r_3.name))

        # Scenario 4:
        # An additional context is passed to the function
        add_ctx = {'foo': 'BAR'}
        js_string_4 = route_manager.get_javascript_routes(name_of_template, path_to_template, additional_context=add_ctx)
        #test_logger.info("js_string_4: {}".format(js_string_4))
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
        #test_logger.info("javascript_code: {}".format(javascript_code))
        self.phantom_js('/', javascript_code)