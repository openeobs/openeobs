from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv




admission_type_data = {'summary': 'Patient Admission', 'data_model': 't4.clinical.patient.admission'}
spell_type_data = {'summary': 'Spell of Care', 'data_model': 't4.clinical.spell', 'assignee_required': False}

data_model_data = {'summary': 'Test Type', 'data_model': 'observation.test'}
submit_data = {'val1': 'submit_val1', 'val2': 'submit_val2'}

class TestOperations(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid
        global task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, employee_pool, type_pool, location_pool, patient_pool
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
        discharge_pool = self.registry('t4.clinical.patient.discharge')
        user_pool = self.registry('res.users')
        employee_pool = self.registry('hr.employee')
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
        global nurse_user_id, nurse_employee_id
        global now, tomorrow
        
        # ids from demo & base data
        donald_patient_id = self.xml2db_id("demo_patient_donald")
        uhg_location_id = self.xml2db_id("demo_location_uhg")
        uhg_pos_id = self.xml2db_id("demo_pos_uhg")
        w8_location_id = self.xml2db_id("demo_location_w8")
        b1_location_id = self.xml2db_id("demo_location_b1")
        nurse_user_id = self.xml2db_id("demo_user_nurse")
        nurse_employee_id = self.xml2db_id("demo_employee_norah")
        
        
        


        # base data tests
        nurse_employee = employee_pool.browse(cr, uid, nurse_employee_id)
        self.assertTrue(nurse_employee.user_id.id == nurse_user_id, 'nurse_user == nurse_employee.user')
        self.assertTrue(w8_location_id in [e.id for e in nurse_employee.location_ids], 'w8_location in nurse_employee.locations')
        
        w8_location = location_pool.browse(cr, uid, w8_location_id)
        self.assertTrue(w8_location.pos_id.id == uhg_pos_id, 'w8_location.pos == uhg_pos')
        
        b1_location = location_pool.browse(cr, uid, b1_location_id)
        self.assertTrue(b1_location.pos_id.id == uhg_pos_id, 'b1_location.pos == uhg_pos')
        
        # admission create
        #admission_task_id = admission_pool.create_task(cr, uid, {}, {'location_id': w8_location_id, 'patient_id': donald_patient_id})
        admission_task_id = self.create_task_test(
                                     admission_pool,
                                     task_vals      = {},
                                     data_vals      = {'location_id': w8_location_id, 'patient_id': donald_patient_id},
                                     patient_id     = donald_patient_id, 
                                     location_id    = w8_location_id, 
                                     employee_id    = nurse_employee_id, 
                                     user_id        = nurse_user_id
                                     )
        
        # admission operations
        task_pool.assign(cr, uid, admission_task_id, nurse_user_id)   
        task_pool.start(cr, uid, admission_task_id)
        task_pool.complete(cr, uid, admission_task_id)
        # test admission complete
        spell_task = patient_pool.get_patient_spell_browse(cr, uid, donald_patient_id).task_id
        self.assertTrue(spell_task, 'on admission.complete spell created')
        self.assertTrue(spell_task, 'on admission.complete spell created')
        
        admission_task = task_pool.browse(cr, uid, admission_task_id)
        # spell


        # tests
        self.assertTrue(admission_task.location_id.id == w8_location_id, 'admission.location == w8_location_id')
        self.assertTrue(admission_task.patient_id.id == donald_patient_id, 'donald_patient_id on Task model')
        
        
        # placement
        placement_domain = [('parent_id','=',admission_task.id), ('data_model','=','t4.clinical.patient.placement')]
        placement_task = task_pool.browse_domain(cr, uid, placement_domain)[0]
        self.assertTrue(placement_task.patient_id.id == donald_patient_id, 'placement.paptient == admission.patient')
        task_pool.start(cr, uid, placement_task.id)
        task_pool.submit(cr, uid, placement_task.id,{'location_id': b1_location_id})
        task_pool.complete(cr, uid, placement_task.id)
        
        # tests
        self.assertTrue(placement_task.location_id.id == b1_location_id, 'task.location == b1_location_id')
        
        location_patient_ids = location_pool.get_location_patient_ids(cr, uid, b1_location_id)
        import pdb; pdb.set_trace()
        self.assertTrue(donald_patient_id in location_patient_ids,
            "donald_patient_id in get_location_patient_ids. location_id=%s, patient_id=%s, location_patient_ids=%s" 
            % (b1_location_id, donald_patient_id, location_patient_ids))
        
       
        # height_weight
        height_weight_task_id = height_weight_pool.create_task(cr, uid, 
                        {'parent_id': spell_task.id}, 
                        {'patient_id': donald_patient_id,'height': 180, 'weight': 80})
        height_weight_task = task_pool.browse(cr, uid, height_weight_task_id)
        
        # tests
        self.assertTrue(admission_task.parent_id.data_model == 't4.clinical.spell', 'Data model')
        location = move_pool.get_patient_location_browse(cr, uid, donald_patient_id)
        self.assertTrue( location and location.id == w8_location_id, 'Data model')
        self.assertTrue(not height_weight_task.data_ref.is_partial, 'partial')
        #self.assertTrue(height_weight_taskpatient_id.id == , 'partial')
        
        # discharge
        discharge_task_id = discharge_pool.create_task(cr, uid, {}, {'patient_id': donald_patient_id})
        discharge_task_id = self.create_task_test(
                                     discharge_pool,
                                     task_vals      = {},
                                     data_vals      = {'patient_id': donald_patient_id},
                                     patient_id     = donald_patient_id, 
                                     location_id    = w8_location_id, 
                                     employee_id    = nurse_employee_id, #nurse_employee_id, auto_assign should be implemented by patient.location
                                     user_id        = nurse_user_id
                                     )        
        task_pool.start(cr, uid, discharge_task_id)
        task_pool.complete(cr, uid, discharge_task_id)
        
        #access
        employee_task_ids = employee_pool.get_employee_task_ids(cr, uid, nurse_employee_id)
        employee = employee_pool.browse(cr, uid, nurse_employee_id)
        employee_task_test = [{'emp_uid':employee.user_id.id, 'task_uid':task.user_id.id, 'task_id': task.id, 'employee_id': employee.id} 
                              for task in task_pool.browse(cr, uid, employee_task_ids)]
        #print employee_task_test
        self.assertTrue(employee_task_ids, 'employee tasks qty > 0')

    def create_task_test(self, data_pool, task_vals={}, data_vals={}, patient_id=False, location_id=False, employee_id=False, user_id=False):
        global cr, uid
        global task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, employee_pool, type_pool, location_pool
        global now, tomorrow        
        
        task_id = data_pool.create_task(cr, uid, task_vals, data_vals)
        if employee_id:
            employee_task_ids = employee_pool.get_employee_task_ids(cr, uid, employee_id)
            task_location_id = task_pool.get_task_location_id(cr, uid, task_id)
            self.assertTrue(task_id in employee_task_ids,
                "task in get_employee_task_ids. task_id=%s, employee_id=%s, employee_task_ids=%s, task_location_id=%s" 
                % (task_id, employee_id, employee_task_ids, task_location_id))
        if location_id:
            self.assertTrue(location_id == task_pool.get_task_location_id(cr, uid, task_id), 'task.location == get_task_location_id')
            #self.assertTrue(location_id == task_pool.get_task_location_id(cr, uid, task_id), 'task.location == get_task_location_id')
        if patient_id:
            self.assertTrue(patient_id == task_pool.get_task_patient_id(cr, uid, task_id), 'task.patient == get_task_patient_id')        
             
        return task_id
         
        