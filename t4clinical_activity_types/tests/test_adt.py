from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
#from t4_base.tools import xml2db_id

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
        global register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool
        global activity_id, api_pool
        global ews_data
        global now, tomorrow
        
        cr, uid = self.cr, self.uid
        
        now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                
        register_pool = self.registry('t4.clinical.adt.patient.register')
        patient_pool = self.registry('t4.clinical.patient')
        admit_pool = self.registry('t4.clinical.adt.patient.admit')
        activity_pool = self.registry('t4.clinical.activity')
        transfer_pool = self.registry('t4.clinical.adt.patient.transfer')
        ews_pool = self.registry('t4.clinical.patient.observation.ews')
        api_pool = self.registry('t4.clinical.api')
        
        super(TestADT, self).setUp()
    
    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(self.cr, self.uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(self.cr, self.uid, imd_id[0]).res_id or False
        return db_id
    
    def test_activity_types(self):
        """            
        """
        global cr, uid
        global register_pool, patient_pool, admit_pool, activity_pool, transfer_pool, ews_pool
        global activity_id, api_pool
        global ews_data        
        global now, tomorrow
        
        adt_uid = self.xml2db_id("demo_user_adt_uhg")
        
        patient_data = {'family_name': 'Bacon', 'other_identifier': '30020', 'dob': '20-12-1922 12:33', 'gender': 'M', 'sex': 'M', 'given_name': 'Andy'}
        reg_activity_id = register_pool.create_activity(cr, adt_uid, {}, patient_data)
        patient_domain = [(k,'=',v) for k,v in patient_data.iteritems()]
        patient_id = patient_pool.search(cr, adt_uid, patient_domain)[0]
        #dupl_activity_id = register_pool.create_activity(cr, uid, {}, patient_data)

        admit_data = {'code': 'test', 'other_identifier': '30020', 'location': 'W9', 'start_date': '2014-01-01 12:00:01'}
        admit_activity_id = admit_pool.create_activity(cr, adt_uid, {}, admit_data)
        admit_activity = activity_pool.browse(cr, adt_uid, admit_activity_id)
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, adt_uid, patient_id)
        transfer_activity_id = transfer_pool.create_activity(cr, adt_uid, {}, {'other_identifier': '30020', 'location': 'W8'})
        
        for data in ews_data:
            data.update({'patient_id': patient_id})
            ews_pool.create_activity(cr, adt_uid, {}, data)
        
        self.assertTrue(reg_activity_id,"reg_activity_id")
        self.assertTrue(not patient_data.get('reg_activity_id'), 'reg_activity_id is not in patient_data')
        self.assertTrue(patient_id, 'patient_id exists')
        #self.assertTrue(patient_id, 'patient_id exists')
        
        #self.assertTrue(admit_activity.parent_id.data_model == 't4.clinical.spell', "spell")