from common import NHMobileCommonTest
import helpers
import re
import logging
import datetime
from helpers import URLS as urls
_logger = logging.getLogger(__name__)

class NotificationTest(NHMobileCommonTest):

	def setUp(self):
		super(NotificationTest, self).setUp()
		# demo data
		demo_data = self.create_test_data(self.cr, self.uid)[0]
		self.nurse = demo_data['users']['nurse']

	def test_access_patient_form(self):
		ews_id = [a for a in self.api.get_activities(self.cr, self.nurse['id'], [], context=self.context) if "NEWS" in a['summary']][0]['id']
		ews_data = {
		'respiration_rate': 20,
		'indirect_oxymetry_spo2': 99,
		'body_temperature': 37.5,
		'blood_pressure_systolic': 120,
		'blood_pressure_diastolic': 80,
		'pulse_rate': 80,
		'avpu_text': 'A',
		'oxygen_administration_flag': True,
		'device_id': 36,
		'flow_rate': 3
		}
		self.api.complete(self.cr, self.nurse['id'], ews_id, ews_data, context=self.context)
		task_id = [a for a in self.api.get_activities(self.cr, self.nurse['id'], [], context=self.context) if "Assess" in a['summary']][0]['id']

		# Take the Task
		task_id = int(task_id)
		task = self.activity.read(self.cr, self.uid, task_id, ['user_id', 'data_model', 'summary', 'patient_id'], context=self.context)
		patient = dict()
		if task['patient_id']:
			patient_info = self.api.get_patients(self.cr, self.uid, [task['patient_id'][0]], context=self.context)
			if len(patient_info) >0:
				patient_info = patient_info[0]
			patient['url'] = urls['single_patient'] + '{0}'.format(patient_info['id'])
			patient['name'] = patient_info['full_name']
			patient['id'] = patient_info['id']
		else:
			patient = False
		form = dict()
		form['action'] = urls['confirm_clinical_notification']+'{0}'.format(task_id)
		form['type'] = task['data_model']
		form['task-id'] = int(task_id)
		form['patient-id'] = task['patient_id'][0]
		form['source'] = "task"
		form['start'] = '0'
		if task.get('user_id') and task['user_id'][0] != self.nurse['id']:
			self.fail('Task is already taken by another user')
		try:
			self.api.assign(self.cr, self.uid, task_id, {'user_id': self.nurse['id']}, context=self.context)
		except Exception:
			self.fail("Wasn't able to take Task")

		obs_reg = self.registry[task['data_model']]
		form_desc = obs_reg.get_form_description(self.cr, self.uid, task['patient_id'][0], context=self.context)
		cancellable = obs_reg.is_cancellable(self.cr, self.uid, context=self.context)
		form['confirm_url'] = "{0}{1}".format(urls['confirm_clinical_notification'], task_id)
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
		if cancellable:
			form['cancel_url'] = "{0}{1}".format(urls['cancel_clinical_notification'], task_id)
		form['type'] = re.match(r'nh\.clinical\.notification\.(.*)', task['data_model']).group(1)
		view_obj = self.registry("ir.ui.view")
		generated_html = view_obj.render(self.cr, self.uid, 'nh_eobs_mobile.notification_confirm_cancel', {'name': task['summary'],
		                                                                                                   'inputs': form_desc,
		                                                                                                   'cancellable': cancellable,
		                                                                                                   'patient': patient,
		                                                                                                   'form': form,
		                                                                                                   'section': 'task',
		                                                                                                   'username': self.nurse['display_name'],
		                                                                                                   'urls': urls}, context=self.context)

		notification_html = helpers.ASSESS_PATIENT_HTML.format(task_url=form['confirm_url'],
		                                                       patient_name=patient['name'],
		                                                       patient_id=patient['id'],
		                                                       patient_url=patient['url'],
		                                                       task_id=task_id,
		                                                       form_action=form['action'],
		                                                       form_ajax_action='confirm_clinical_notification',
		                                                       form_ajax_args=task_id,
		                                                       obs_type='assessment',
		                                                       form_source='task',
		                                                       form_task_id=' task-id="{tid}"'.format(tid=task_id))

		example_html = helpers.BASE_HTML.format(user=self.nurse['display_name'], task_selected=' class="selected"', patient_selected='', content=notification_html)
		self.assertTrue(self.compare_doms(generated_html, example_html),
		                'DOM from Controller ain\'t the same as DOM from example')