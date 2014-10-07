__author__ = 'colin'
from openerp.tests import common
import openerp.modules.registry
from BeautifulSoup import BeautifulSoup
import helpers
import re


class AdhocPBPObsTest(common.SingleTransactionCase):

    def setUp(self):
        super(AdhocPBPObsTest, self).setUp()

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

    def test_news_obs_form(self):
        cr, uid = self.cr, self.uid

        # create environment
        api_demo = self.registry('nh.clinical.api.demo')
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
        form['action'] = helpers.URLS['patient_form_action']+'{0}/{1}'.format('pbp', test_patient['id'])
        form['type'] = 'pbp'
        form['task-id'] = False
        form['patient-id'] = test_patient['id']
        form['source'] = "patient"
        form['start'] = '0'


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.pbp', context=self.context)
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
        get_tasks_html = view_obj.render(cr, uid, 'mobile_frontend.observation_entry',
                                         {'inputs': form_desc,
                                          'name': 'Postural Blood Pressure Observation',
                                          'patient': patient,
                                          'form': form,
                                          'section': 'patient',
                                          'username': 'norah',
                                          'urls': helpers.URLS},
                                         context=self.context)

        example_html = helpers.PBP_PATIENT_HTML.format(patient_url=patient['url'],
                                                       patient_name=patient['name'],
                                                       patient_id=patient['id'],
                                                       task_url=form['action'],
                                                       timestamp=0)

        get_tasks_bs = str(BeautifulSoup(get_tasks_html)).replace('\n', '')
        example_tasks_bs = str(BeautifulSoup(example_html)).replace('\n', '')

        # Assert that shit
        self.assertEqual(get_tasks_bs,
                         example_tasks_bs,
                         'DOM from Controller ain\'t the same as DOM from example')
