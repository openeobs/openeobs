from openerp.tests import common
from datetime import datetime as dt
from openerp.osv import orm
from dateutil.relativedelta import relativedelta as rd


class TestADTEntry(common.SingleTransactionCase):

    def setUp(self):

        cr, uid = self.cr, self.uid
        
        self.now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        self.tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                
        self.activity_pool = self.registry('t4.activity')
        self.spell_pool = self.registry('t4.clinical.spell')
        self.patient_pool = self.registry('t4.clinical.patient')
        self.register_pool = self.registry('t4.clinical.adt.patient.register')
        self.admission_pool = self.registry('t4.clinical.adt.patient.admit')
        self.move_pool = self.registry('t4.clinical.patient.move')
        super(TestADTEntry, self).setUp()

        self.patient_data = {
            'given_name': 'Fred',
            'middle_names': 'John',
            'family_name': 'Flintstone',
            'dob': dt.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sex': 'M',
            'gender': 'M',
            'patient_identifier': 'NHS2223',
            'other_identifier': 'HOSPNO778',
            }

    def xml2db_id(self, xmlid):
        cr, uid = self.cr, self.uid
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(cr, uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(cr, uid, imd_id[0]).res_id or False
        return db_id

    def test_register_patient(self):
        cr, uid, patient_data = self.cr, self.uid, self.patient_data

        reg_activity_id = self.register_pool.create_activity(cr, uid, {}, patient_data)
        self.assertTrue(reg_activity_id)
        patient_domain = [(k, '=', v) for k,v in patient_data.iteritems()]
        self.patient_id = self.patient_pool.search(cr, uid, patient_domain)[0]
        self.assertTrue(self.patient_id)
        #Assert cannot enter same data twice
        self.assertRaises(orm.except_orm, self.register_pool.create_activity, cr, uid, {}, patient_data)

    def test_admit_patient(self):
        cr, uid = self.cr, self.uid

        admission_data = {
            'other_identifier': self.patient_data['other_identifier'],
            'code': '100100',
            'location': 'W8',
            'start_date': dt.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        admit_activity_id = self.admission_pool.create_activity(cr, uid, {}, admission_data)
        activity = self.activity_pool.browse(cr, uid, admit_activity_id)

        self.assertEqual(admit_activity_id, activity.id)
        self.assertTrue(activity.patient_id)

    def test_place_patient_can_only_be_done_by_ward_manager(self):
        cr, uid = self.cr, self.uid
        self.assertTrue(False, 'Not Yet Implemented')
