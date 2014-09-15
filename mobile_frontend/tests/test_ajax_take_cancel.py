__author__ = 'colin'

import openerp.tests
import helpers

class TestAjaxTakeCancel(openerp.tests.HttpCase):

    def setUp(self):
        super(TestAjaxTakeCancel, self).setUp()

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


    # test task taking and cancel taking via ajax
    def test_ajax_take_cancel(self):
        cr, uid = self.cr, self.uid

        # create environment
        api_demo = self.registry('t4.clinical.api.demo')
        api_demo.build_uat_env(cr, uid, patients=8, placements=4, context=None)

        # get a nurse user
        norah_user = self.users.search(cr, uid, [['login', '=', 'norah']])[0]

        self.context = {
            'lang': 'en_GB',
            'tz': 'Europe/London',
            'uid': 1
        }

        # Grab the NEWS Obs task from task list
        task_api = self.registry['t4.clinical.api.external']
        task_id = [a for a in task_api.get_activities(cr, norah_user, [], context=self.context) if "NEWS" in a['summary']][0]['id']

        take = helpers.TAKE_TASK_AJAX.format(task_id=task_id)
        cancel = helpers.CANCEL_TAKE_TASK_AJAX.format(task_id=task_id)

        self.phantom_js('/ajax_test/', take, 'document', login='norah')
        self.phantom_js('/ajax_test/', cancel, 'document', login='norah')
