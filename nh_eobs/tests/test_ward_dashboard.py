import logging

from openerp.tests.common import SingleTransactionCase
from openerp.osv.orm import except_orm

_logger = logging.getLogger(__name__)


class TestWardDashboard(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWardDashboard, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.user_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.category_pool = cls.registry('res.partner.category')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.api = cls.registry('nh.clinical.api')
        cls.context_pool = cls.registry('nh.clinical.context')
        # WardDashboard Models
        cls.ward_pool = cls.registry('nh.eobs.ward.dashboard')
        cls.bed_pool = cls.registry('nh.eobs.bed.dashboard')

        cls.eobs_context_id = cls.context_pool.search(cr, uid, [['name', '=', 'eobs']])[0]
        cls.admin_role_id = cls.category_pool.search(cr, uid, [['name', '=', 'System Administrator']])[0]
        cls.hca_role_id = cls.category_pool.search(cr, uid, [['name', '=', 'HCA']])[0]
        cls.nurse_role_id = cls.category_pool.search(cr, uid, [['name', '=', 'Nurse']])[0]
        cls.wm_role_id = cls.category_pool.search(cr, uid, [['name', '=', 'Ward Manager']])[0]
        cls.dr_role_id = cls.category_pool.search(cr, uid, [['name', '=', 'Doctor']])[0]

        cls.hospital_id = cls.location_pool.create(cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                                                             'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})

        cls.adt_uid = cls.user_pool.create(cr, uid, {'name': 'Admin 0', 'login': 'user_000', 'pos_id': cls.pos_id,
                                                     'password': 'user_000', 'category_id': [[4, cls.admin_role_id]]})
        cls.ward_id = cls.location_pool.create(cr, uid, {'name': 'Ward0', 'code': 'W0', 'usage': 'ward',
                                                         'parent_id': cls.hospital_id, 'type': 'poc',
                                                         'context_ids': [[4, cls.eobs_context_id]]})
        cls.ward_id2 = cls.location_pool.create(cr, uid, {'name': 'Ward1', 'code': 'W1', 'usage': 'ward',
                                                          'parent_id': cls.hospital_id, 'type': 'poc',
                                                          'context_ids': [[4, cls.eobs_context_id]]})
        cls.beds = [cls.location_pool.create(cr, uid, {'name': 'Bed'+str(i), 'code': 'B'+str(i), 'usage': 'bed',
                                                       'parent_id': cls.ward_id, 'type': 'poc',
                                                       'context_ids': [[4, cls.eobs_context_id]]}) for i in range(3)]
        cls.hca_uid = cls.user_pool.create(cr, uid, {'name': 'HCA0', 'login': 'hca0', 'password': 'hca0',
                                                     'category_id': [[4, cls.hca_role_id]],
                                                     'location_ids': [[4, cls.beds[0]]]})
        cls.nurse_uid = cls.user_pool.create(cr, uid, {'name': 'NURSE0', 'login': 'n0', 'password': 'n0',
                                                       'category_id': [[4, cls.nurse_role_id]],
                                                       'location_ids': [[4, cls.beds[1]]]})
        cls.wm_uid = cls.user_pool.create(cr, uid, {'name': 'WM0', 'login': 'wm0', 'password': 'wm0',
                                                    'category_id': [[4, cls.wm_role_id]],
                                                    'location_ids': [[4, cls.ward_id]]})
        cls.dr_uid = cls.user_pool.create(cr, uid, {'name': 'DR0', 'login': 'dr0', 'password': 'dr0',
                                                    'category_id': [[4, cls.dr_role_id]],
                                                    'location_ids': [[4, cls.ward_id]]})
        cls.patients = [cls.patient_pool.create(cr, uid, {'other_identifier': 'HN00'+str(i)}) for i in range(3)]
        
        cls.api.admit(cr, cls.adt_uid, 'HN000', {'location': 'W0'})
        cls.api.admit(cr, cls.adt_uid, 'HN001', {'location': 'W0'})
        cls.api.admit(cr, cls.adt_uid, 'HN002', {'location': 'W0'})
        
        placement_id = cls.activity_pool.search(cr, uid, [['patient_id', '=', cls.patients[0]],
                                                          ['data_model', '=', 'nh.clinical.patient.placement'],
                                                          ['state', '=', 'scheduled']])[0]
        cls.activity_pool.submit(cr, uid, placement_id, {'location_id': cls.beds[0]})
        cls.activity_pool.complete(cr, uid, placement_id)
        placement_id = cls.activity_pool.search(cr, uid, [['patient_id', '=', cls.patients[1]],
                                                          ['data_model', '=', 'nh.clinical.patient.placement'],
                                                          ['state', '=', 'scheduled']])[0]
        cls.activity_pool.submit(cr, uid, placement_id, {'location_id': cls.beds[1]})
        cls.activity_pool.complete(cr, uid, placement_id)
        placement_id = cls.activity_pool.search(cr, uid, [['patient_id', '=', cls.patients[2]],
                                                          ['data_model', '=', 'nh.clinical.patient.placement'],
                                                          ['state', '=', 'scheduled']])[0]
        cls.activity_pool.submit(cr, uid, placement_id, {'location_id': cls.beds[2]})
        cls.activity_pool.complete(cr, uid, placement_id)
        
        cls.user_pool.write(cr, uid, [cls.nurse_uid, cls.hca_uid], {'following_ids': [[4, cls.patients[2]]]})

    def test_01_get_bed_ids(self):
        cr, uid = self.cr, self.uid

        res = self.ward_pool._get_bed_ids(cr, uid, [self.ward_id, self.ward_id2], 'bed_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertListEqual(res[self.ward_id], self.beds)
        self.assertFalse(res[self.ward_id2])

    def test_02_get_wm_ids(self):
        cr, uid = self.cr, self.uid

        res = self.ward_pool._get_wm_ids(cr, uid, [self.ward_id, self.ward_id2], 'assigned_wm_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertListEqual(res[self.ward_id], [self.wm_uid])
        self.assertFalse(res[self.ward_id2])

    def test_03_get_dr_ids(self):
        cr, uid = self.cr, self.uid

        res = self.ward_pool._get_dr_ids(cr, uid, [self.ward_id, self.ward_id2], 'assigned_doctor_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertListEqual(res[self.ward_id], [self.dr_uid])
        self.assertFalse(res[self.ward_id2])
        
    def test_04_get_hca_ids(self):
        cr, uid = self.cr, self.uid

        res = self.bed_pool._get_hca_ids(cr, uid, self.beds, 'assigned_hca_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertListEqual(res[self.beds[0]], [self.hca_uid])
        self.assertFalse(res[self.beds[1]])
        self.assertFalse(res[self.beds[2]])
    
    def test_05_get_nurse_ids(self):
        cr, uid = self.cr, self.uid

        res = self.bed_pool._get_nurse_ids(cr, uid, self.beds, 'assigned_nurse_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertListEqual(res[self.beds[1]], [self.nurse_uid])
        self.assertFalse(res[self.beds[0]])
        self.assertFalse(res[self.beds[2]])
    
    def test_06_get_patient_ids(self):
        cr, uid = self.cr, self.uid

        res = self.bed_pool._get_patient_ids(cr, uid, self.beds, 'patient_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertListEqual(res[self.beds[0]], [self.patients[0]])
        self.assertListEqual(res[self.beds[1]], [self.patients[1]])
        self.assertListEqual(res[self.beds[2]], [self.patients[2]])
    
    def test_07_get_nurse_follower_ids(self):
        cr, uid = self.cr, self.uid

        res = self.bed_pool._get_nurse_follower_ids(cr, uid, self.beds, 'nurse_follower_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertFalse(res[self.beds[0]])
        self.assertFalse(res[self.beds[1]])
        self.assertListEqual(res[self.beds[2]], [self.nurse_uid])
        
    def test_08_get_hca_follower_ids(self):
        cr, uid = self.cr, self.uid

        res = self.bed_pool._get_hca_follower_ids(cr, uid, self.beds, 'hca_follower_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertFalse(res[self.beds[0]])
        self.assertFalse(res[self.beds[1]])
        self.assertListEqual(res[self.beds[2]], [self.hca_uid])

    def test_09_ward_dashboard_data(self):
        cr, uid = self.cr, self.uid

        ward = self.ward_pool.browse(cr, self.wm_uid, self.ward_id)
        self.assertEqual(ward.location_id.id, self.ward_id, msg='Incorrect location_id field')
        self.assertEqual(ward.waiting_patients, 0, msg='Incorrect waiting_patients field')
        self.assertEqual(ward.patients_in_bed, 3, msg='Incorrect patients_in_bed field')
        self.assertEqual(ward.free_beds, 0, msg='Incorrect free_beds field')
        self.assertEqual(ward.related_hcas, 1, msg='Incorrect related_hcas field')
        self.assertEqual(ward.related_nurses, 1, msg='Incorrect related_nurses field')
        self.assertEqual(ward.related_doctors, 1, msg='Incorrect related_doctors field')
        self.assertEqual(ward.kanban_color, 7, msg='Incorrect kanban_color field')
        self.assertEqual(ward.high_risk_patients, 0, msg='Incorrect high_risk_patients field')
        self.assertEqual(ward.med_risk_patients, 0, msg='Incorrect med_risk_patients field')
        self.assertEqual(ward.low_risk_patients, 0, msg='Incorrect low_risk_patients field')
        self.assertEqual(ward.no_risk_patients, 0, msg='Incorrect no_risk_patients field')
        self.assertEqual(ward.noscore_patients, 3, msg='Incorrect noscore_patients field')

    def test_10_ward_dashboard_patient_board(self):
        cr, uid = self.cr, self.uid

        res = self.ward_pool.patient_board(cr, self.wm_uid, [self.ward_id], {})
        self.assertDictEqual(res, {
            'name': 'Patients Board',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'view_type': 'form',
            'view_mode': 'kanban,form,tree',
            'domain': [('spell_state', '=', 'started'), ('location_id.usage', '=', 'bed')],
            'target': 'current',
            'context': {'search_default_clinical_risk': 1, 'search_default_high_risk': 0,
                        'search_default_ward_id': self.ward_id}
        })

    def test_11_get_waiting_patient_ids(self):
        cr, uid = self.cr, self.uid

        res = self.ward_pool._get_waiting_patient_ids(cr, uid, [self.ward_id], 'waiting_patient_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertFalse(res[self.ward_id])

        patient_id = self.patient_pool.create(cr, uid, {'other_identifier': 'HN003'})
        self.api.admit(cr, self.adt_uid, 'HN003', {'location': 'W0'})

        res = self.ward_pool._get_waiting_patient_ids(cr, uid, [self.ward_id], 'waiting_patient_ids', {})
        self.assertTrue(isinstance(res, dict))
        self.assertListEqual(res[self.ward_id], [patient_id])
