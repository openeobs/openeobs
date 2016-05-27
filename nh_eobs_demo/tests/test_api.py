# coding=utf-8
import logging
from openerp.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestApiDemo(TransactionCase):

    def setUp(self):
        super(TestApiDemo, self).setUp()
        cr, uid = self.cr, self.uid
        self.user_pool = self.registry('res.users')
        self.group_pool = self.registry('res.groups')
        self.patient_pool = self.registry('nh.clinical.patient')
        self.spell_pool = self.registry('nh.clinical.spell')
        self.demo_loader = self.registry('nh.eobs.demo.loader')
        self.demo_api = self.registry('nh.clinical.api.demo')
        self.activity_pool = self.registry('nh.activity')
        self.location_pool = self.registry('nh.clinical.location')
        self.ews_pool = self.registry('nh.clinical.patient.observation.ews')

        self.adt_uid = self.user_pool.search(
            cr, uid, [('login', '=', 'adt')])[0]

    def test_get_patient_hospital_numbers_by_ward(self):
        cr, uid = self.cr, self.uid
        result = self.demo_loader._get_patient_hospital_numbers_by_ward(
            cr, uid, 'A'
        )
        self.assertEqual(len(result), 28)

    # def test_get_patient_hospital_numbers_by_ward_not_placed(self):
    #     cr, uid = self.cr, self.uid
    #     result = self.demo_loader._get_hospital_numbers_by_ward_not_placed(
    #         cr, uid, 'A'
    #     )
    #     self.assertEqual(len(result), 8)

    def test_discharge_patients_completes_spell_patients_on_given_ward(self):
        cr, uid = self.cr, self.uid

        result = self.demo_loader.discharge_patients(
            cr, self.adt_uid, 'A', 2, context=None
        )

        self.assertEqual(len(result), 2)
        patient_ids = self.patient_pool.search(
            cr, uid, [('other_identifier', 'in', result)])
        patients = self.patient_pool.browse(cr, uid, patient_ids)

        # check location is 'Discharge Location'
        locations = [patient.current_location_id for patient in patients]
        self.assertEqual(len(locations), 2)
        for location in locations:
            self.assertIn(location.code, ['DISL-GUH', 'GDL0987654321'])

        # check spell is now completed
        for patient_id in patient_ids:
            spell = self.spell_pool.get_by_patient_id(cr, uid, patient_id)
            self.assertFalse(spell)

    def test_get_available_beds_in_ward(self):
        cr, uid = self.cr, self.uid
        self.demo_api.generate_locations(
            cr, uid, wards=1, beds=4, hospital=True
        )

        result = self.demo_loader._get_available_beds_in_ward(
            cr, uid, 'W1', context=None
        )
        self.assertEqual(result, ['W1B1', 'W1B2', 'W1B3', 'W1B4'])

    def test_transfer_patients_transfers_them_from_location_to_location(self):
        cr, uid = self.cr, self.uid
        self.demo_api.generate_locations(
            cr, uid, wards=1, beds=4, hospital=True)

        result = self.demo_loader.transfer_patients(
            cr, self.adt_uid, 'A', 'W1', 2, context=None
        )
        self.assertEqual(len(result), 2)
        patient_ids = self.patient_pool.search(
            cr, uid, [('other_identifier', 'in', result)])
        patients = self.patient_pool.browse(cr, uid, patient_ids)

        # check location is destination
        locations = [patient.current_location_id for patient in patients]
        for location in locations:
            self.assertTrue(location.code in ['W1B1', 'W1B2'])

    def test_get_nurse_hcs_user_ids(self):
        cr, uid = self.cr, self.uid
        user_ids = self.demo_loader._get_nurse_hca_user_ids(cr, uid)
        self.assertTrue(len(user_ids) > 0)

    def test_get_random_user_id(self):
        cr, uid = self.cr, self.uid
        user_ids = [1, 2, 3, 4]
        user_id = self.demo_loader._get_random_user_id(cr, uid, user_ids)
        self.assertTrue(user_id in user_ids)
