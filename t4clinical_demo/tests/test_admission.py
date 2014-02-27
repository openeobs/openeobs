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
task_pool, spell_pool, adm_pool, hw_obs_pool, move_pool, discharge_pool = 0,0,0,0,0,0
patient_id, location_id, bed_location_id, admissiion_data, adm_task_id, dis_task_id = 0,0,0,0,0,0
now, tomorrow = 0,0
class TestAdmission(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid
        global task_pool, spell_pool, adm_pool, hw_obs_pool, move_pool, discharge_pool
        global patient_id, location_id, bed_location_id, admissiion_data, adm_task_id, dis_task_id
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
        adm_pool = self.registry('t4.clinical.patient.admission')
        move_pool = self.registry('t4.clinical.patient.move')
        hw_obs_pool = self.registry('t4.clinical.patient.observation.height_weight')
        discharge_pool = self.registry('t4.clinical.patient.discharge')
        
        patient_id = self.xml2db_id("demo_patient_donald")
        location_id = self.xml2db_id("demo_location_uhg")
        bed_location_id = self.xml2db_id("demo_location_b1")
        adm_task_id = adm_pool.create_task(cr, uid, {}, {'location_id': location_id, 'patient_id': patient_id})
        dis_task_id = discharge_pool.create_task(cr, uid, {}, {'patient_id': patient_id})
        
        super(TestAdmission, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(cr, uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(cr, uid, imd_id[0]).res_id or False
        return db_id
    
    def test_complete(self):
        """
        when:
            adm_task.complete
        then:
            adm_task.parent_id.data_model == 't4.clinical.spell'
            move_pool.get_location() == self.location
            
        """
        global cr, uid
        global task_pool, spell_pool, adm_pool, hw_obs_pool, move_pool, discharge_pool
        global patient_id, location_id, bed_location_id, admissiion_data, adm_task_id, dis_task_id
        
        
        
        task_pool.assign(cr, uid, adm_task_id, 1)
        task_pool.start(cr, uid, adm_task_id)
        #import pdb; pdb.set_trace()
        task_pool.complete(cr, uid, adm_task_id)
        adm_task = task_pool.browse(cr, uid, adm_task_id)
        placement_domain = [('parent_id','=',adm_task.id), ('data_model','=','t4.clinical.patient.placement')]
        placement_task = task_pool.browse_domain(cr, uid, placement_domain)[0]
        task_pool.start(cr, uid, placement_task.id)
        task_pool.submit(cr, uid, placement_task.id,{'location_id': bed_location_id})
        task_pool.complete(cr, uid, placement_task.id)
        
        spell_task = spell_pool.get_spell(cr, uid, patient_id).task_id
       
        
        obs_task_id = hw_obs_pool.create_task(cr, uid, {'parent_id': spell_task.id}, {'patient_id': patient_id,'height': 180, 'weight': 80})
        obs_task = task_pool.browse(cr, uid, obs_task_id)
        
        # tests
        self.assertTrue(adm_task.parent_id.data_model == 't4.clinical.spell', 'Data model')
        location = move_pool.get_location(cr, uid, patient_id)
        self.assertTrue( location and location.id == location_id, 'Data model')
        self.assertTrue(not obs_task.data_ref.is_partial, 'partial')
        
        task_pool.start(cr, uid, dis_task_id)
        task_pool.complete(cr, uid, dis_task_id)
        
        