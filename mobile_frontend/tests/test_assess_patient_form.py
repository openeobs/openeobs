__author__ = 'colin'
from openerp.tests import common
import openerp.modules.registry
from BeautifulSoup import BeautifulSoup
from helpers import URLS as urls
import re
import datetime
import helpers


class AssessPatientTest(common.SingleTransactionCase):

    def setUp(self):
        super(AssessPatientTest, self).setUp()

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

    def test_assess_patient_form(self):
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

        # Grab the NEWS Obs task from task list
        task_api = self.registry['nh.clinical.api.external']

        ews_id = [a for a in task_api.get_activities(cr, norah_user, [], context=self.context) if "NEWS" in a['summary']][0]['id']
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
            'flow_rate': 3,
            'startTimestamp': datetime.datetime.now().strftime('%s')
        }
        task_api.complete(cr, norah_user, ews_id, ews_data, context=self.context)

        task_id = [a for a in task_api.get_activities(cr, norah_user, [], context=self.context) if "Assess" in a['summary']][0]['id']

        # Take the Task
        activity_reg = self.registry['nh.activity']
        api_reg = self.registry['nh.clinical.api.external']
        task_id = int(task_id)
        task = activity_reg.read(cr, uid, task_id, ['user_id', 'data_model', 'summary', 'patient_id'], context=self.context)
        patient = dict()
        if task['patient_id']:
            patient_info = api_reg.get_patients(cr, uid, [task['patient_id'][0]], context=self.context)
            if len(patient_info) >0:
                patient_info = patient_info[0]
            patient['url'] = urls['single_patient'] + '{0}'.format(patient_info['id'])
            patient['name'] = patient_info['full_name']
            patient['id'] = patient_info['id']
        else:
            patient = False
        form = dict()
        form['action'] = urls['task_form_action']+'{0}'.format(task_id)
        form['type'] = task['data_model']
        form['task-id'] = int(task_id)
        form['patient-id'] = task['patient_id'][0]
        form['source'] = "task"
        form['start'] = '0'
        #if task.get('user_id') and task['user_id'][0] != new_uid:
        if task.get('user_id') and task['user_id'][0] != norah_user:
            self.fail('Task is already taken by another user')
        try:
            task_api.assign(cr, uid, task_id, {'user_id': norah_user}, context=self.context)
        except Exception:
            self.fail("Wasn't able to take Task")

        # Grab the form Def and compile the data to send to template
        obs_reg = self.registry[task['data_model']]
        form_desc = obs_reg.get_form_description(cr, uid, task['patient_id'][0], context=self.context)
        cancellable = obs_reg.is_cancellable(cr, uid, context=self.context)
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
        get_tasks_html = view_obj.render(cr, uid, 'mobile_frontend.notification_confirm_cancel', {'name': task['summary'],
                                                                                       'inputs': form_desc,
                                                                                       'cancellable': cancellable,
                                                                                       'patient': patient,
                                                                                       'form': form,
                                                                                       'section': 'task',
                                                                                       'username': 'norah',
                                                                                       'urls': urls}, context=self.context)

        example_html = helpers.ASSESS_PATIENT_HTML.format(task_url=form['confirm_url'],
                                               patient_name=patient['name'],
                                               patient_id=patient['id'],
                                               task_id=task_id)

        get_tasks_bs = str(BeautifulSoup(get_tasks_html)).replace('\n', '')
        example_tasks_bs = str(BeautifulSoup(example_html)).replace('\n', '')

        # Assert that shit
        self.assertEqual(get_tasks_bs,
                         example_tasks_bs,
                         'DOM from Controller ain\'t the same as DOM from example')
