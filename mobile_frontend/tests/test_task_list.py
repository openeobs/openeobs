__author__ = 'colin'
from openerp.tests import common
import openerp.modules.registry
from BeautifulSoup import BeautifulSoup
import helpers


class TaskListTest(common.SingleTransactionCase):

    def setUp(self):
        super(TaskListTest, self).setUp()

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

    def test_patient_list(self):
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

        # Call controller
        task_api = self.registry['t4.clinical.api.external']
        tasks = task_api.get_activities(cr, adt_user_id, [], context=self.context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(helpers.URLS['single_task'], task['id'])
            task['color'] = 'level-one'
            task['trend_icon'] = 'icon-{0}-arrow'.format(task['ews_trend'])
            task['summary'] = task['summary'] if task.get('summary') else False

        view_obj = self.registry("ir.ui.view")
        get_tasks_html = view_obj.render(
            cr, uid, 'mobile_frontend.patient_task_list', {'items': tasks[:1],
                                                           'section': 'task',
                                                           'username': 'norah',
                                                           'urls': helpers.URLS},
            context=self.context)

        # Create BS instances
        example_task = tasks[0]
        example_html = helpers.TASK_LIST_HTML.format(example_task['url'],
                                                     example_task['deadline_time'],
                                                     example_task['full_name'],
                                                     example_task['ews_score'],
                                                     example_task['trend_icon'],
                                                     example_task['location'],
                                                     example_task['parent_location'],
                                                     example_task['summary'])

        get_tasks_bs = str(BeautifulSoup(get_tasks_html)).replace('\n', '')
        example_tasks_bs = str(BeautifulSoup(example_html)).replace('\n', '')

        # Assert that shit
        self.assertEqual(get_tasks_bs,
                         example_tasks_bs,
                         'DOM from Controller ain\'t the same as DOM from example')
