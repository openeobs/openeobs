# -*- coding: utf-8 -*-
# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.tests import common
from faker import Faker
import logging

_logger = logging.getLogger(__name__)
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class test_observations(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(test_observations, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')

        # OBSERVATIONS DATA MODELS
        cls.height_pool = cls.registry(
            'nh.clinical.patient.observation.height')
        cls.weight_pool = cls.registry(
            'nh.clinical.patient.observation.weight')
        cls.blood_sugar_pool = cls.registry(
            'nh.clinical.patient.observation.blood_sugar')
        cls.blood_product_pool = cls.registry(
            'nh.clinical.patient.observation.blood_product')
        # PARAMETERS DATA MODELS
        cls.mrsa_pool = cls.registry('nh.clinical.patient.mrsa')
        cls.diabetes_pool = cls.registry('nh.clinical.patient.diabetes')
        cls.weight_monitoring_pool = cls.registry(
            'nh.clinical.patient.weight_monitoring')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.apidemo.build_unit_test_env(cr, uid, bed_count=4,
                                        patient_placement_count=2)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(
            cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(
            cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(
            cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']),
                      ('pos_id', '=', cls.pos_id)])[0]

    def test_basic_observations(self):
        cr, uid = self.cr, self.uid

        patient_ids = self.patient_pool.search(
            cr, uid, [['current_location_id.usage', '=', 'bed'],
                      ['current_location_id.parent_id', 'in',
                       [self.wu_id, self.wt_id]]])
        self.assertTrue(
            patient_ids, msg="Test set up Failed. No placed patients found")
        patient_id = fake.random_element(patient_ids)
        spell_ids = self.activity_pool.search(
            cr, uid, [['data_model', '=', 'nh.clinical.spell'],
                      ['patient_id', '=', patient_id]])
        self.assertTrue(
            spell_ids,
            msg="Test set up Failed. No spell found for the patient")
        spell_activity = self.activity_pool.browse(cr, uid, spell_ids[0])
        user_id = False
        if self.nu_id in [user.id for user in spell_activity.user_ids]:
            user_id = self.nu_id
        else:
            user_id = self.nt_id

        # Height Observation
        height_data = {
            'height': float(fake.random_int(min=100, max=220))/100.0
        }
        height_activity_id = self.height_pool.create_activity(
            cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, height_activity_id, height_data)
        check_height = self.activity_pool.browse(
            cr, user_id, height_activity_id)

        self.assertTrue(
            check_height.summary == self.height_pool._description,
            msg="Height Observation: Activity summary not submitted correctly")
        self.assertTrue(
            check_height.data_ref.patient_id.id == patient_id,
            msg="Height Observation: Patient id not submitted correctly")
        height = self.height_pool.read(
            cr, uid, check_height.data_ref.id, ['height'])['height']
        self.assertTrue(
            height == height_data['height'],
            msg="Height Observation: Height not submitted correctly - "
                "Read comparison")
        self.activity_pool.complete(cr, user_id, height_activity_id)
        check_height = self.activity_pool.browse(
            cr, user_id, height_activity_id)
        self.assertTrue(
            check_height.state == 'completed',
            msg="Height Observation Completed: State not updated")
        self.assertTrue(
            check_height.date_terminated,
            msg="Height Observation Completed: Date terminated not updated")
        self.assertFalse(
            check_height.data_ref.is_partial,
            msg="Height Observation Completed: Partial status incorrect")

        # Weight Observation
        weight_data = {
            'weight': float(fake.random_int(min=400, max=1200))/10.0
        }
        weight_activity_id = self.weight_pool.create_activity(
            cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, weight_activity_id, weight_data)
        check_weight = self.activity_pool.browse(
            cr, user_id, weight_activity_id)

        self.assertTrue(
            check_weight.summary == self.weight_pool._description,
            msg="Weight Observation: Activity summary not submitted correctly")
        self.assertTrue(
            check_weight.data_ref.patient_id.id == patient_id,
            msg="Weight Observation: Patient id not submitted correctly")
        weight = self.weight_pool.read(
            cr, uid, check_weight.data_ref.id, ['weight'])['weight']
        self.assertTrue(
            weight == weight_data['weight'],
            msg="Weight Observation: Weight not submitted correctly - "
                "Read comparison")
        self.activity_pool.complete(cr, user_id, weight_activity_id)
        check_weight = self.activity_pool.browse(
            cr, user_id, weight_activity_id)
        self.assertTrue(
            check_weight.state == 'completed',
            msg="Weight Observation Completed: State not updated")
        self.assertTrue(
            check_weight.date_terminated,
            msg="Weight Observation Completed: Date terminated not updated")
        self.assertFalse(
            check_weight.data_ref.is_partial,
            msg="Weight Observation Completed: Partial status incorrect")

        # Blood Sugar Observation
        blood_sugar_data = {
            'blood_sugar': float(fake.random_int(min=10, max=999))/10.0
        }
        blood_sugar_activity_id = self.blood_sugar_pool.create_activity(
            cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(
            cr, user_id, blood_sugar_activity_id, blood_sugar_data)
        check_blood_sugar = self.activity_pool.browse(
            cr, user_id, blood_sugar_activity_id)

        self.assertTrue(
            check_blood_sugar.summary == self.blood_sugar_pool._description,
            msg="Blood Sugar Observation: Activity summary not submitted "
                "correctly")
        self.assertTrue(
            check_blood_sugar.data_ref.patient_id.id == patient_id,
            msg="Blood Sugar Observation: Patient id not submitted correctly")
        blood_sugar = self.blood_sugar_pool.read(
            cr, uid, check_blood_sugar.data_ref.id,
            ['blood_sugar'])['blood_sugar']
        self.assertTrue(
            blood_sugar == blood_sugar_data['blood_sugar'],
            msg="Blood Sugar Observation: Blood Sugar not submitted correctly "
                "- Read comparison")
        self.activity_pool.complete(cr, user_id, blood_sugar_activity_id)
        check_blood_sugar = self.activity_pool.browse(
            cr, user_id, blood_sugar_activity_id)
        self.assertTrue(
            check_blood_sugar.state == 'completed',
            msg="Blood Sugar Observation Completed: State not updated")
        self.assertTrue(
            check_blood_sugar.date_terminated,
            msg="Blood Sugar Observation Completed: Date terminated "
                "not updated")
        self.assertFalse(
            check_blood_sugar.data_ref.is_partial,
            msg="Blood Sugar Observation Completed: Partial status incorrect")

        # Blood Product Observation
        blood_product_data = {
            'vol': float(fake.random_int(min=1, max=100000))/10.0,
            'product': fake.random_element(
                self.blood_product_pool._blood_product_values)[0]
        }
        blood_product_activity_id = self.blood_product_pool.create_activity(
            cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(
            cr, user_id, blood_product_activity_id, blood_product_data)
        check_blood_product = self.activity_pool.browse(
            cr, user_id, blood_product_activity_id)

        self.assertTrue(
            check_blood_product.summary ==
            self.blood_product_pool._description,
            msg="Blood Product Observation: Activity summary not submitted "
                "correctly")
        self.assertTrue(
            check_blood_product.data_ref.patient_id.id == patient_id,
            msg="Blood Product Observation: Patient id not submitted "
                "correctly")
        self.assertTrue(
            check_blood_product.data_ref.product ==
            blood_product_data['product'],
            msg="Blood Product Observation: Blood Product not submitted "
                "correctly")
        blood_product = self.blood_product_pool.read(
            cr, uid, check_blood_product.data_ref.id, ['vol'])['vol']
        self.assertTrue(
            blood_product == blood_product_data['vol'],
            msg="Blood Product Observation: volume not submitted correctly - "
                "Read comparison")
        self.activity_pool.complete(
            cr, user_id, blood_product_activity_id)
        check_blood_product = self.activity_pool.browse(
            cr, user_id, blood_product_activity_id)
        self.assertTrue(
            check_blood_product.state == 'completed',
            msg="Blood Product Observation Completed: State not updated")
        self.assertTrue(
            check_blood_product.date_terminated,
            msg="Blood Product Observation Completed: Date terminated "
                "not updated")
        self.assertFalse(
            check_blood_product.data_ref.is_partial,
            msg="Blood Product Observation Completed: Partial status "
                "incorrect")

    def test_parameters(self):
        cr, uid = self.cr, self.uid
        patient_ids = self.patient_pool.search(
            cr, uid, [
                ['current_location_id.usage', '=', 'bed'],
                ['current_location_id.parent_id', 'in',
                 [self.wu_id, self.wt_id]]])
        self.assertTrue(patient_ids,
                        msg="Test set up Failed. No placed patients found")
        patient_id = fake.random_element(patient_ids)
        spell_ids = self.activity_pool.search(
            cr, uid, [['data_model', '=', 'nh.clinical.spell'],
                      ['patient_id', '=', patient_id]])
        self.assertTrue(
            spell_ids,
            msg="Test set up Failed. No spell found for the patient")
        spell_activity = self.activity_pool.browse(cr, uid, spell_ids[0])
        user_id = False
        if self.wmu_id in [user.id for user in spell_activity.user_ids]:
            user_id = self.wmu_id
        else:
            user_id = self.wmt_id
        # MRSA parameter
        mrsa_data = {
            'status': fake.random_element([True, False])
        }
        mrsa_activity_id = self.mrsa_pool.create_activity(
            cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, user_id, mrsa_activity_id, mrsa_data)
        check_mrsa = self.activity_pool.browse(cr, user_id, mrsa_activity_id)

        self.assertTrue(
            check_mrsa.data_ref.patient_id.id == patient_id,
            msg="MRSA Parameter: Patient id not submitted correctly")
        self.assertTrue(
            check_mrsa.data_ref.status == mrsa_data['status'],
            msg="MRSA Parameter: MRSA not submitted correctly")
        self.activity_pool.complete(cr, user_id, mrsa_activity_id)
        check_mrsa = self.activity_pool.browse(cr, user_id, mrsa_activity_id)
        self.assertTrue(
            check_mrsa.state == 'completed',
            msg="MRSA Parameter Completed: State not updated")
        self.assertTrue(
            check_mrsa.date_terminated,
            msg="MRSA Parameter Completed: Date terminated not updated")
        # Diabetes parameter
        diabetes_data = {
            'status': fake.random_element([True, False])
        }
        diabetes_activity_id = self.diabetes_pool.create_activity(
            cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(
            cr, user_id, diabetes_activity_id, diabetes_data)
        check_diabetes = self.activity_pool.browse(
            cr, user_id, diabetes_activity_id)

        self.assertTrue(
            check_diabetes.data_ref.patient_id.id == patient_id,
            msg="Diabetes Parameter: Patient id not submitted correctly")
        self.assertTrue(
            check_diabetes.data_ref.status == diabetes_data['status'],
            msg="Diabetes Parameter: Diabetes not submitted correctly")
        self.activity_pool.complete(cr, user_id, diabetes_activity_id)
        check_diabetes = self.activity_pool.browse(
            cr, user_id, diabetes_activity_id)
        self.assertTrue(
            check_diabetes.state == 'completed',
            msg="Diabetes Parameter Completed: State not updated")
        self.assertTrue(
            check_diabetes.date_terminated,
            msg="Diabetes Parameter Completed: Date terminated not updated")
        # Weight Monitoring parameter
        weight_monitoring_data = {
            'status': fake.random_element([True, False])
        }
        weight_monitoring_activity_id = \
            self.weight_monitoring_pool.create_activity(
                cr, uid, {}, {'patient_id': patient_id})
        self.activity_pool.submit(
            cr, user_id, weight_monitoring_activity_id, weight_monitoring_data)
        check_weight_monitoring = self.activity_pool.browse(
            cr, user_id, weight_monitoring_activity_id)

        self.assertTrue(
            check_weight_monitoring.data_ref.patient_id.id == patient_id,
            msg="Weight Monitoring Parameter: Patient id not submitted "
                "correctly")
        self.assertTrue(
            check_weight_monitoring.data_ref.status ==
            weight_monitoring_data['status'],
            msg="Weight Monitoring Parameter: Weight Monitoring not submitted "
                "correctly")
        self.activity_pool.complete(cr, user_id, weight_monitoring_activity_id)
        check_weight_monitoring = self.activity_pool.browse(
            cr, user_id, weight_monitoring_activity_id)
        self.assertTrue(
            check_weight_monitoring.state == 'completed',
            msg="Weight Monitoring Parameter Completed: State not updated")
        self.assertTrue(
            check_weight_monitoring.date_terminated,
            msg="Weight Monitoring Parameter Completed: Date terminated not "
                "updated")
