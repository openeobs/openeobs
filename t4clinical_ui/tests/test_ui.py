from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp.addons.t4clinical_activity_types.tests.test_scenario import ActivityTypesTest

class TestUI(ActivityTypesTest):

    def setUp(self):
        super(TestUI, self).setUp()

        self.activity_pool = self.registry('t4.clinical.activity')

    def test_workload(self):
        cr, uid = self.cr, self.uid
        data = [
            {'name': '46-', 'date_scheduled': (dt.today()+rd(minutes=48)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 10},
            {'name': '45-30', 'date_scheduled': (dt.today()+rd(minutes=38)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 20},
            {'name': '30-15', 'date_scheduled': (dt.today()+rd(minutes=18)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 30},
            {'name': '15-0', 'date_scheduled': (dt.today()+rd(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 40},
            {'name': '1-15', 'date_scheduled': (dt.today()-rd(minutes=8)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 50},
            {'name': '16+', 'date_scheduled': (dt.today()-rd(minutes=18)).strftime("%Y-%m-%d %H:%M:%S"), 'expected_value': 60},
        ]
        #create activities
        pos_env = self.create_pos_environment()
        register_pool = self.registry('t4.clinical.adt.patient.register')
        [d.update({'id': register_pool.create_activity(cr, pos_env['adt_user_id'], {'summary': d['name']}, self.data_patient())}) for d in data]

        #tests
        activity_pool = self.registry('t4.clinical.activity')
        activity_workload_pool = self.registry('t4.clinical.activity.workload')
        for d in data:
            activity_pool.schedule(cr, uid, d['id'], d['date_scheduled'])
            activity_workload = activity_workload_pool.browse(cr, uid, d['id'])
            print "expected: ", d['expected_value'], "  actual: ", activity_workload.proximity_interval, \
                  "date_scheduled: ", activity_workload.date_scheduled
            self.assertTrue(activity_workload.proximity_interval == d['expected_value'], 
                            "workload_interval expected to be %s but is %s" 
                            % (str(d['expected_value']), str(activity_workload.proximity_interval)))


    def test_wardboard(self):
        from pprint import pprint as pp
        cr, uid = self.cr, self.uid
        pos_env = self.create_pos_environment()
        self.adt_patient_register(data_vals={'other_identifier': "test_workload"}, env=pos_env)
        pp(pos_env)
        #self.adt_patient_admit()
        #self.patient_placement(pos_env['pateint_ids'][0])
        