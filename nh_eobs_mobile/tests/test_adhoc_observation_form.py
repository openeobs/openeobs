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

        form = self.create_test_patient_form(test_patient, 'ews', 'ews')
        patient = self.create_test_patient_patient(test_patient)

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


    def test_blood_product_obs_form(self):
        cr, uid = self.cr, self.uid


        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, self.nurse['id'], [], context=self.context)[0]

        form = self.create_test_patient_form(test_patient, 'blood_product', 'blood-product')
        patient = self.create_test_patient_patient(test_patient)


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.blood_product', context=self.context)

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': [i for i in self.process_form_description(form_desc) if i['type'] is not 'meta'],
                                          'name': 'Blood Product Observation',
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
                                             obs_type='blood_product',
                                             form_source='patient',
                                             form_ajax_action='json_patient_form_action',
                                             form_action='/mobile/patient/submit/blood-product/{pid}'.format(pid=patient['id']),
                                             content=obs_form_string,
                                             task_url=form['action'],
                                             timestamp=0)

        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected='', patient_selected=' class="selected"', content=obs_string)


        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')


    def test_blood_sugar_obs_form(self):
        cr, uid = self.cr, self.uid


        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, self.nurse['id'], [], context=self.context)[0]

        form = self.create_test_patient_form(test_patient, 'blood_sugar', 'blood-sugar')
        patient = self.create_test_patient_patient(test_patient)


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.blood_sugar', context=self.context)

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': [i for i in self.process_form_description(form_desc) if i['type'] is not 'meta'],
                                          'name': 'Blood Sugar Observation',
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
                                             obs_type='blood_sugar',
                                             form_source='patient',
                                             form_ajax_action='json_patient_form_action',
                                             form_action='/mobile/patient/submit/blood-sugar/{pid}'.format(pid=patient['id']),
                                             content=obs_form_string,
                                             task_url=form['action'],
                                             timestamp=0)

        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected='', patient_selected=' class="selected"', content=obs_string)


        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')


    def test_gcs_form(self):
        cr, uid = self.cr, self.uid


        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, self.nurse['id'], [], context=self.context)[0]

        form = self.create_test_patient_form(test_patient, 'gcs', 'gcs')
        patient = self.create_test_patient_patient(test_patient)


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.gcs', context=self.context)

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': [i for i in self.process_form_description(form_desc) if i['type'] is not 'meta'],
                                          'name': 'GCS Observation',
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
                                             obs_type='gcs',
                                             form_source='patient',
                                             form_ajax_action='json_patient_form_action',
                                             form_action='/mobile/patient/submit/gcs/{pid}'.format(pid=patient['id']),
                                             content=obs_form_string,
                                             task_url=form['action'],
                                             timestamp=0)

        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected='', patient_selected=' class="selected"', content=obs_string)


        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')

    def test_height_form(self):
        cr, uid = self.cr, self.uid


        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, self.nurse['id'], [], context=self.context)[0]

        form = self.create_test_patient_form(test_patient, 'height', 'height')
        patient = self.create_test_patient_patient(test_patient)


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.height', context=self.context)

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': [i for i in self.process_form_description(form_desc) if i['type'] is not 'meta'],
                                          'name': 'Height Observation',
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
                                             obs_type='height',
                                             form_source='patient',
                                             form_ajax_action='json_patient_form_action',
                                             form_action='/mobile/patient/submit/height/{pid}'.format(pid=patient['id']),
                                             content=obs_form_string,
                                             task_url=form['action'],
                                             timestamp=0)

        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected='', patient_selected=' class="selected"', content=obs_string)


        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')

    def test_weight_form(self):
        cr, uid = self.cr, self.uid


        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, self.nurse['id'], [], context=self.context)[0]

        form = self.create_test_patient_form(test_patient, 'weight', 'weight')
        patient = self.create_test_patient_patient(test_patient)


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.weight', context=self.context)

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': [i for i in self.process_form_description(form_desc) if i['type'] is not 'meta'],
                                          'name': 'Weight Observation',
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
                                             obs_type='weight',
                                             form_source='patient',
                                             form_ajax_action='json_patient_form_action',
                                             form_action='/mobile/patient/submit/weight/{pid}'.format(pid=patient['id']),
                                             content=obs_form_string,
                                             task_url=form['action'],
                                             timestamp=0)

        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected='', patient_selected=' class="selected"', content=obs_string)


        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')

    def test_pbp_form(self):
        cr, uid = self.cr, self.uid


        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, self.nurse['id'], [], context=self.context)[0]

        form = self.create_test_patient_form(test_patient, 'pbp', 'pbp')
        patient = self.create_test_patient_patient(test_patient)


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.pbp', context=self.context)

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': [i for i in self.process_form_description(form_desc) if i['type'] is not 'meta'],
                                          'name': 'Postural Blood Pressure Observation',
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
                                             obs_type='pbp',
                                             form_source='patient',
                                             form_ajax_action='json_patient_form_action',
                                             form_action='/mobile/patient/submit/pbp/{pid}'.format(pid=patient['id']),
                                             content=obs_form_string,
                                             task_url=form['action'],
                                             timestamp=0)

        # absolutely shocking hack
        obs_string = obs_string.replace('<div class="block obsField" id="parent_systolic_sitting">', '<h3 class="block">Lying/Sitting Blood Pressure</h3><div class="block obsField" id="parent_systolic_sitting">')
        obs_string = obs_string.replace('<div class="block obsField valHide" id="parent_systolic_standing">','<h3 class="block valHide" id="standing_title">Standing Blood Pressure</h3><div class="block obsField valHide" id="parent_systolic_standing">')
        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected='', patient_selected=' class="selected"', content=obs_string)


        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')

    def test_stools_form(self):
        cr, uid = self.cr, self.uid


        patient_api = self.registry['nh.eobs.api']
        test_patient = patient_api.get_patients(cr, self.nurse['id'], [], context=self.context)[0]

        form = self.create_test_patient_form(test_patient, 'stools', 'stools')
        patient = self.create_test_patient_patient(test_patient)


        form_desc = patient_api.get_form_description(cr, uid, test_patient['id'], 'nh.clinical.patient.observation.stools', context=self.context)

        view_obj = self.registry("ir.ui.view")
        generated_html = view_obj.render(cr, uid, 'nh_eobs_mobile.observation_entry',
                                         {'inputs': [i for i in self.process_form_description(form_desc) if i['type'] is not 'meta'],
                                          'name': 'Stools Observation',
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
                                             obs_type='stools',
                                             form_source='patient',
                                             form_ajax_action='json_patient_form_action',
                                             form_action='/mobile/patient/submit/stools/{pid}'.format(pid=patient['id']),
                                             content=obs_form_string,
                                             task_url=form['action'],
                                             timestamp=0)

        # absolutely shocking hack
        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected='', patient_selected=' class="selected"', content=obs_string)


        # Assert that shit
        self.assertTrue(self.compare_doms_stools(generated_html, example_html),
                        'DOM from Controller ain\'t the same as DOM from example')