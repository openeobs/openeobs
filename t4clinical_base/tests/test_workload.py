from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd


class TestWorkload(common.SingleTransactionCase):

    def setUp(self):
        super(TestWorkload, self).setUp()

        self.activity_pool = self.registry('t4.clinical.activity')

    def test_intervals(self):
        cr, uid = self.cr, self.uid
        activity_pool = self.registry('t4.clinical.activity')
        data = [
            {'name': '46-', 'date_started': (dt.today()+rd(minutes=48)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 10},
            {'name': '45-30', 'date_started': (dt.today()+rd(minutes=38)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 20},
            {'name': '30-15', 'date_started': (dt.today()+rd(minutes=18)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 30},
            {'name': '15-0', 'date_started': (dt.today()+rd(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 40},
            {'name': '1-15', 'date_started': (dt.today()-rd(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 50},
            {'name': '16+', 'date_started': (dt.today()-rd(minutes=18)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 60},
        ]
        #create activities
        test_pool = self.registry('test.activity.data')
        type_pool = self.registry('t4.clinical.activity.type')
        type_pool.create(cr, uid, {'data_model': 'test.activity.data'})
        [d.update({'id': test_pool.create_activity(cr, uid, {}, d)}) for d in data]
        [activity_pool.create(cr, uid, d['id']) for d in data]
        # re-calculate workload_interval field
        # values taken are the ones passed to the function in real situation (extracted through debug)
        domain = [['datetime_deadline', '!=', False]]
        groupby = ['workload_interval', 'remaining_hours']
        fields = ['proximity_interval', 'summary', 'user_id','state']
        activity_pool.read_group(cr, uid, domain, fields, groupby)
        #tests
        for d in data:
            activity = activity_pool.browse(cr, uid, d['id'])
            self.assertTrue(activity.proximity_interval == d['expected_value'], 
                            "workload_interval expected to be %s but is %s" 
                            % (str(d['expected_value']), str(activity.proximity_interval)))
