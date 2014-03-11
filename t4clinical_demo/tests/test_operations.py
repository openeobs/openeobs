from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv




admission_type_data = {'summary': 'Patient Admission', 'data_model': 't4.clinical.patient.admission'}

data_model_data = {'summary': 'Test Type', 'data_model': 'observation.test'}
submit_data = {'val1': 'submit_val1', 'val2': 'submit_val2'}

class TestOperations(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid
        global task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, type_pool, location_pool, patient_pool, ews_pool
        global donald_patient_id, w8_location_id, b1_location_id, admission_data, admission_task_id, discharge_task_id
        global nurse_user_id, nurse_employee_id
        global now, tomorrow
        
        cr, uid = self.cr, self.uid
        
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                
        task_pool = self.registry('t4.clinical.task')
        spell_pool = self.registry('t4.clinical.spell')
        admission_pool = self.registry('t4.clinical.patient.admission')
        move_pool = self.registry('t4.clinical.patient.move')
        height_weight_pool = self.registry('t4.clinical.patient.observation.height_weight')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        discharge_pool = self.registry('t4.clinical.patient.discharge')
        user_pool = self.registry('res.users')
        location_pool = self.registry('t4.clinical.location')
        patient_pool = self.registry('t4.clinical.patient')
        
        super(TestOperations, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(cr, uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(cr, uid, imd_id[0]).res_id or False
        return db_id
    
    def test_operations(self):
        """            
        """
        global cr, uid
        global task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, employee_pool, type_pool, location_pool, patient_pool
        global donald_patient_id, w8_location_id, b1_location_id, admission_data, admission_task_id, discharge_task_id
        global nurse_user_id, nurse_employee_id, manager_user_id
        global now, tomorrow
        
        # ids from demo & base data
        donald_patient_id = self.xml2db_id("demo_patient_donald")
        uhg_location_id = self.xml2db_id("demo_location_uhg")
        uhg_pos_id = self.xml2db_id("demo_pos_uhg")
        w8_location_id = self.xml2db_id("demo_location_w8")
        b1_location_id = self.xml2db_id("demo_location_b1")
        nurse_user_id = self.xml2db_id("demo_user_nurse")
        manager_user_id = self.xml2db_id("demo_user_manager")

        
        
        # task frequency
        task_pool.set_task_trigger(cr, uid, donald_patient_id, 
                                   't4.clinical.patient.observation.ews', 
                                   'minute', 15, context=None)        

        nurse_user = user_pool.browse(cr, uid, nurse_user_id)
        # base data tests
        self.assertTrue(w8_location_id in [l.id for l in nurse_user.location_ids], 'w8_location in nurse_user.locations')
        
        w8_location = location_pool.browse(cr, uid, w8_location_id)
        #import pdb; pdb.set_trace()
        self.assertTrue(w8_location.pos_id.id == uhg_pos_id, 'w8_location.pos == uhg_pos')
        
        b1_location = location_pool.browse(cr, uid, b1_location_id)
        self.assertTrue(b1_location.pos_id.id == uhg_pos_id, 'b1_location.pos == uhg_pos')
        
        # admission create
        admission_task_id = self.create_task_test(
                                     admission_pool,
                                     task_vals      = {},
                                     data_vals      = {'location_id': w8_location_id, 'patient_id': donald_patient_id},
                                     patient_id     = donald_patient_id, 
                                     location_id    = w8_location_id, 
                                     user_id        = manager_user_id
                                     )
        
        # admission operations
        task_pool.assign(cr, uid, admission_task_id, manager_user_id)   
        task_pool.start(cr, uid, admission_task_id)
        task_pool.complete(cr, uid, admission_task_id)
        # admission test
        self.admission_complete_test(
                                     admission_task_id,
                                     patient_id     = donald_patient_id, 
                                     location_id    = w8_location_id, 
                                     user_id        = manager_user_id
                                     )
         
         
        # placement
        placement_task = task_pool.browse_domain(cr, uid, 
                             [('parent_id','=',admission_task_id), ('data_model','=','t4.clinical.patient.placement')])[0]
        task_pool.start(cr, uid, placement_task.id)
        task_pool.submit(cr, uid, placement_task.id,{'location_id': b1_location_id})
        task_pool.complete(cr, uid, placement_task.id)
        # test spell has placement location set
        spell_task_id = task_pool.get_patient_spell_task_id(cr, uid, placement_task.data_ref.patient_id.id)
        spell_task = task_pool.browse(cr, uid, spell_task_id)
        self.assertTrue(spell_task.data_ref.location_id.id == b1_location_id, 'spell.location == placement.location')
         
        # tests
        self.assertTrue(placement_task.location_id.id == b1_location_id, 'task.location == b1_location_id')


        admission_task = task_pool.browse(cr, uid, admission_task_id)
        spell_task_id = admission_task.parent_id.id
        
        height_weight_task_id = self.create_task_test(
                                     height_weight_pool,
                                     task_vals      = {'parent_id': spell_task_id},
                                     data_vals      = {'patient_id': donald_patient_id,'height': 180},#'weight': 80},
                                     patient_id     = donald_patient_id, 
                                     location_id    = b1_location_id, #implemented as latest placement location
                                     user_id        = nurse_user_id
                                     )          
        height_weight_task = task_pool.browse(cr, uid, height_weight_task_id)
        # tests PARTIAL
        self.assertTrue(height_weight_task.data_ref.is_partial, 'partial')


        # EWS
        #import pdb; pdb.set_trace()
        ews_task_id = self.create_task_test(
                                     ews_pool,
                                     task_vals      = {},
                                     data_vals      = {'patient_id': donald_patient_id},
                                     patient_id     = donald_patient_id, 
                                     location_id    = b1_location_id, # patient placement location
                                     user_id        = nurse_user_id
                                     )        
        task_pool.start(cr, uid, ews_task_id)
        task_pool.complete(cr, uid, ews_task_id)  
         
        # discharge
        #import pdb; pdb.set_trace()
        discharge_task_id = self.create_task_test(
                                     discharge_pool,
                                     task_vals      = {},
                                     data_vals      = {'patient_id': donald_patient_id},
                                     patient_id     = donald_patient_id, 
                                     location_id    = b1_location_id, # patient placement location
                                     user_id        = manager_user_id
                                     )        
        task_pool.start(cr, uid, discharge_task_id)
        task_pool.complete(cr, uid, discharge_task_id)



    def create_task_test(self, data_pool, task_vals={}, data_vals={}, patient_id=False, location_id=False, user_id=False):
        global cr, uid
        global task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, type_pool, location_pool, ews_pool
        global now, tomorrow        
#         def print_vars():
#             print "\n"
#             print "task_create_test vars dump header"
#             print "data_pool: %s" % data_pool
#             print "task_vals: %s" % task_vals
#             print "data_vals: %s" % data_vals
#             print "patient_id: %s" % patient_id
#             print "location_id: %s" % location_id            
#             print "user_id: %s" % user_id
#             print "\n"
#         
#         print_vars()
            
            
        task_id = data_pool.create_task(cr, uid, task_vals, data_vals)
        task = task_pool.browse(cr, uid, task_id)
        
        data_domain = []
        data_vals and data_domain.extend([(k,'=',v) for k,v in data_vals.iteritems() if isinstance(v,(int, basestring, float, long))])
        
        task_domain=[('data_model','=',data_pool._name)]
        patient_id and task_domain.append(('patient_id','=',patient_id))
        location_id and task_domain.append(('location_id','=',location_id))      
        user_id and task_domain.append(('user_id','=',user_id))
        task_ids = task_pool.get_task_ids(cr, uid, data_pool._name, data_domain)

        print "task_ids: %s" % task_ids
        print "task_domain: %s" % task_domain
        print "data_domain: %s" % data_domain
        print "user_id: %s" % user_id
        print "task.location_id: %s" % task.location_id
        print "location_ids child_of task.location_id: %s" % location_pool.search(cr, uid, [('id','child_of',task.location_id.id)])        
        print "task.patient_id: %s" % task.patient_id
        print "task.user_ids: %s" % task.user_ids
        print "\n"        
        self.assertTrue(task_id in task_ids, "task_id in task_ids")
        #import pdb; pdb.set_trace()
        user_id and self.assertTrue(user_id in [u.id for u in task.user_ids], "user in task.user")
        location_id and self.assertTrue(location_id == task.location_id.id, 'location == task.location')
        patient_id and self.assertTrue(patient_id == task.patient_id.id, 'patient == get.patient')        
             
        return task_id

    def admission_complete_test(self, admission_task_id, patient_id=False, location_id=False, user_id=False):
        global cr, uid
        global task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, type_pool, location_pool, ews_pool
        global now, tomorrow
        
        admission_task = task_pool.browse(cr, uid, admission_task_id)
        spell_task = task_pool.browse(cr, uid, admission_task.parent_id.id)
        child_tasks = {task.data_model: task for task in task_pool.browse_domain(cr, uid, [('id','child_of',admission_task.id)])}
        move_task = child_tasks['t4.clinical.patient.move']
        placement_task = child_tasks['t4.clinical.patient.placement'] 
        
        self.assertTrue(admission_task.data_model == "t4.clinical.patient.admission", "admission_task.data_model == admission")
        self.assertTrue(admission_task.state == "completed", "admission_task.state == completed")
        self.assertTrue(spell_task.data_model == "t4.clinical.spell", "spell_task.data_model == spell")
        self.assertTrue(spell_task.state == "started", "spell_task.state == started")
        self.assertTrue(move_task.state == "completed", "move_task.state == completed")
        self.assertTrue(placement_task.state == "draft", "placement_task.state == draft")
        if patient_id:
            self.assertTrue(patient_id == admission_task.patient_id.id, 'patient == admission.patient') 
            #import pdb; pdb.set_trace()
            self.assertTrue(patient_id == spell_task.patient_id.id, 'patient == spell.patient') 
            self.assertTrue(patient_id == move_task.patient_id.id, 'patient == move.patient')
            self.assertTrue(patient_id == placement_task.patient_id.id, 'patient == placement.patient')
        if location_id:
            self.assertTrue(location_id == admission_task.location_id.id, 'location == admission.location')
            self.assertTrue(not spell_task.location_id.id, 'not spell.location') 
            self.assertTrue(location_id == move_task.location_id.id, 'location == move.location')
            self.assertTrue(not placement_task.location_id.id, 'not placement.location')   
        if user_id:
            self.assertTrue(user_id in [u.id for u in admission_task.user_ids], 'user in admission.users') 
            self.assertTrue(not [u.id for u in spell_task.user_ids], 'not spell.users') 
            self.assertTrue(user_id in [u.id for u in move_task.user_ids], 'user in move.users')
            self.assertTrue(not [u.id for u in placement_task.user_ids], 'not placement.users')     
        if user_id:
            self.assertTrue(admission_task.user_id.id == user_id, 'admission.user == user')