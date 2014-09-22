__author__ = 'colin'

import openerp.tests
import helpers

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)
def next_seed():
    global seed
    seed += 1
    return seed

class TestAjaxTakeCancel(openerp.tests.HttpCase):

    def setUp(self):
        super(TestAjaxTakeCancel, self).setUp()
        global cr, uid

        # set up database connection objects
        self.registry = openerp.modules.registry.RegistryManager.get('t4clinical_test')
        self.uid = 1
        self.host = 'http://localhost:8169'

        # set up pools
        self.patient = self.registry.get('t4.clinical.patient')
        self.patient_visits = self.registry.get('t4.clinical.patient.visit')
        self.tasks = self.registry.get('t4.clinical.task.base')
        self.users = self.registry.get('res.users')
        self.activities = self.registry.get('t4.activity')


    # test task taking and cancel taking via ajax
    def test_ajax_take_cancel(self):
        cr, uid = self.cr, self.uid

        # create a postgres save point so we can have changes available to phantom
        test_save_point = self.savepoint_create()

        # create environment
        api_demo = self.registry('t4.clinical.api.demo')
        api_demo.build_uat_env(cr, uid, patients=8, placements=4, ews=0, context=None)
        cr.commit()
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

        assigned_to = self.activities.read(cr, uid, task_id, [])

        self.phantom_js('/ajax_test/', cancel, 'document', login='norah', db='t4clinical_test')

        # rollback to save point cos otherwise them changes be made
        self.savepoint_rollback(test_save_point)

    def savepoint_create(self, name=None):
        next_seed()
        i = 0
        while i < 1000:
                name = name or fake.first_name().lower()
                self.cr.execute("savepoint %s" % name)
                break
        assert i < 1000, "Couldn't create savepoint after 1000 attempts!"

        return name

    def savepoint_rollback(self, name):
        self.cr.execute("rollback to savepoint %s" % name)
        return True

    def savepoint_release(self, name):
        self.cr.execute("release savepoint %s" % name)
        return True
