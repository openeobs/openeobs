__author__ = 'colin'
from common import NHMobileCommonTest
import helpers
import re
import logging
_logger = logging.getLogger(__name__)

class ObsTest(NHMobileCommonTest):

    def setUp(self):
        super(ObsTest, self).setUp()

        # demo data
        demo_data = self.create_test_data(self.cr, self.uid)[0]
        self.nurse = demo_data['users']['nurse']

    def test_news_obs_form(self):
        cr, uid = self.cr, self.uid

        task_id = [a for a in self.api.get_activities(cr, self.nurse['id'], [], context=self.context) if "NEWS" in a['summary']][0]['id']

        # Take the Task
        task_id = int(task_id)
        task = self.activity.read(cr, uid, task_id, ['user_id', 'data_model', 'summary', 'patient_id'],
                                  context=self.context)
        patient = dict()
        if task['patient_id']:
            patient_info = self.api.get_patients(cr, uid, [task['patient_id'][0]], context=self.context)
            if len(patient_info) >0:
                patient_info = patient_info[0]
            patient['url'] = helpers.URLS['single_patient'] + '{0}'.format(patient_info['id'])
            patient['name'] = patient_info['full_name']
            patient['id'] = patient_info['id']
        else:
            patient = False
        form = dict()
        form['action'] = helpers.URLS['task_form_action']+'{0}'.format(task_id)
        form['type'] = task['data_model']
        form['task-id'] = int(task_id)
        form['patient-id'] = task['patient_id'][0]
        form['source'] = "task"
        form['start'] = '0'
        #if task.get('user_id') and task['user_id'][0] != new_uid:
        if task.get('user_id') and task['user_id'][0] != self.nurse['id']:
            self.fail('Task is already taken by another user')
        try:
            self.api.assign(cr, uid, task_id, {'user_id': self.nurse['id']}, context=self.context)
        except Exception:
            self.fail("Wasn't able to take Task")

        # Grab the form Def and compile the data to send to template
        obs_reg = self.registry[task['data_model']]
        form_desc = obs_reg.get_form_description(cr, uid, task['patient_id'][0], context=self.context)
        form['type'] = re.match(r'nh\.clinical\.patient\.observation\.(.*)', task['data_model']).group(1)
        for form_input in form_desc:
            if form_input['type'] in ['float', 'integer']:
                form_input['step'] = 0.1 if form_input['type'] is 'float' else 1
                form_input['type'] = 'number'
                form_input['number'] = True
                form_input['info'] = ''
                form_input['errors'] = ''
                form_input['min'] = str(form_input['min'])
            elif form_input['type'] == 'selection':
                form_input['selection_options'] = []
                form_input['info'] = ''
                form_input['errors'] = ''
                for option in form_input['selection']:
                    opt = dict()
                    opt['value'] = '{0}'.format(option[0])
                    opt['label'] = option[1]
                    form_input['selection_options'].append(opt)

        generated_html = self.render_template(cr, uid, 'nh_eobs_mobile.observation_entry',
                                              {'inputs': [i for i in form_desc if i['type'] is not 'meta'],
                                               'name': task['summary'],
                                               'patient': patient,
                                               'form': form,
                                               'section': 'task',
                                               'username': self.nurse['display_name'],
                                               'urls': helpers.URLS})

        # Create BS instances
        obs_form_string = ""
        for form_field in form_desc:
            if form_field['type'] is 'number':
                if 'validation' in form_field:
                    for validation in form_field['validation']:
                        validation['condition']['operator'] = validation['condition']['operator'].replace('<', '&lt;').replace('>', '&gt;')
                obs_form_string += helpers.OBS_INPUT.format(
                    name=form_field['name'],
                    label=form_field['label'],
                    type=form_field['type'],
                    min=form_field['min'],
                    max=form_field['max'],
                    step=form_field['step'],
                    hidden_block=' valHide' if form_field['initially_hidden'] else '',
                    hidden_input=' class="exclude"' if form_field['initially_hidden'] else '',
                    data_validation=' data-validation="{0}"'.format(form_field['validation']) if 'validation' in form_field else ''
                )
            elif form_field['type'] is 'selection':
                options_string = ''
                for option in form_field['selection_options']:
                    options_string += helpers.OPTION.format(value=option['value'], name=option['label'])
                obs_form_string += helpers.OBS_SELECT.format(
                    name=form_field['name'],
                    label=form_field['label'],
                    onchange=' data-onchange="{0}"'.format(form_field['on_change']) if 'on_change' in form_field else '',
                    options=options_string,
                    hidden_block=' valHide' if form_field['initially_hidden'] else '',
                    hidden_input=' class="exclude"' if form_field['initially_hidden'] else '',
                )


        obs_string = helpers.BASE_OBS.format(patient_url=patient['url'],
                                             patient_name=patient['name'],
                                             patient_id=patient['id'],
                                             task_id=task_id,
                                             content=obs_form_string,
                                             timestamp=0)

        example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected=' class="selected"', patient_selected='', content=obs_string)

        # Assert that shit
        self.assertTrue(self.compare_doms(generated_html, example_html),
                         'DOM from Controller ain\'t the same as DOM from example')
