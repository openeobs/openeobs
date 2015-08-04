import logging

from openerp.tests.common import SingleTransactionCase
from openerp.osv.orm import except_orm

_logger = logging.getLogger(__name__)


class TestWardboard(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWardboard, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.user_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.api = cls.registry('nh.clinical.api')
        cls.context_pool = cls.registry('nh.clinical.context')
        cls.devcategory_pool = cls.registry('nh.clinical.device.category')
        cls.devtype_pool = cls.registry('nh.clinical.device.type')
        cls.device_pool = cls.registry('nh.clinical.device')

        # Wardboard Models
        cls.swap_pool = cls.registry('wardboard.swap_beds')
        cls.swapbeds_pool = cls.registry('nh.clinical.patient.swap_beds')
        cls.movement_pool = cls.registry('wardboard.patient.placement')
        cls.devses_start_pool = cls.registry('wardboard.device.session.start')
        cls.devses_complete_pool = cls.registry('wardboard.device.session.complete')

        cls.eobs_context_id = cls.context_pool.search(cr, uid, [['name', '=', 'eobs']])[0]
        cls.admin_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Admin Group']])[0]
        cls.hca_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical HCA Group']])[0]
        cls.nurse_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Nurse Group']])[0]
        cls.wm_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Ward Manager Group']])[0]

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
        cls.hca_uid = cls.user_pool.create(cr, uid, {'name': 'HCA0', 'login': 'hca0', 'password': 'hca0',
                                                     'groups_id': [[4, cls.hca_group_id]], 'location_ids': [[5]]})
        cls.nurse_uid = cls.user_pool.create(cr, uid, {'name': 'NURSE0', 'login': 'n0', 'password': 'n0',
                                                       'groups_id': [[4, cls.nurse_group_id]], 'location_ids': [[5]]})
        cls.wm_uid = cls.user_pool.create(cr, uid, {'name': 'WM0', 'login': 'wm0', 'password': 'wm0',
                                                    'groups_id': [[4, cls.wm_group_id]],
                                                    'location_ids': [[4, cls.ward_id]]})
        cls.patients = [cls.patient_pool.create(cr, uid, {'other_identifier': 'HN00'+str(i)}) for i in range(3)]

        cls.api.admit(cr, cls.adt_uid, 'HN000', {'location': 'W0'})
        cls.api.admit(cr, cls.adt_uid, 'HN001', {'location': 'W0'})

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

    def test_01_swap_beds(self):
        cr, uid = self.cr, self.uid

        swap_id = self.swap_pool.create(cr, self.wm_uid, {'patient1_id': self.patients[0],
                                                          'ward_location_id': self.ward_id,
                                                          'location1_id': self.beds[0]})
        # Scenario 1: onchange_location2 empty location
        self.assertDictEqual(self.swap_pool.onchange_location2(cr, self.wm_uid, swap_id, False),
                             {'value': {'patient2_id': False}})

        # Scenario 2: onchange_location2 location without patient
        self.assertDictEqual(self.swap_pool.onchange_location2(cr, self.wm_uid, swap_id, self.beds[2]),
                             {'value': {'patient2_id': False, 'location2_id': False}})

        # Scenario 3: onchange_location2 location with patient
        self.assertDictEqual(self.swap_pool.onchange_location2(cr, self.wm_uid, swap_id, self.beds[1]),
                             {'value': {'patient2_id': self.patients[1]}})

        # Scenario 4: do_swap creates a swap activity
        self.swap_pool.write(cr, self.wm_uid, swap_id, {'patient2_id': self.patients[1], 'location2_id': self.beds[1]})
        self.swap_pool.do_swap(cr, self.wm_uid, [swap_id])
        self.assertTrue(self.swapbeds_pool.search(cr, uid, [['location1_id', '=', self.beds[0]],
                                                            ['location2_id', '=', self.beds[1]],
                                                            ['activity_id.state', '=', 'completed']]))

    def test_02_movement(self):
        cr, uid = self.cr, self.uid

        movement_id = self.movement_pool.create(cr, self.wm_uid, {'patient_id': self.patients[0],
                                                                  'ward_location_id': self.ward_id,
                                                                  'bed_src_location_id': self.beds[1],
                                                                  'bed_dst_location_id': self.beds[2]})
        self.movement_pool.do_move(cr, self.wm_uid, [movement_id])
        move_ids = self.activity_pool.search(cr, uid, [['patient_id', '=', self.patients[0]],
                                                       ['data_model', '=', 'nh.clinical.patient.move'],
                                                       ['state', '=', 'completed']], order='sequence desc')
        self.assertTrue(move_ids)
        move = self.activity_pool.browse(cr, uid, move_ids[0])
        self.assertEqual(move.data_ref.location_id.id, self.beds[2])

    def test_03_device_session_start(self):
        cr, uid = self.cr, self.uid

        devtype_id = self.devtype_pool.search(cr, uid, [])[0]
        devcategory_id = self.devtype_pool.browse(cr, uid, devtype_id).category_id.id
        device_id = self.device_pool.create(cr, uid, {'type_id': devtype_id, 'serial_number': '000111'})

        devses_start_id = self.devses_start_pool.create(cr, uid, {
            'patient_id': self.patients[0], 'device_category_id': devcategory_id, 'device_type_id': devtype_id,
            'device_id': device_id, 'location': 'mouth'})

        # Scenario 1: onchange_device_category_id no category
        self.assertFalse(self.devses_start_pool.onchange_device_category_id(cr, uid, [devses_start_id], False))

        # Scenario 2: onchange_device_category_id
        ids = self.devtype_pool.search(cr, uid, [('category_id', '=', devcategory_id)])
        self.assertDictEqual(
            self.devses_start_pool.onchange_device_category_id(cr, uid, [devses_start_id], devcategory_id),
            {'value': {'device_id': False, 'device_type_id': False},
             'domain': {'device_type_id': [('id', 'in', ids)]}})

        # Scenario 3: onchange_device_category_id no type
        self.assertFalse(self.devses_start_pool.onchange_device_type_id(cr, uid, [devses_start_id], False))

        # Scenario 4: onchange_device_type_id
        ids = self.device_pool.search(cr, uid, [('type_id', '=', devtype_id)])
        self.assertDictEqual(
            self.devses_start_pool.onchange_device_type_id(cr, uid, [devses_start_id], devtype_id),
            {'value': {'device_id': False}, 'domain': {'device_id': [('id', 'in', ids), ('is_available', '=', True)]}})

        # Scenario 5: onchange_device_id no device
        self.assertFalse(self.devses_start_pool.onchange_device_id(cr, uid, [devses_start_id], False))

        # Scenario 6: onchange_device_type_id
        self.assertDictEqual(
            self.devses_start_pool.onchange_device_id(cr, uid, [devses_start_id], device_id),
            {'value': {'device_type_id': devtype_id}}
        )

        # Scenario 7: Start the session
        self.devses_start_pool.do_start(cr, self.wm_uid, [devses_start_id])
        self.assertTrue(self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['data_model', '=', 'nh.clinical.device.session'],
            ['state', '=', 'started']]))