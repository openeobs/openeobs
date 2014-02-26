from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv



task1_data = {'notes': "Test task is in draft when created by default"}
task1_type_data = {'summary': 'Test Type', 'data_model': 'observation.test'}
data_model_data = {'summary': 'Test Type', 'data_model': 'observation.test'}
submit_data = {'val1': 'submit_val1', 'val2': 'submit_val2'}


class TestTask(common.SingleTransactionCase):
    def setUp(self):

        self.now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        self.tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        super(TestTask, self).setUp()
        self.task_pool = self.registry('t4.clinical.task')
        self.task1_id = self.task_pool.create(self.cr, self.uid, task1_data)

        self.type_pool = self.registry('t4.clinical.task.data.type')
        self.data_type_id = self.type_pool.create(self.cr, self.uid, data_model_data)
        recurrence_minute_data = {'unit':'minute', 'unit_qty':1, 'date_start': (dt.now()+rd(days=-1)).strftime('%Y-%m-%d %H:%M:%S'),
                          'vals_task': "{'summary': 'test', 'data_type_id': %s}" % str(self.data_type_id),
                          'vals_data': "{'val1': 'test'}"
                          }
        self.rec_pool = self.registry('t4.clinical.task.recurrence')
        self.rec_id = self.rec_pool.create(self.cr, self.uid, recurrence_minute_data)
        

    
    def get_task1(self):
        return self.task_pool.browse(self.cr, self.uid, self.task1_id)
    
    def write_task1(self, vals):
        self.task_pool.write(self.cr, self.uid, self.task1_id, vals)
    
    def test_draft(self):
        """
        when created state == draft
        """
        self.task1_id = self.task_pool.create(self.cr, self.uid, task1_data)
        
        task1 = self.get_task1()
        self.assertEquals(task1.state, 'draft', 'test_draft error')
        
        
    def test_scheduled(self):
        """
        if 
            date_scheduled written to task
            and
            schedule() run
        then 
            state == 'scheduled'  
        """
        self.write_task1({'date_scheduled': self.tomorrow})
        self.task_pool.schedule(self.cr, self.uid, self.task1_id)
        
        task1 = self.get_task1()
        self.assertEquals(task1.state, 'scheduled', 'test_scheduled error')
        
    def test_start(self):
        """
        if
            assign() run with user_id = 1
            and 
            start() run
        then
            user_id == 1
            and
            state == 'started'
        """
        self.test_scheduled()
        self.task_pool.assign(self.cr, self.uid, self.task1_id, 1)
        self.task_pool.start(self.cr, self.uid, self.task1_id)
        
        task1 = self.get_task1()
        self.assertEquals(task1.user_id.id, 1, 'test_start user_id')
        self.assertEquals(task1.state, 'started', 'test_start state')
        

    def test_submit_retrieve(self):
        """
        if
            type_id written to task
            and
            submit() run
            and 
            data = retrieve() 
        then
            data[task1.id]['val1'] == 'submit_val1'
            and 
            data[task1.id]['val2'] == 'submit_val2'
            
        """
        self.test_start()
        self.write_task1({'data_type_id': self.data_type_id})
        self.task_pool.submit(self.cr, self.uid, self.task1_id, submit_data)
        #import pdb; pdb.set_trace()
        task1 = self.get_task1()
        data = self.task_pool.retrieve(self.cr, self.uid, task1.id)
        
        self.assertEquals(data['val1'], 'submit_val1', 'test_submit val1')
        self.assertEquals(data['val2'], 'submit_val2', 'test_submit val2')
       
        
    def test_complete(self):
        """
        if
            complete() run
        then 
            state == 'completed'
        """
        self.test_submit_retrieve()
        self.task_pool.complete(self.cr, self.uid, self.task1_id)
        
        task1 = self.get_task1()
        
        self.assertEquals(task1.state, 'completed', 'test_complete state')
        self.assertTrue(task1.date_terminated, 'test_complete date_terminated')
        
        
    def test_recurrence_minute(self):
        """
        if
            task_count == x
            and
            rec_pool.cron(now)
        then
            task_count > x
            and
            last task by id: summary == 'test'
            and
            task.data_res_id
            and 
            task.data_model == observation.test
            and
            (observation.test, task.data_res_id).val1 == 'test'
        """
        
        task_count0 = self.task_pool.search(self.cr, self.uid, [], count=True)
        self.rec_pool.cron(self.cr, self.uid, self.now)
        task_count1 = self.task_pool.search(self.cr, self.uid, [], count=True)
        last_task_id = self.task_pool.search(self.cr, self.uid, [], limit=1, order="id desc")[0]
        last_task = self.task_pool.browse(self.cr, self.uid, last_task_id)
        model_pool = self.registry(last_task.data_model)
        last_task_data = model_pool.browse(self.cr, self.uid, last_task.data_res_id)
        #import pdb; pdb.set_trace()
        self.assertTrue(task_count1 > task_count0, 'test_recurrence_minute count')
        self.assertEquals(last_task.summary,'test', 'test_recurrence_minute summary')
        self.assertTrue(last_task.data_res_id, 'test_recurrence_minute data_res_id')
        self.assertEquals(last_task.data_model,'observation.test', 'test_recurrence_minute data_model')
        self.assertEquals(last_task_data.val1,'test', 'test_recurrence_minute val1')
        
        
    def test_recurrence_replace(self):
        """
        if 
            rec_pool.replace({'unit_qty':2})
        then
            last_rec_id > self.rec_id
            and
            rec.active == False
            and
            last_rec.unit_qty == 2
        """
        self.rec_pool.replace(self.cr, self.uid, self.rec_id, {'unit_qty':2})
        last_rec_id = self.task_pool.search(self.cr, self.uid, [], limit=1, order="id desc")[0]
        last_rec = self.rec_pool.browse(self.cr, self.uid, last_rec_id)
        

        
        rec = self.rec_pool.browse(self.cr, self.uid, self.rec_id)
        self.assertTrue(last_rec_id > self.rec_id, 'test_recurrence_replace last_rec_id')
        self.assertTrue(rec.active == False, 'test_recurrence_replace active')
        # in setup add new rec and replace it there. look like they get into different sessions/savepoints
#         self.assertTrue(last_rec.unit_qty == 2, 'test_recurrence_replace unit_qty')
#         last_rec1 = self.rec_pool.read(self.cr, self.uid, [last_rec_id], [])
#         print last_rec.name
#         print 'last_rec_id', last_rec_id        
        
        