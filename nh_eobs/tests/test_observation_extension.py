from openerp.tests.common import SingleTransactionCase
from openerp.osv.orm import except_orm
from datetime import datetime as dt


class TestObservationExtension(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestObservationExtension, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.user_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.context_pool = cls.registry('nh.clinical.context')
        cls.api = cls.registry('nh.clinical.api')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.eobs_api = cls.registry('nh.eobs.api')
        cls.apidemo = cls.registry('nh.clinical.api.demo')
        cls.follow_pool = cls.registry('nh.clinical.patient.follow')
        cls.unfollow_pool = cls.registry('nh.clinical.patient.unfollow')
        cls.creason_pool = cls.registry('nh.cancel.reason')

        cls.placement_pool = cls.registry('nh.clinical.patient.placement')
        cls.ews_pool = cls.registry('nh.clinical.patient.observation.ews')
        cls.mrsa_pool = cls.registry('nh.clinical.patient.mrsa')
        cls.diabetes_pool = cls.registry('nh.clinical.patient.diabetes')
        cls.pcare_pool = cls.registry('nh.clinical.patient.palliative_care')
        cls.psurgery_pool = cls.registry('nh.clinical.patient.post_surgery')
        cls.ccare_pool = cls.registry('nh.clinical.patient.critical_care')
        cls.wmonitoring_pool = cls.registry('nh.clinical.patient.weight_monitoring')
        cls.uotarget_pool = cls.registry('nh.clinical.patient.uotarget')
        cls.height_pool = cls.registry('nh.clinical.patient.observation.height')
        cls.pbpm_pool = cls.registry('nh.clinical.patient.pbp_monitoring')
        cls.o2target_pool = cls.registry('nh.clinical.patient.o2target')
        cls.o2level_pool = cls.registry('nh.clinical.o2level')

        cls.eobs_context_id = cls.context_pool.search(cr, uid, [['name', '=', 'eobs']])[0]
        cls.admin_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Admin Group']])[0]
        cls.nurse_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Nurse Group']])[0]

        cls.hospital_id = cls.location_pool.create(cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                                                             'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})

        cls.adt_uid = cls.user_pool.create(cr, uid, {'name': 'Admin 0', 'login': 'user_000', 'pos_id': cls.pos_id,
                                                     'password': 'user_000', 'groups_id': [[4, cls.admin_group_id]]})
        cls.ward_id = cls.location_pool.create(cr, uid, {'name': 'Ward0', 'code': 'W0', 'usage': 'ward',
                                                         'parent_id': cls.hospital_id, 'type': 'poc',
                                                         'context_ids': [[4, cls.eobs_context_id]]})
        cls.beds = [cls.location_pool.create(cr, uid, {'name': 'Bed'+str(i), 'code': 'B'+str(i), 'usage': 'bed',
                                                       'parent_id': cls.ward_id, 'type': 'poc',
                                                       'context_ids': [[4, cls.eobs_context_id]]}) for i in range(3)]
        cls.nurse_uid = cls.user_pool.create(cr, uid, {'name': 'NURSE0', 'login': 'n0', 'password': 'n0',
                                                       'groups_id': [[4, cls.nurse_group_id]],
                                                       'location_ids': [[4, cls.beds[0]]]})
        cls.patients = [cls.patient_pool.create(cr, uid, {'other_identifier': 'HN00'+str(i)}) for i in range(3)]

        cls.api.admit(cr, cls.adt_uid, 'HN000', {'location': 'W0'})
        cls.api.admit(cr, cls.adt_uid, 'HN001', {'location': 'W0'})

    def test_01_placement_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.placement_pool._patch_method('refresh_views', do_refresh_views)

        placement_id = self.activity_pool.search(cr, uid, [['patient_id', '=', self.patients[0]],
                                                           ['data_model', '=', 'nh.clinical.patient.placement'],
                                                           ['state', '=', 'scheduled']])[0]
        self.activity_pool.submit(cr, uid, placement_id, {'location_id': self.beds[0]})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, placement_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.placement_pool._revert_method('refresh_views')

    def test_02_ews_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.ews_pool._patch_method('refresh_views', do_refresh_views)

        ews_id = self.activity_pool.search(cr, uid, [['patient_id', '=', self.patients[0]],
                                                     ['data_model', '=', self.ews_pool._name],
                                                     ['state', '=', 'scheduled']])[0]
        self.activity_pool.submit(cr, uid, ews_id, {
            'respiration_rate': 35,
            'indirect_oxymetry_spo2': 99,
            'body_temperature': 37.5,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 65,
            'avpu_text': 'A',
            'oxygen_administration_flag': False
        })
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, ews_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.ews_pool._revert_method('refresh_views')

    def test_03_mrsa_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.mrsa_pool._patch_method('refresh_views', do_refresh_views)

        mrsa_id = self.mrsa_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0], 'mrsa': False})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, mrsa_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.mrsa_pool._revert_method('refresh_views')

    def test_04_diabetes_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.diabetes_pool._patch_method('refresh_views', do_refresh_views)

        diabetes_id = self.diabetes_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0], 'diabetes': False})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, diabetes_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.diabetes_pool._revert_method('refresh_views')

    def test_05_palliative_care_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.pcare_pool._patch_method('refresh_views', do_refresh_views)

        pcare_id = self.pcare_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0], 'status': False})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, pcare_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.pcare_pool._revert_method('refresh_views')

    def test_06_post_surgery_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.psurgery_pool._patch_method('refresh_views', do_refresh_views)

        psurgery_id = self.psurgery_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0], 'status': False})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, psurgery_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.psurgery_pool._revert_method('refresh_views')

    def test_07_critical_care_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.ccare_pool._patch_method('refresh_views', do_refresh_views)

        ccare_id = self.ccare_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0], 'status': False})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, ccare_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.ccare_pool._revert_method('refresh_views')

    def test_08_weight_monitoring_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.wmonitoring_pool._patch_method('refresh_views', do_refresh_views)

        wm_id = self.wmonitoring_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0],
                                                                    'weight_monitoring': False})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, wm_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.wmonitoring_pool._revert_method('refresh_views')

    def test_09_urine_output_target_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.uotarget_pool._patch_method('refresh_views', do_refresh_views)

        uot_id = self.uotarget_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0],
                                                                  'volume': 500, 'unit': 1})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, uot_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.uotarget_pool._revert_method('refresh_views')

    def test_10_height_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.height_pool._patch_method('refresh_views', do_refresh_views)

        height_id = self.height_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0], 'height': 1.7})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, height_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.height_pool._revert_method('refresh_views')

    def test_11_pbp_monitoring_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.pbpm_pool._patch_method('refresh_views', do_refresh_views)

        pbpm_id = self.pbpm_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0], 'pbp_monitoring': False})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, pbpm_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.pbpm_pool._revert_method('refresh_views')

    def test_12_o2_target_complete_refreshes_views_threading(self):
        cr, uid = self.cr, self.uid

        def do_refresh_views(self, cr, uid, views, context=None):
            s = dt.now()
            t = 0
            while t < 3000:
                d = dt.now() - s
                t = int(d.total_seconds() * 1000)
            return do_refresh_views.origin(self, cr, uid, views, context)

        self.o2target_pool._patch_method('refresh_views', do_refresh_views)

        o2target_id = self.o2target_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0],
                                                                       'level_id': False})
        start = dt.now()
        self.assertTrue(self.activity_pool.complete(cr, uid, o2target_id))
        delta = dt.now() - start
        timer = int(delta.total_seconds() * 1000)
        self.assertLess(timer, 3000)
        self.o2target_pool._revert_method('refresh_views')

    def test_13_refresh_materialized_views_decorator(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: send a int as views parameter
        with self.assertRaises(except_orm):
            self.height_pool.refresh_views(cr, uid, 0)

        # Scenario 2: send a int inside the views list parameter
        with self.assertRaises(except_orm):
            self.height_pool.refresh_views(cr, uid, [0])

        # Scenario 3: refresh materialized views normally
        height_id = self.height_pool.create_activity(cr, uid, {}, {'patient_id': self.patients[0], 'height': 1.75})
        self.assertTrue(self.activity_pool.complete(cr, uid, height_id))
        s = dt.now()
        t = 0
        while t < 3000:
            d = dt.now() - s
            t = int(d.total_seconds() * 1000)
