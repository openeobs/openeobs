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
        self.location = self.registry.get('t4.clinical.location')
        #self.location_type = self.registry.get('t4.clinical.location.type')
        self.users = self.registry.get('res.users')
        self.activities = self.registry.get('t4.activity')

    def test_task_list(self):
        cr, uid = self.cr, self.uid

        # create environment
        api_demo = self.registry('t4.clinical.api.demo')
        api_demo.build_uat_env(cr, uid, patients=8, placements=4, context=None)

        # get a nurse user
        norah_user = self.users.search(cr, uid, [['login', '=', 'norah']])[0]

        # assign nurse to ward

        self.context = {
            'lang': 'en_GB',
            'tz': 'Europe/London',
            'uid': norah_user
        }

        # Call controller
        task_api = self.registry['t4.clinical.api.external']
        tasks = task_api.get_activities(cr, norah_user, [], context=self.context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(helpers.URLS['single_task'], task['id'])
            task['color'] = 'level-one'
            task['trend_icon'] = 'icon-{0}-arrow'.format(task['ews_trend'])
            task['summary'] = task['summary'] if task.get('summary') else False
            task['notification_string'] = '<i class="icon-alert"></i>' if task['notification']==True else ''

        view_obj = self.registry("ir.ui.view")
        get_tasks_html = view_obj.render(
            cr, uid, 'mobile_frontend.patient_task_list', {'items': tasks,
                                                           'section': 'task',
                                                           'username': 'norah',
                                                           'urls': helpers.URLS},
            context=self.context)

        # Create BS instances
        task_list_string = ""
        for task in tasks:
            task_list_string += helpers.TASK_LIST_ITEM.format(task['url'],
                                                              task['deadline_time'],
                                                              task['notification_string'],
                                                              task['full_name'],
                                                              task['ews_score'],
                                                              task['trend_icon'],
                                                              task['location'],
                                                              task['parent_location'],
                                                              task['summary'])
        example_html = helpers.TASK_LIST_HTML.format(task_list=task_list_string)

        get_tasks_bs = str(BeautifulSoup(get_tasks_html)).replace('\n', '')
        example_tasks_bs = str(BeautifulSoup(example_html)).replace('\n', '')

        # Assert that shit
        self.assertEqual(get_tasks_bs,
                         example_tasks_bs,
                         'DOM from Controller ain\'t the same as DOM from example')
