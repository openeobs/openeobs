from openerp.tests import common

import logging
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class TestPBP(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestPBP, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')

        cls.placement_pool = cls.registry('nh.clinical.patient.placement')
        cls.pbp_pool = cls.registry('nh.clinical.patient.observation.pbp')
        cls.pbp_monitoring_pool = cls.registry('nh.clinical.patient.pbp_monitoring')
        cls.notification_pool = cls.registry('nh.clinical.notification.nurse')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.apidemo.build_unit_test_env(cr, uid, bed_count=4, patient_placement_count=2)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]

    def test_postural_blood_pressure_monitoring(self):
        cr, uid = self.cr, self.uid

        patient_ids = self.patient_pool.search(cr, uid, [['current_location_id.usage', '=', 'bed'], ['current_location_id.parent_id', 'in', [self.wu_id, self.wt_id]]])
        self.assertTrue(patient_ids, msg="Test set up Failed. No placed patients found")
        patient_id = fake.random_element(patient_ids)
        spell_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.spell'], ['patient_id', '=', patient_id]])
        self.assertTrue(spell_ids, msg="Test set up Failed. No spell found for the patient")
        spell_activity = self.activity_pool.browse(cr, uid, spell_ids[0])
        user_id = False
        if self.nu_id in [user.id for user in spell_activity.user_ids]:
            user_id = self.nu_id
        else:
            user_id = self.nt_id

        # Check there are no PBP activities before test
        pbp_activity_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.pbp'], ['patient_id', '=', patient_id]])
        self.assertFalse(pbp_activity_ids, msg="Postural Blood Pressure monitoring activities were triggered before setting monitoring ON")
        # Set PBP Monitoring ON
        monitoring_id = self.pbp_monitoring_pool.create_activity(cr, uid, {'parent_id': spell_activity.id}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, uid, monitoring_id, {'status': True})
        check_monitoring = self.activity_pool.browse(cr, uid, monitoring_id)
        self.assertTrue(check_monitoring.data_ref.patient_id.id == patient_id, msg="PBP Monitoring parameter set: Patient id not submitted correctly")
        self.assertTrue(check_monitoring.data_ref.status, msg="PBP Monitoring parameter set: Monitoring value not submitted correctly")
        self.activity_pool.complete(cr, uid, monitoring_id)
        check_monitoring = self.activity_pool.browse(cr, uid, monitoring_id)
        self.assertTrue(check_monitoring.state == 'completed', msg="PBP Monitoring parameter set not completed successfully")
        self.assertTrue(check_monitoring.date_terminated, msg="PBP Monitoring parameter set Completed: Date terminated not registered")
        # Check the PBP activity triggered correctly
        pbp_activity_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.pbp'], ['patient_id', '=', patient_id], ['state', '=', 'scheduled']])
        self.assertTrue(pbp_activity_ids, msg="PBP activity not scheduled after setting monitoring ON")
        
        pbp_data = {
            'systolic_sitting': 120,
            'systolic_standing': 118,
            'diastolic_sitting': 80,
            'diastolic_standing': 79,
        }
        
        self.activity_pool.submit(cr, user_id, pbp_activity_ids[0], pbp_data)
        check_pbp = self.activity_pool.browse(cr, uid, pbp_activity_ids[0])
        self.assertTrue(check_pbp.data_ref.systolic_sitting == pbp_data['systolic_sitting'], msg="PBP: Systolic sitting not submitted correctly")
        self.assertTrue(check_pbp.data_ref.systolic_standing == pbp_data['systolic_standing'], msg="PBP: Systolic standing not submitted correctly")
        self.assertTrue(check_pbp.data_ref.diastolic_sitting == pbp_data['diastolic_sitting'], msg="PBP: Diastolic sitting not submitted correctly")
        self.assertTrue(check_pbp.data_ref.diastolic_standing == pbp_data['diastolic_standing'], msg="PBP: Diastolic standing not submitted correctly")
        # Complete PBP
        self.activity_pool.complete(cr, user_id, pbp_activity_ids[0])
        pbp_activity_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.pbp'], ['patient_id', '=', patient_id], ['state', '=', 'scheduled']])
        self.assertTrue(pbp_activity_ids, msg="PBP activity not scheduled after completing previous observation")
        notification_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.notification.nurse'], ['state', 'not in', ['completed', 'cancelled']], ['summary', '=', 'Inform FY2'], ['parent_id', '=', spell_activity.id]])
        self.assertFalse(notification_ids, msg="Inform FY2 triggered despite sitting and standing Blood Pressures being within the OK range")

        # Set PBP Monitoring OFF
        monitoring_id = self.pbp_monitoring_pool.create_activity(cr, uid, {'parent_id': spell_activity.id}, {'patient_id': patient_id})
        self.activity_pool.submit(cr, uid, monitoring_id, {'status': False})
        self.activity_pool.complete(cr, uid, monitoring_id)
        pbp_activity_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.pbp'], ['patient_id', '=', patient_id], ['state', '=', 'scheduled']])
        self.assertTrue(pbp_activity_ids, msg="PBP activity cancelled after setting monitoring OFF")

        pbp_data = {
            'systolic_sitting': 120,
            'systolic_standing': 99,
            'diastolic_sitting': 80,
            'diastolic_standing': 79,
        }

        self.activity_pool.submit(cr, user_id, pbp_activity_ids[0], pbp_data)
        check_pbp = self.activity_pool.browse(cr, uid, pbp_activity_ids[0])
        self.assertTrue(check_pbp.data_ref.systolic_sitting == pbp_data['systolic_sitting'], msg="PBP: Systolic sitting not submitted correctly")
        self.assertTrue(check_pbp.data_ref.systolic_standing == pbp_data['systolic_standing'], msg="PBP: Systolic standing not submitted correctly")
        self.assertTrue(check_pbp.data_ref.diastolic_sitting == pbp_data['diastolic_sitting'], msg="PBP: Diastolic sitting not submitted correctly")
        self.assertTrue(check_pbp.data_ref.diastolic_standing == pbp_data['diastolic_standing'], msg="PBP: Diastolic standing not submitted correctly")
        # Complete PBP
        self.activity_pool.complete(cr, user_id, pbp_activity_ids[0])
        pbp_activity_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.patient.observation.pbp'], ['patient_id', '=', patient_id], ['state', '=', 'scheduled']])
        self.assertFalse(pbp_activity_ids, msg="PBP activity scheduled after completing previous observation despite monitoring being OFF")
        notification_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.notification.nurse'], ['state', 'not in', ['completed', 'cancelled']], ['summary', '=', 'Inform FY2'], ['parent_id', '=', spell_activity.id]])
        self.assertTrue(notification_ids, msg="Inform FY2 not triggered despite sitting and standing Blood Pressures having a difference > 20")