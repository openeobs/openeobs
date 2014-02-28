from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv




admission_type_data = {'summary': 'Patient Admission', 'data_model': 't4.clinical.patient.admission'}
spell_type_data = {'summary': 'Spell of Care', 'data_model': 't4.clinical.spell', 'assignee_required': False}

data_model_data = {'summary': 'Test Type', 'data_model': 'observation.test'}
submit_data = {'val1': 'submit_val1', 'val2': 'submit_val2'}
cr, uid = 0, 0
task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool = 0,0,0,0,0,0
user_pool, employee_pool = 0,0
patient_id, location_id, bed_location_id, admission_data, admission_task_id, discharge_task_id = 0,0,0,0,0,0
user_id, employee_id = 0,0
now, tomorrow = 0,0
class TestOperations(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid
        global task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, employee_pool
        global patient_id, location_id, bed_location_id, admission_data, admission_task_id, discharge_task_id
        global user_id, employee_id
        global now, tomorrow
        
        cr, uid = self.cr, self.uid
        
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        
#         self.type_pool = self.registry('t4.clinical.task.data.type')
#         self.data_type_id = self.type_pool.create(cr, uid, admission_type_data)
# 
#         self.type_pool = self.registry('t4.clinical.task.data.type')
#         self.data_type_id = self.type_pool.create(cr, uid, spell_type_data)
                
        task_pool = self.registry('t4.clinical.task')
        spell_pool = self.registry('t4.clinical.spell')
        admission_pool = self.registry('t4.clinical.patient.admission')
        move_pool = self.registry('t4.clinical.patient.move')
        height_weight_pool = self.registry('t4.clinical.patient.observation.height_weight')
        discharge_pool = self.registry('t4.clinical.patient.discharge')
        user_pool = self.registry('res.users')
        employee_pool = self.registry('hr.employee')
        
        patient_id = self.xml2db_id("demo_patient_donald")
        location_id = self.xml2db_id("demo_location_w8")
        bed_location_id = self.xml2db_id("demo_location_b1")
        admission_task_id = admission_pool.create_task(cr, uid, {}, {'location_id': location_id, 'patient_id': patient_id})
        discharge_task_id = discharge_pool.create_task(cr, uid, {}, {'patient_id': patient_id})
        user_id = self.xml2db_id("demo_user_nurse")
        employee = employee_pool.browse_domain(cr, uid, [('user_id','=',user_id)])[0]
        employee_id = employee.id
        
        super(TestOperations, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(cr, uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(cr, uid, imd_id[0]).res_id or False
        return db_id
    
    def test_complete(self):
        """            
        """
        global cr, uid
        global task_pool, spell_pool, admission_pool, height_weight_pool, move_pool, discharge_pool
        global user_pool, employee_pool
        global patient_id, location_id, bed_location_id, admission_data, admission_task_id, discharge_task_id
        global user_id, employee_id
        global now, tomorrow
        
        #tests
        employee = employee_pool.browse(cr, uid, employee_id)
        self.assertTrue(employee.user_id.id == user_id, 'Employee-User test')
        
        # admission
        task_pool.assign(cr, uid, admission_task_id, user_id)
        task_pool.start(cr, uid, admission_task_id)
        task_pool.complete(cr, uid, admission_task_id)
        admission_task = task_pool.browse(cr, uid, admission_task_id)
        # spell
        spell_task = spell_pool.get_patient_spell_browse(cr, uid, patient_id).task_id

        # tests
        self.assertTrue(admission_task.location_id.id == location_id, 'location_id on Task model')
        self.assertTrue(admission_task.patient_id.id == patient_id, 'patient_id on Task model')
        self.assertTrue(task_pool.get_task_spell_id(cr, uid, admission_task_id) == spell_task.data_ref.id, 'get_patient_spell_browse')
        
        # placement
        placement_domain = [('parent_id','=',admission_task.id), ('data_model','=','t4.clinical.patient.placement')]
        placement_task = task_pool.browse_domain(cr, uid, placement_domain)[0]
        task_pool.start(cr, uid, placement_task.id)
        task_pool.submit(cr, uid, placement_task.id,{'location_id': bed_location_id})
        task_pool.complete(cr, uid, placement_task.id)
        
        # tests
        self.assertTrue(placement_task.location_id.id == bed_location_id, 'location_id on Task model')
        
        
       
        # height_weight
        height_weight_task_id = height_weight_pool.create_task(cr, uid, 
                        {'parent_id': spell_task.id}, 
                        {'patient_id': patient_id,'height': 180, 'weight': 80})
        height_weight_task = task_pool.browse(cr, uid, height_weight_task_id)
        
        # tests
        self.assertTrue(admission_task.parent_id.data_model == 't4.clinical.spell', 'Data model')
        location = move_pool.get_patient_location_browse(cr, uid, patient_id)
        self.assertTrue( location and location.id == location_id, 'Data model')
        self.assertTrue(not height_weight_task.data_ref.is_partial, 'partial')
        #self.assertTrue(height_weight_task.patient_id.id == , 'partial')
        
        # discharge
        task_pool.start(cr, uid, discharge_task_id)
        task_pool.complete(cr, uid, discharge_task_id)
        
        #access
        employee_task_ids = employee_pool.get_employee_task_ids(cr, uid, employee_id)
        print employee_task_ids
        #task_ids = task_pool.search(cr, uid, [('location_id','child_of',employee_location_id)])
        
        
        
        
         
        