from openerp.tests import common
from datetime import datetime as dt
from openerp.osv import orm
from dateutil.relativedelta import relativedelta as rd


class TestADTEntry(common.SingleTransactionCase):

    def setUp(self):

        cr, uid = self.cr, self.uid
        
        self.now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        self.tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                
        self.task_pool = self.registry('t4.clinical.task')
        self.spell_pool = self.registry('t4.clinical.spell')
        self.patient_pool = self.registry('t4.clinical.patient')
        self.register_pool = self.registry('t4.clinical.adt.patient.register')
        self.admission_pool = self.registry('t4.clinical.adt.patient.admit')
        self.move_pool = self.registry('t4.clinical.patient.move')
        super(TestADTEntry, self).setUp()

    def xml2db_id(self, xmlid):
        cr, uid = self.cr, self.uid
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(cr, uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(cr, uid, imd_id[0]).res_id or False
        return db_id

    def test_register_patient(self):
        cr, uid = self.cr, self.uid

        patient_data = {
            'given_name': 'Fred',
            'middle_names': 'John',
            'family_name': 'Flintstone',
            'dob': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sex': 'M',
            'gender': 'M',
            'patient_identifier': 'NHS2223',
            'other_identifier': 'HOSPNO778',
        }

        reg_task_id = self.register_pool.create_task(cr, uid, {}, patient_data)
        self.assertTrue(reg_task_id)
        patient_domain = [(k, '=', v) for k,v in patient_data.iteritems()]
        self.patient_id = self.patient_pool.search(cr, uid, patient_domain)[0]
        self.assertTrue(self.patient_id)
        #Assert cannot enter same data twice
        self.assertRaises(orm.except_orm, self.register_pool.create_task, cr, uid, {}, patient_data)

    def test_admit_patient(self):
        cr, uid = self.cr, self.uid

        admission_data = {

        }

        admit_task_id = self.admission_pool.create_task(cr, uid, {}, admission_data)
        task = self.task_pool.browse(cr, uid, admit_task_id)

        self.assertEqual(admit_task_id, task.id)
        self.assertTrue(task.patient_id)

