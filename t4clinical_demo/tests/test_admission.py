from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv




admission_type_data = {'summary': 'Patient Admission', 'data_model': 't4.clinical.patient.admission'}
spell_type_data = {'summary': 'Spell of Care', 'data_model': 't4.clinical.spell', 'assignee_required': False}

data_model_data = {'summary': 'Test Type', 'data_model': 'observation.test'}
submit_data = {'val1': 'submit_val1', 'val2': 'submit_val2'}


class TestAdmission(common.SingleTransactionCase):
    def setUp(self):
        
        self.now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        self.tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        
#         self.type_pool = self.registry('t4.clinical.task.data.type')
#         self.data_type_id = self.type_pool.create(self.cr, self.uid, admission_type_data)
# 
#         self.type_pool = self.registry('t4.clinical.task.data.type')
#         self.data_type_id = self.type_pool.create(self.cr, self.uid, spell_type_data)
                
        self.task_pool = self.registry('t4.clinical.task')
        self.adm_pool = self.registry('t4.clinical.patient.admission')
        self.move_pool = self.registry('t4.clinical.patient.move')
        self.patient_id = self.xml2db_id("t4clinical_patient_donald_duck")
        self.location_id = self.xml2db_id("demo_location_pos_uhg")
        self.admission_data = {'location_id': self.location_id, 'patient_id':self.patient_id}
        self.adm_task_id = self.adm_pool.create_task(self.cr, self.uid, {}, self.admission_data)
        
        super(TestAdmission, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(self.cr, self.uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(self.cr, self.uid, imd_id[0]).res_id or False
        return db_id
    
    def test_complete(self):
        """
        when:
            adm_task.complete
        then:
            adm_task.parent_id.data_model == 't4.clinical.spell'
            move_pool.get_location() == self.location
            
        """
        self.task_pool.assign(self.cr, self.uid, self.adm_task_id, 1)
        self.task_pool.start(self.cr, self.uid, self.adm_task_id)
        #import pdb; pdb.set_trace()
        self.task_pool.complete(self.cr, self.uid, self.adm_task_id)
        adm_task = self.task_pool.browse(self.cr, self.uid, self.adm_task_id)
        
        self.assertTrue(adm_task.parent_id.data_model == 't4.clinical.spell', 'Data model')
        location = self.move_pool.get_location(self.cr, self.uid, self.patient_id)
        self.assertTrue( location and location.id == self.location_id, 'Data model')
        
     
        
        