__author__ = 'colin'
from common import NHMobileCommonTest
import helpers
import re
import logging
_logger = logging.getLogger(__name__)

class AdhocObsTest(NHMobileCommonTest):

    def setUp(self):
        super(AdhocObsTest, self).setUp()

        # demo data
        demo_data = self.create_test_data(self.cr, self.uid)[0]
        self.nurse = demo_data['users']['nurse']

    def test_news_obs_form(self):
        cr, uid = self.cr, self.uid


        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, self.nurse['id'], [], context=self.context)[0]

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

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': [i for i in self.process_form_description(form_desc) if i['type'] is not 'meta'],
                                          'name': 'NEWS Observation',
                                          'patient': patient,
                                          'form': form,
                                          'section': 'patient',
                                          'username': self.nurse['display_name'],
                                          'urls': helpers.URLS},
                                         context=self.context)

        # Create BS instances
        obs_form_string = self.process_test_form(form_desc)

        obs_string = helpers.BASE_OBS.format(patient_url=patient['url'],
                                             patient_name=patient['name'],
                                             patient_id=patient['id'],
                                             task_id=patient['id'],
                                             hidden_task_id='',
                                             form_task_id='',
                                             obs_type='ews',
                                             form_source='patient',
                                             form_ajax_action='json_patient_form_action',
                                             form_action='/mobile/patient/submit/ews/{pid}'.format(pid=patient['id']),
                                             content=obs_form_string,
                                             task_url=form['action'],
                                             timestamp=0)

        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected='', patient_selected=' class="selected"', content=obs_string)


        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                         'DOM from Controller ain\'t the same as DOM from example')
