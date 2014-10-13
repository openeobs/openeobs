__author__ = 'colin'
from openerp.tests import common
import openerp.modules.registry
from BeautifulSoup import BeautifulSoup
import helpers
import logging
_logger = logging.getLogger(__name__)

class PatientListTest(common.SingleTransactionCase):

    def setUp(self):
        super(PatientListTest, self).setUp()

        # set up database connection objects
        self.uid = 1
        self.host = 'http://localhost:8169'

        # set up pools
        self.patient = self.registry.get('nh.clinical.patient')
        self.patient_visits = self.registry.get('nh.clinical.patient.visit')
        self.tasks = self.registry.get('nh.clinical.task.base')
        self.location = self.registry.get('nh.clinical.pos.delivery')
        self.location_type = self.registry.get('nh.clinical.pos.delivery.type')
        self.users = self.registry.get('res.users')

    def test_patient_list(self):
        cr, uid = self.cr, self.uid

        # Create test patient
        # create environment
        api_demo = self.registry('nh.clinical.api.demo')
        if not api_demo.demo_data_loaded(cr, uid):
            _logger.warn("Demo data is not loaded and this test relies on it! Skiping test.")
            return
        api_demo.build_uat_env(cr, uid, patients=8, placements=4, context=None)

        # get a nurse user
        norah_user = self.users.search(cr, uid, [['login', '=', 'norah']])[0]

        self.context = {
            'lang': 'en_GB',
            'tz': 'Europe/London',
            'uid': 1
        }

        # Call controller
        patient_api = self.registry['nh.eobs.api']
        patients = patient_api.get_patients(cr, norah_user, [], context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'], patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False

        view_obj = self.registry("ir.ui.view")
        get_patients_html = view_obj.render(
            cr, uid, 'nh_eobs_mobile.patient_task_list', {'items': patients,
                                                           'section': 'patient',
                                                           'username': 'norah',
                                                           'urls': helpers.URLS},
            context=self.context)

        # Create BS instances
        patient_list_string = ""
        for patient in patients:
           patient_list_string += helpers.PATIENT_LIST_ITEM.format(patient['url'],
                                                                   patient['deadline_time'],
                                                                   patient['full_name'],
                                                                   patient['ews_score'],
                                                                   patient['trend_icon'],
                                                                   patient['location'],
                                                                   patient['parent_location'])
        example_html = helpers.PATIENT_LIST_HTML.format(patient_list_string)

        get_patients_bs = str(BeautifulSoup(get_patients_html)).replace('\n', '')
        example_patients_bs = str(BeautifulSoup(example_html)).replace('\n', '')

        # Assert that shit
        self.assertEqual(get_patients_bs,
                         example_patients_bs,
                         'DOM from Controller ain\'t the same as DOM from example')
