__author__ = 'colin'
from openerp.tests import common
import openerp.modules.registry
import xml.etree.ElementTree as et
import helpers
import re
import logging
_logger = logging.getLogger(__name__)

class AdhocNewsObsTest(common.SingleTransactionCase):

    def setUp(self):
        super(AdhocNewsObsTest, self).setUp()

        # set up database connection objects
        self.uid = 1
        self.host = 'http://localhost:%s' % openerp.tools.config['xmlrpc_port']

        # set up pools
        self.patient = self.registry.get('nh.clinical.patient')
        self.patient_visits = self.registry.get('nh.clinical.patient.visit')
        self.tasks = self.registry.get('nh.clinical.task.base')
        self.location = self.registry.get('nh.clinical.pos.delivery')
        self.location_type = self.registry.get('nh.clinical.pos.delivery.type')
        self.users = self.registry.get('res.users')

    def test_news_obs_form(self):
        cr, uid = self.cr, self.uid

        # create environment
        api_demo = self.registry('nh.clinical.api.demo')
        if not api_demo.demo_data_loaded(cr, uid):
            _logger.warn("Demo data is not loaded and this test relies on it! Skiping test.")
            return
        api_demo.build_uat_env(cr, uid, patients=8, placements=4, ews=0, context=None)

        # get a nurse user
        norah_user = self.users.search(cr, uid, [['login', '=', 'norah']])[0]

        self.context = {
            'lang': 'en_GB',
            'tz': 'Europe/London',
            'uid': 1
        }

        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, norah_user, [], context=self.context)[0]

        patient = dict()
        if test_patient:
            patient['url'] = helpers.URLS['single_patient'] + '{0}'.format(test_patient['id'])
            patient['name'] = test_patient['full_name']
            patient['id'] = test_patient['id']
        else:
            patient = False
        form = dict()
        form['action'] = helpers.URLS['patient_form_action']+'{0}/{1}'.format('ews', test_patient['id'])
        form['type'] = 'ews'
        form['task-id'] = False
        form['patient-id'] = test_patient['id']
        form['source'] = "patient"
        form['start'] = '0'


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.ews', context=self.context)
        for form_input in form_desc:
            if form_input['type'] in ['float', 'integer']:
                form_input['step'] = 0.1 if form_input['type'] is 'float' else 1
                form_input['type'] = 'number'
                form_input['number'] = True
                form_input['info'] = ''
                form_input['errors'] = ''
            elif form_input['type'] == 'selection':
                form_input['selection_options'] = []
                form_input['info'] = ''
                form_input['errors'] = ''
                for option in form_input['selection']:
                    opt = dict()
                    opt['value'] = '{0}'.format(option[0])
                    opt['label'] = option[1]
                    form_input['selection_options'].append(opt)

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': form_desc,
                                          'name': 'NEWS Observation',
                                          'patient': patient,
                                          'form': form,
                                          'section': 'patient',
                                          'username': 'norah',
                                          'urls': helpers.URLS},
                                         context=self.context)

        # Create BS instances
        devices_string = ""
        for device in [v['selection'] for v in form_desc if v['name'] is 'device_id'][0]:
            devices_string += helpers.DEVICE_OPTION.format(device_id=device[0], device_name=device[1])
        example_html = helpers.NEWS_PATIENT_HTML.format(patient_url=patient['url'],
                                                        patient_name=patient['name'],
                                                        patient_id=patient['id'],
                                                        device_options=devices_string,
                                                        task_url=form['action'],
                                                        timestamp=0)

        generated_tree = et.tostring(et.fromstring(generated_html)).replace('\n', '').replace(' ', '')  # str(BeautifulSoup(get_patients_html)).replace('\n', '')
        example_tree = et.tostring(et.fromstring(example_html)).replace('\n', '').replace(' ', '')  # str(Beauti

        # Assert that shit
        self.assertEqual(generated_tree,
                         example_tree,
                         'DOM from Controller ain\'t the same as DOM from example')
