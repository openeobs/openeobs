# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import logging

from openerp.tests.common import SingleTransactionCase

_logger = logging.getLogger(__name__)


class TestWorkload(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWorkload, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.user_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.activity_pool = cls.registry('nh.activity')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.context_pool = cls.registry('nh.clinical.context')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.api = cls.registry('nh.clinical.api')
        # Workload Models
        cls.workload_pool = cls.registry('nh.activity.workload')

        cls.eobs_context_id = cls.context_pool.search(cr, uid, [['name', '=', 'eobs']])[0]
        cls.admin_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Admin Group']])[0]
        cls.wm_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Ward Manager Group']])[0]

        cls.hospital_id = cls.location_pool.create(cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                                                             'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})

        cls.adt_uid = cls.user_pool.create(cr, uid, {'name': 'Admin 0', 'login': 'user_000', 'pos_id': cls.pos_id,
                                                     'password': 'user_000', 'groups_id': [[4, cls.admin_group_id]]})
        cls.ward_id = cls.location_pool.create(cr, uid, {'name': 'Ward0', 'code': 'W0', 'usage': 'ward',
                                                         'parent_id': cls.hospital_id, 'type': 'poc',
                                                         'context_ids': [[4, cls.eobs_context_id]]})

        cls.wm_uid = cls.user_pool.create(cr, uid, {'name': 'WM0', 'login': 'wm0', 'password': 'wm0',
                                                    'groups_id': [[4, cls.wm_group_id]],
                                                    'location_ids': [[4, cls.ward_id]]})
        cls.patients = [cls.api.register(cr, cls.adt_uid, 'HN000', {'given_name': 'giventest',
                                                                    'family_name': 'familytest'})]
        cls.api.admit(cr, cls.adt_uid, 'HN000', {'location': 'W0'})

    def test_01_get_groups(self):
        cr, uid = self.cr, self.uid

        res, fold = self.workload_pool._get_groups(cr, self.wm_uid, [], [])
        groups = [(10, '46- minutes'), (20, '45-31 minutes remain'), (30, '30-16 minutes remain'),
                  (40, '15-0 minutes remain'), (50, '1-15 minutes late'), (60, '16+ minutes late')]
        groups.reverse()
        self.assertListEqual(res, groups)
        self.assertDictEqual(fold, {g[0]: False for g in groups})

    def test_02_data(self):
        cr, uid = self.cr, self.uid

        placement_id = self.activity_pool.search(cr, uid, [['patient_id', '=', self.patients[0]],
                                                           ['data_model', '=', 'nh.clinical.patient.placement'],
                                                           ['state', '=', 'scheduled']])[0]
        wk_id = self.workload_pool.search(cr, uid, [['id', '=', placement_id]])
        self.assertTrue(wk_id)
        wk_data = self.workload_pool.read(cr, self.wm_uid, wk_id[0], [])
        spell_id = self.spell_pool.get_by_patient_id(cr, uid, self.patients[0])
        spell = self.spell_pool.browse(cr, uid, spell_id)

        self.assertEqual(wk_data['activity_id'][0], spell.activity_id.id)
        self.assertEqual(wk_data['proximity_interval'], 10)
        self.assertEqual(wk_data['summary'], 'Patient Placement')
        self.assertEqual(wk_data['state'], 'scheduled')
        self.assertEqual(wk_data['user_id'], False)
        self.assertEqual(wk_data['data_model'], 'nh.clinical.patient.placement')
        self.assertEqual(wk_data['patient_other_id'], 'HN000')
