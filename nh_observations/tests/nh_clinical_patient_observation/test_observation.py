# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime as dt, timedelta as td

from openerp.osv.orm import except_orm
from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

_logger = logging.getLogger(__name__)


class TestObservation(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestObservation, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.height_pool = cls.registry(
            'nh.clinical.patient.observation.height')

        cls.patient_id = cls.patient_pool.search(
            cr, uid, [['patient_identifier', '=', 'NHSNUM0000']])[0]
        cls.patient_2_id = cls.patient_pool.search(
            cr, uid, [['patient_identifier', '=', 'NHSNUM0001']])[0]
        cls.spell_id = cls.activity_pool.search(
            cr, uid, [['patient_id', '=', cls.patient_id],
                      ['data_model', '=', 'nh.clinical.spell']])[0]
        cls.location_id = cls.location_pool.search(
            cr, uid, [['code', '=', 'A01']])[0]

    def test_01_create_updates_none_values_and_null_values(self):
        cr, uid = self.cr, self.uid
        height_id = self.height_pool.create(
            cr, uid, {'patient_id': self.patient_id})
        height_values = self.height_pool.read(
            cr, uid, height_id, ['none_values', 'null_values'])
        self.assertEqual(height_values.get('none_values'), "['height']")
        self.assertEqual(height_values.get('null_values'), "['height']")

    def test_02_create_activity_raises_without_admitted_patient_id(self):
        cr, uid = self.cr, self.uid
        with self.assertRaises(except_orm):
            self.height_pool.create_activity(
                cr, uid, {}, {'patient_id': self.patient_2_id})

    def test_03_create_activity_updates_activity_parent_id(self):
        cr, uid = self.cr, self.uid
        activity_id = self.height_pool.create_activity(
            cr, uid, {}, {'patient_id': self.patient_id})
        activity_data = self.activity_pool.read(
            cr, uid, activity_id, ['parent_id'])
        self.assertEqual(activity_data.get('parent_id')[0], self.spell_id)

    def test_04_write_updates_none_values_and_null_values(self):
        cr, uid = self.cr, self.uid
        height_id = self.height_pool.create(
            cr, uid, {'patient_id': self.patient_id})
        self.height_pool.write(
            cr, uid, height_id, {'height': 180})
        height_values = self.height_pool.read(
            cr, uid, height_id, ['none_values', 'null_values'])
        self.assertEqual(height_values.get('none_values'), "[]")
        self.assertEqual(height_values.get('null_values'), "[]")

    def test_05_write_frequency_schedules_observation(self):
        cr, uid = self.cr, self.uid
        schedule_date = dt.now() + td(minutes=60)
        height_act_id = self.height_pool.create_activity(
            cr, uid, {}, {'patient_id': self.patient_id})
        height_act = self.activity_pool.browse(cr, uid, height_act_id)
        self.height_pool.write(
            cr, uid, height_act.data_ref.id, {'frequency': 60})
        activity_values = self.activity_pool.read(
            cr, uid, height_act_id, ['date_scheduled', 'state'])
        self.assertEqual(activity_values.get('state'), 'scheduled')
        self.assertAlmostEqual(
            activity_values.get('date_scheduled'), schedule_date.strftime(DTF))

    def test_06_read_null_value_returns_false_instead_of_0(self):
        cr, uid = self.cr, self.uid
        height_id = self.height_pool.create(
            cr, uid, {'patient_id': self.patient_id})
        height_values = self.height_pool.read(cr, uid, height_id, ['height'])
        self.assertFalse(height_values.get('height'))
        self.assertEqual(isinstance(height_values.get('height'), bool), True)

    def test_07_get_activity_location_id_returns_spell_id(self):
        cr, uid = self.cr, self.uid
        height_act_id = self.height_pool.create_activity(
            cr, uid, {}, {'patient_id': self.patient_id})
        self.assertEqual(
            self.height_pool.get_activity_location_id(cr, uid, height_act_id),
            self.location_id)
