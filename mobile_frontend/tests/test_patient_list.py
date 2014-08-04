__author__ = 'colin'
from openerp.tests import common
from mock import patch
from datetime import datetime, timedelta, date
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
import openerp.modules.registry
from BeautifulSoup import BeautifulSoup
from openerp.addons.mobile_frontend.controllers.main import MobileFrontend
from werkzeug.wrappers import Request
from werkzeug.test import EnvironBuilder
from werkzeug.contrib.sessions import Session
import requests

# A HTML string that represents the output we expect given the demo data we create
PATIENT_LIST_HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open-eObs</title>
        <link type="text/css" rel="stylesheet" href="/mobile/src/css/main.css"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no" name="viewport"/>
    </head>
    <body>
        <div class="header">
              <div class="header-main block">
                    <img class="logo" src="/mobile/src/img/logo.png"/>
                    <ul class="header-meta">
                        <li class="logout"><a class="button back" href="/mobile/logout/">Logout</a></li>
                    </ul>
              </div>
              <ul class="header-menu two-col">
                   <li><a id="taskNavItem" href="/mobile/tasks/">Task</a></li>
                   <li><a id="patientNavItem" href="/mobile/patients/" class="selected">My Patients</a></li>
              </ul>
        </div>
        <div class="content">
            <ul class="tasklist">
                <li>
                    <a class="level-one block" href="/mobile/patient/1">
                        <div class="task-meta">
                            <div class="task-right">
                                <p class="aside">1988-01-12 06:30:00</p>
                            </div>
                            <div class="task-left">
                                <strong>Patient, Test</strong> ()<br/>
                                <em>Patient, Test ,Patient, Test </em>
                            </div>
                        </div>
                        <div class="task-meta">
                            <p class="taskInfo">Patient, Test</p>
                        </div>
                    </a>
                </li>
            </ul>
        </div>
        <div class="footer block">
            <p class="user">nadine</p>
        </div>
    </body>
</html>
"""

class PatientListTest(common.SingleTransactionCase):

    @patch('openerp.http.Controller')
    def setUp(self, httpController):
        super(PatientListTest, self).setUp()

        # set up database connection objects
        self.registry = openerp.modules.registry.RegistryManager.get('t4clinical_test')
        self.uid = 1
        self.host = 'http://localhost:8169'
        cr, uid = self.cr, self.uid

        # set up pools
        self.patient = self.registry.get('t4.clinical.patient')
        self.patient_visits = self.registry.get('t4.clinical.patient.visit')
        self.tasks = self.registry.get('t4.clinical.task.base')
        self.location = self.registry.get('t4.clinical.pos.delivery')
        self.location_type = self.registry.get('t4.clinical.pos.delivery.type')
        self.users = self.registry.get('res.users')


        # DEMO USERS
        #self.wm = self.users.search(cr, uid, [('login', '=', 'wardmanagergeorge')])[0]
        #self.n = self.users.search(cr, uid, [('login', '=', 'nursemandy')])[0]

        # setup controller
        self.mobile_frontend = MobileFrontend()



    #@patch('werkzeug.wrappers.BaseRequest')
    def test_patient_list(self):
        #with patch('openerp.http.OpenERPSession') as session:
        cr, uid = self.cr, self.uid

        # Create test patient
        env_pool = self.registry('t4.clinical.demo.env')
        api_pool = self.registry('t4.clinical.api')
        config = {
            'patient_qty': 1,
            }
        env_id = env_pool.create(cr, uid, config)
        env = env_pool.build(cr, uid, env_id)
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        register_activity = env_pool.create_complete(cr, adt_user_id, env_id,'t4.clinical.adt.patient.register')
        admit_data = env_pool.fake_data(cr, uid, env_id, 't4.clinical.adt.patient.admit')
        admit_data['other_identifier'] = register_activity.data_ref.other_identifier
        admit_activity = env_pool.create_complete(cr, adt_user_id, env_id,'t4.clinical.adt.patient.admit', {}, admit_data)
        # test admission
        admission_activity = [a for a in admit_activity.created_ids if a.data_model == 't4.clinical.patient.admission']
        assert len(admission_activity) == 1, "Created admission activity: %s" % admission_activity
        admission_activity = admission_activity[0]
        assert admission_activity.state == 'completed'
        #test placement
        placement_activity = [a for a in admission_activity.created_ids if a.data_model == 't4.clinical.patient.placement']
        assert len(placement_activity) == 1, "Created patient.placement activity: %s" % placement_activity
        placement_activity = placement_activity[0]
        assert placement_activity.state == 'new'
        assert placement_activity.pos_id.id == register_activity.pos_id.id
        assert placement_activity.patient_id.id == register_activity.patient_id.id
        assert placement_activity.data_ref.patient_id.id == placement_activity.patient_id.id
        assert placement_activity.data_ref.suggested_location_id
        assert placement_activity.location_id.id == placement_activity.data_ref.suggested_location_id.id

        # Set up request
        session = openerp.http.OpenERPSession({'db': 't4clinical_test',
                                               'login': 'admin',
                                               'password': 'admin',
                                               'uid': 1,
                                               'context': {
                                                   'lang': 'en_GB',
                                                   'tz': 'Europe/London',
                                                   'uid': 1
                                               }}, sid='patientlisttest')
        builder = EnvironBuilder(path='/mobile/patients', base_url='http://localhost:8169', method='GET', data={}, environ_base={'session': session})
        environ = builder.get_environ()
        request = Request(environ)

        request.session = session
        req = openerp.http.HttpRequest(request)

        # Call controller
        get_patients_html = self.mobile_frontend.get_patients(req)

        # Create BS instances
        get_patients_bs = BeautifulSoup(get_patients_html)
        example_patients_bs = BeautifulSoup(PATIENT_LIST_HTML)

        # Assert that shit
        self.assertEqual(get_patients_bs.prettify(), example_patients_bs.prettify(), 'DOM from Controller aint the same as DOM from example')

