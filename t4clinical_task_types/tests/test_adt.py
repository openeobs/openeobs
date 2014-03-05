from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv

ews_data = [{
    #'duration': False,
    'three_in_one': False,
    'respiration_rate': 18,
    'indirect_oxymetry_spo2': 99,
    'oxygen_administration_flag': False,
    'body_temperature': 37.5,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A'
},
{
    #'duration': False,
    'three_in_one': False,
    'respiration_rate': 18,
    'indirect_oxymetry_spo2': 99,
    'oxygen_administration_flag': False,
    'body_temperature': False,
    'blood_pressure_systolic': 120,
    'blood_pressure_diastolic': 80,
    'pulse_rate': 65,
    'avpu_text': 'A'
}]

class TestADT(common.SingleTransactionCase):
    def setUp(self):
        global cr, uid
        global register_pool, patient_pool, admit_pool, task_pool, transfer_pool, ews_pool
        global task_id
        global ews_data
        global now, tomorrow
        
        cr, uid = self.cr, self.uid
        
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                
        register_pool = self.registry('t4.clinical.adt.patient.register')
        patient_pool = self.registry('t4.clinical.patient')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        task_pool = self.registry('t4.clinical.task')
        transfer_pool = self.registry('t4.clinical.adt.patient.transfer')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        
        super(TestADT, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(cr, uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(cr, uid, imd_id[0]).res_id or False
        return db_id
    
    def test_task_types(self):
        """            
        """
        global cr, uid
        global register_pool, patient_pool, admit_pool, task_pool, transfer_pool, ews_pool
        global task_id
        global ews_data        
        global now, tomorrow
        patient_data = {'family_name': 'Bacon', 'other_identifier': '30020', 'dob': '20-12-1922 12:33', 'gender': 'M', 'sex': 'M', 'given_name': 'Andy'}
        reg_task_id = register_pool.create_task(cr, uid, {}, patient_data)
        patient_domain = [(k,'=',v) for k,v in patient_data.iteritems()]
        patient_id = patient_pool.search(cr, uid, patient_domain)[0]
        #dupl_task_id = register_pool.create_task(cr, uid, {}, patient_data)

        admit_data = {'code': 'test', 'other_identifier': '30020', 'location': 'W9', 'start_date': '2014-01-01 12:00:01'}
        admit_task_id = admit_pool.create_task(cr, uid, {}, admit_data)
        admit_task = task_pool.browse(cr, uid, admit_task_id)
        spell_task_id = task_pool.search(cr, uid, [('parent_id','=',admit_task_id)])[0]
        spell_task = task_pool.browse(cr, uid, spell_task_id)
        transfer_task_id = transfer_pool.create_task(cr, uid, {}, {'other_identifier': '30020', 'location': 'W8'})
        
        for data in ews_data:
            data.update({'patient_id': patient_id})
            ews_pool.create_task(cr, uid, {}, data)
        
        self.assertTrue(reg_task_id,"reg_task_id")
        self.assertTrue(not patient_data.get('reg_task_id'), 'reg_task_id is not in patient_data')
        self.assertTrue(patient_id, 'patient_id exists')
        #self.assertTrue(patient_id, 'patient_id exists')
        
        #self.assertTrue(admit_task.parent_id.data_model == 't4.clinical.spell', "spell")
        

         
            

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        