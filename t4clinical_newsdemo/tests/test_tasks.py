from openerp.tests import common
from datetime import datetime as dt
from openerp.osv import orm
from dateutil.relativedelta import relativedelta as rd


class TestTasks(common.SingleTransactionCase):

    def setUp(self):

        cr, uid = self.cr, self.uid
        
        self.now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        self.tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                
        self.task_pool = self.registry('t4.clinical.task')
        self.user_pool = self.registry('res.users')

        super(TestTasks, self).setUp()

    def test_nurse_can_see_tasks(self):
        cr, uid = self.cr, self.uid

        self.task_pool.create_task()

        nurse_id = self.user_pool.search(cr, uid, [('login', '=', 'winifred')])[0]
        print nurse_id

        tasks = self.task_pool.search(cr, nurse_id, [])
        self.assertTrue(tasks)



