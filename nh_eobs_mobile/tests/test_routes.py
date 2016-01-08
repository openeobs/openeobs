from openerp.tools import config
import openerp.tests
import helpers
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

class TestRoutes(openerp.tests.HttpCase):
    def setUp(self):
        super(TestRoutes, self).setUp()
        self.host = "http://localhost:%s" % config['xmlrpc_port']
        self.no404 = 'if(document.getElementsByTagName("body").length && document.getElementsByTagName("body")[0].textContent.indexOf("Not Found")<0){ console.log("ok") }else{ console.log("error") }'
        self.non_db_routes = ['login']
        self.resource_routes =['stylesheet',
                               'jquery',
                               'js_routes',
                               'observation_form_js',
                               'observation_form_validation',
                               'data_driven_documents',
                               'patient_graph',
                               'graph_lib',
                               'logo',
                               'bristol_stools_chart',
                               'logout']
        self.db_routes_no_args = [route['name'] for route in helpers.urls.routes if route['name'] not in self.resource_routes and route['args'] is False]
        self.db_routes_args = [route for route in helpers.urls.routes if route['args'] is not False]


        # self.users_pool = self.registry('res.users')
        # self.api_pool = self.registry('nh.eobs.api')
        # self.patient_pool = self.registry('nh.clinical.patient')
        # self.nurse_id = self.users_pool.search(self.cr, self.uid, [('login', '=', 'nadine')])[0]
        # self.adt_id = self.users_pool.search(self.cr, self.uid, [('login', '=', 'adt')])[0]
        # dob = (dt.now()+td(days=-7300)).strftime(dtf)
        # patient_data = {
        #     'patient_identifier': 'TESTNHS0001',
        #     'family_name': "Al'Thor",
        #     'given_name': 'Rand',
        #     'dob': dob,
        #     'gender': 'M',
        #     'sex': 'M'
        # }
        #
        # self.api_pool.register(self.cr, self.adt_id, 'TESTP0001', patient_data)
        #
        # self.demo_patient_id = self.patient_pool.search(self.cr, self.uid, [('other_identifier', '=', 'TESTP0001')])[0]
        #
        # doctors_data = [
        #     {
        #         'type': 'c',
        #         'code': 'c01',
        #         'title': 'dr',
        #         'family_name': 'Damodred',
        #         'given_name': 'Moiraine'
        #     },
        #     {
        #         'type': 'r',
        #         'code': 'r01',
        #         'title': 'dr',
        #         'family_name': "Al'Vere",
        #         'given_name': 'Egwene'
        #     }
        # ]
        # doa = dt.now().strftime(dtf)
        # admit_data = {
        #     'location': 'U',
        #     'start_date': doa,
        #     'doctors': doctors_data
        # }
        #
        # self.api_pool.admit(self.cr, self.adt_id, 'TESTP0001', admit_data)
        # # Need to add a bit to go and get an example patient and an example of
        # self.demo_task_id = self.api_pool.get_activities(self.cr, self.nurse_id, [])[0]



    def test_non_db_routes_available_without_db(self):
        for route in self.non_db_routes:
            url = helpers.urls.URLS[route]
            print 'non-db ' + url
            self.phantom_js(url, self.no404, 'document', timeout=3600)

    def test_db_routes_without_args_available_post_login(self):
        for route in self.db_routes_no_args:
            url = '{host}{endpoint}'.format(host=self.host, endpoint=helpers.urls.URLS[route])
            print 'db no args ' + url
            self.phantom_js(url, self.no404, 'document', login='nadine', timeout=3600)

    def get_demo_values(self, argument):
        if argument is 'patient_id':
            return '1'
        if argument is 'task_id':
            return '2'
        if argument is 'observation':
            return 'ews'
        return argument

    def test_db_routes_with_args(self):
        for route in self.db_routes_args:
            url = helpers.urls.URLS[route['name']] + '/'.join(map(self.get_demo_values, route['args']))
            print 'db with args ' + url