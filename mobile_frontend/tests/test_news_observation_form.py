__author__ = 'colin'
from openerp.tests import common
import openerp.modules.registry
from BeautifulSoup import BeautifulSoup
import helpers
import re


class NewsObsTest(common.SingleTransactionCase):

    def setUp(self):
        super(NewsObsTest, self).setUp()

        # set up database connection objects
        self.registry = openerp.modules.registry.RegistryManager.get('t4clinical_test')
        self.uid = 1
        self.host = 'http://localhost:8169'

        # set up pools
        self.patient = self.registry.get('t4.clinical.patient')
        self.patient_visits = self.registry.get('t4.clinical.patient.visit')
        self.tasks = self.registry.get('t4.clinical.task.base')
        self.location = self.registry.get('t4.clinical.pos.delivery')
        self.location_type = self.registry.get('t4.clinical.pos.delivery.type')
        self.users = self.registry.get('res.users')

    def test_news_obs_form(self):
        cr, uid = self.cr, self.uid

        # Create test patient
        env_pool = self.registry('t4.clinical.demo.env')
        config = {'patient_qty': 1}
        env_id = env_pool.create(cr, uid, config)
        adt_user_id = env_pool.get_adt_user_ids(cr, uid, env_id)[0]
        register_activity = env_pool.create_complete(cr,
                                                     adt_user_id,
                                                     env_id,
                                                     't4.clinical.adt.patient.register')
        admit_data = env_pool.fake_data(cr, uid, env_id, 't4.clinical.adt.patient.admit')
        admit_data['other_identifier'] = register_activity.data_ref.other_identifier
        admit_activity = env_pool.create_complete(cr,
                                                  adt_user_id,
                                                  env_id,
                                                  't4.clinical.adt.patient.admit',
                                                  {},
                                                  admit_data)
        # test admission
        admission_activity = [a for a in admit_activity.created_ids if a.data_model == 't4.clinical.patient.admission']
        assert len(admission_activity) == 1, "Created admission activity: %s" % admission_activity
        admission_activity = admission_activity[0]
        assert admission_activity.state == 'completed'
        #test placement
        placement_activity = [a for a in admission_activity.created_ids if a.data_model ==
                              't4.clinical.patient.placement']
        assert len(placement_activity) == 1, "Created patient.placement activity: %s" % placement_activity
        placement_activity = placement_activity[0]
        assert placement_activity.state == 'new'
        assert placement_activity.pos_id.id == register_activity.pos_id.id
        assert placement_activity.patient_id.id == register_activity.patient_id.id
        assert placement_activity.data_ref.patient_id.id == placement_activity.patient_id.id
        assert placement_activity.data_ref.suggested_location_id
        assert placement_activity.location_id.id == placement_activity.data_ref.suggested_location_id.id

        self.context = {
            'lang': 'en_GB',
            'tz': 'Europe/London',
            'uid': 1
        }

        # Grab the NEWS Obs task from task list
        task_api = self.registry['t4.clinical.api.external']
        task_id = [a for a in task_api.get_activities(cr, adt_user_id, [], context=self.context) if "NEWS" in a['summary']][0]['id']

        # Take the Task
        activity_reg = self.registry['t4.activity']
        task = activity_reg.read(cr, uid, task_id, ['user_id', 'data_model', 'summary'], context=self.context)
        patient = dict()
        patient['url'] = helpers.URLS['single_patient'] + '{0}'.format(2)
        patient['name'] = 'Colin is Awesome'
        form = dict()
        form['action'] = helpers.URLS['task_form_action']+'{0}'.format(task_id)
        form['type'] = task['data_model']
        form['source-id'] = int(task_id)
        form['source'] = "task"
        form['start'] = '0'
        #if task.get('user_id') and task['user_id'][0] != new_uid:
        if task.get('user_id') and task['user_id'][0] != adt_user_id:
            self.fail('Task is already taken by another user')
        try:
            task_api.assign(cr, uid, task_id, {'user_id': adt_user_id}, context=self.context)
        except Exception:
            self.fail("Wasn't able to take Task")

        # Grab the form Def and compile the data to send to template
        obs_reg = self.registry[task['data_model']]
        form_desc = obs_reg._form_description
        form['type'] = re.match(r't4\.clinical\.patient\.observation\.(.*)', task['data_model']).group(1)
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
                                          'name': task['summary'],
                                          'patient': patient,
                                          'form': form,
                                          'section': 'task',
                                          'username': 'norah',
                                          'urls': helpers.URLS},
                                         context=self.context)

        # Create BS instances
        example_html = helpers.NEWS_OBS.format(patient['url'],
                                               patient['name'],
                                               task_id, 0)

        get_tasks_bs = str(BeautifulSoup(get_tasks_html)).replace('\n', '')
        example_tasks_bs = str(BeautifulSoup(example_html)).replace('\n', '')

        # Assert that shit
        self.assertEqual(get_tasks_bs,
                         example_tasks_bs,
                         'DOM from Controller ain\'t the same as DOM from example')
