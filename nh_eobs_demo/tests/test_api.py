# coding=utf-8
import logging

from datetime import datetime

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

