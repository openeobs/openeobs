# coding=utf-8
import logging

from datetime import datetime, timedelta

from openerp.osv import osv
from openerp.tests.common import TransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

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

        self.adt_uid = self.user_pool.search(
            cr, uid, [('login', '=', 'adt')])[0]

    def test_get_patient_hospital_numbers_by_ward(self):
        cr, uid = self.cr, self.uid
        result = self.demo_loader._get_patient_hospital_numbers_by_ward(
            cr, uid, 'A'
        )
        self.assertEqual(len(result), 40)
        self.assertTrue('HOSNUM0001' in result)
        self.assertTrue('HOSNUM0041' not in result)

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
            self.assertEqual(location.code, 'DISL-GUH')

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

    def test_transfer_patients_transfers_patient_from_location_to_location(self):
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
        self.assertEqual(
            ['W1B1', 'W1B2'], [location.code for location in locations]
        )

    def test_get_nurse_hcs_user_ids(self):
        cr, uid = self.cr, self.uid
        user_ids = self.demo_loader._get_nurse_hca_user_ids(cr, uid)
        self.assertTrue(len(user_ids) > 0)

    def test_get_random_user_id(self):
        cr, uid = self.cr, self.uid
        user_ids = [1, 2, 3, 4]
        user_id = self.demo_loader._get_random_user_id(cr, uid, user_ids)
        self.assertTrue(user_id in user_ids)

    def test_generate_news_simulation(self):
        cr, uid = self.cr, self.uid

        locations = self.demo_api.generate_locations(cr, uid, wards=1, beds=3, hospital=True)
        location_ids = locations.get('Ward 1')
        users = self.demo_api.generate_users(cr, uid, location_ids)
        patient_ids = self.demo_api.generate_patients(cr, users['adt'][0], 3)
        results = self.location_pool.read(cr, uid, [location_ids[0]], ['code'])

        # generate eobs for 2 days
        start_date = datetime.now() - timedelta(days=2)
        data = {'location': results[0]['code'], 'start_date': start_date}
        admit_patient_ids = self.demo_api.admit_patients(cr, users['adt'][0], patient_ids, data)

        self.demo_api.place_patients(cr, uid, admit_patient_ids, location_ids[0])
        result = self.demo_loader.generate_news_simulation(
            cr, uid, 1, patient_ids=admit_patient_ids)

        self.assertEquals(result, True)
        scheduled_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', 'in', patient_ids],
            ['data_model', '=', 'nh.clinical.patient.observation.ews'],
            ['state', 'not in', ['completed', 'cancelled']]])
        self.assertEquals(len(scheduled_ids), 3)
