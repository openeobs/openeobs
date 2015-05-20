__author__ = 'lorenzo'
import jinja2
import logging
import re
from openerp.tools import config


test_logger = logging.getLogger(__name__)


class Route(object):
    """Class storing all the data for a single route."""
    def __init__(self, name, url, methods=['GET'], response_type='json', headers=[]):
        self.name = name
        self.url = url
        self.methods = methods
        self.response_type = response_type  # TODO: get this from the URL parameter? (ex: adding ?_format=json to the URL)
        self.headers = headers
        #self.CORS = None  # TODO: is this really needed?

        self.args = self.get_args(self.url)

    def get_args(self, url):
        """Fetch named arguments for a URL from that URL.

        Named arguments are the ones written as: <argument_name>

        :param url: A string with a "Werkzeug style" URL - example: 'api/v1/patients/<patient_id>/observation/<observation_id>/'
        :return: List of comma separated strings or the boolean value False (if no argument was fetched)
        """
        args_fetched = re.findall(r'\/<[a-zA-Z]+(?:(?:_|-)[a-zA-Z]+)*>\/?', url)
        trim_regex = re.compile(r'>\/?')
        return [trim_regex.sub('', arg[2:]) for arg in args_fetched] or False


class RouteManager(object):
    """Class storing and managing Route objects."""
    def __init__(self):  # TODO: put these properties as 'init' arguments (?)
        self.SERVER_PROTOCOL = "http"
        self.SERVER_ADDRESS = "localhost"
        self.SERVER_PORT = "{0}".format(config['xmlrpc_port'])
        self.URL_PREFIX = '/mobile/'
        self.BASE_URL = self.SERVER_PROTOCOL + '://' + self.SERVER_ADDRESS + ':' + self.SERVER_PORT + self.URL_PREFIX

        self.ROUTES = {}

    def add_route(self, route):
        """Add a new route to the dictionary ROUTES.

        :param route: A Route object
        :raise KeyError: If 'name' of the Route object to be added is the same of another Route object already in the dictionary
        """
        if route.name in self.ROUTES:
            raise KeyError
        else:
            self.ROUTES[route.name] = route

    def remove_route(self, route_name):  # TODO: is this really needed?
        """Remove an existing route from the dictionary ROUTES.

        :param route_name: A string matching the 'name' key of the route to be removed
        """
        pass

    def get_route(self, route_name):
        """Return an existing route from the dictionary ROUTES.

        :param route_name: A string matching the 'name' key of the route to be returned
        :return: A Route object or None (if a Route object with that name is not found)
        """
        return self.ROUTES.get(route_name, None)

    def get_javascript_routes(self, template_name, template_path, route_list=None, additional_context=None):  # TODO: rename this ! It's not JavaScript strictly related!
        """Render a template file using Jinja.

        :param template_name: The name of the template file
        :param template_path: The absolute path of the template file (omitting the name of the template file)
        :param route_list: A list of Route objects, used to render the template (OPTIONAL)
        :param additional_context: A dictionary that will extend the context used to render the template (OPTIONAL)
        :return: The template file rendered as a string (with a default template variable called "routes" that stores a list of Route objects)
        """
        loader = jinja2.FileSystemLoader(template_path)  # TODO: use only ONE argument for the template's filepath (?)
        env = jinja2.Environment(loader=loader)

        template = env.get_template(template_name)

        routes = route_list or self.ROUTES.values()  # list all the Route objects or only some of them
        default_context = {'routes': routes}

        if additional_context is None:
            return template.render(default_context)
        else:
            default_context.update(additional_context)
            return template.render(default_context)