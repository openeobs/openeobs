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
        cls.dev_session_pool = cls.registry('nh.clinical.device.session')
        cls.model_data = cls.registry('ir.model.data')
        cls.move_pool = cls.registry('nh.clinical.patient.move')
        # Wardboard Models
        cls.swap_pool = cls.registry('wardboard.swap_beds')
        cls.swapbeds_pool = cls.registry('nh.clinical.patient.swap_beds')
        cls.movement_pool = cls.registry('wardboard.patient.placement')
        cls.devses_start_pool = cls.registry('wardboard.device.session.start')
        cls.devses_complete_pool = cls.registry('wardboard.device.session.complete')
        cls.wardboard_pool = cls.registry('nh.clinical.wardboard')

        cls.eobs_context_id = cls.context_pool.search(cr, uid, [['name', '=', 'eobs']])[0]
        cls.admin_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Admin Group']])[0]
        cls.hca_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical HCA Group']])[0]
        cls.nurse_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Nurse Group']])[0]
        cls.wm_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Ward Manager Group']])[0]
        cls.dr_group_id = cls.groups_pool.search(cr, uid, [['name', '=', 'NH Clinical Doctor Group']])[0]

        cls.hospital_id = cls.location_pool.create(cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                                                             'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})

        cls.adt_uid = cls.user_pool.create(cr, uid, {'name': 'Admin 0', 'login': 'user_000', 'pos_id': cls.pos_id,
                                                     'password': 'user_000', 'groups_id': [[4, cls.admin_group_id]]})
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
                                                     'groups_id': [[4, cls.hca_group_id]], 'location_ids': [[5]]})
        cls.nurse_uid = cls.user_pool.create(cr, uid, {'name': 'NURSE0', 'login': 'n0', 'password': 'n0',
                                                       'groups_id': [[4, cls.nurse_group_id]], 'location_ids': [[5]]})
        cls.wm_uid = cls.user_pool.create(cr, uid, {'name': 'WM0', 'login': 'wm0', 'password': 'wm0',
                                                    'groups_id': [[4, cls.wm_group_id]],
                                                    'location_ids': [[4, cls.ward_id]]})
        cls.dr_uid = cls.user_pool.create(cr, uid, {'name': 'DR0', 'login': 'dr0', 'password': 'dr0',
                                                    'groups_id': [[4, cls.dr_group_id]],
                                                    'location_ids': [[4, cls.ward_id]]})
        cls.patients = [cls.patient_pool.create(cr, uid, {'other_identifier': 'HN00'+str(i)}) for i in range(3)]

        cls.api.admit(cr, cls.adt_uid, 'HN000', {'location': 'W0'})
        cls.api.admit(cr, cls.adt_uid, 'HN001', {'location': 'W0'})
        cls.wb_disc_id = cls.wardboard_pool.search(cr, uid, [['spell_state', '=', 'started'],
                                                             ['patient_id', '=', cls.patients[1]]])[0]
        cls.api.discharge(cr, cls.adt_uid, 'HN001', {})
        cls.api.admit(cr, cls.adt_uid, 'HN001', {'location': 'W0'})
        cls.api.transfer(cr, cls.adt_uid, 'HN001', {'location': 'W1'})
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

        cls.wb_id = cls.wardboard_pool.search(cr, uid, [['spell_state', '=', 'started'],
                                                        ['patient_id', '=', cls.patients[0]]])[0]
        cls.wb_id2 = cls.wardboard_pool.search(cr, uid, [['spell_state', '=', 'started'],
                                                         ['patient_id', '=', cls.patients[1]]])[0]
        cls.wb_id3 = cls.wardboard_pool.search(cr, uid, [['spell_state', '=', 'started'],
                                                         ['patient_id', '=', cls.patients[2]]])[0]

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

    def test_02_swap_beds_open_wizard(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.wardboard_swap_beds(cr, self.wm_uid, [self.wb_id])
        res_id = self.swap_pool.search(cr, uid, [], order="id desc")[0]
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_swap_beds_form')[1]
        self.assertDictEqual(res, {
            'name': 'Swap Beds',
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.swap_beds',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': None,
            'view_id': view_id
        })

    def test_03_movement(self):
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

    def test_04_placement_open_wizard(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Movement wizard opener
        res = self.wardboard_pool.wardboard_patient_placement(cr, self.wm_uid, [self.wb_id])
        res_id = self.movement_pool.search(cr, uid, [], order="id desc")[0]
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_patient_placement_form')[1]
        wardboard = self.wardboard_pool.browse(cr, uid, self.wb_id)
        self.assertDictEqual(res, {
            'name': 'Move Patient: %s' % wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.patient.placement',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': None,
            'view_id': view_id
        })

        # Scenario 2: Try to use it for a not placed patient
        with self.assertRaises(except_orm):
            self.wardboard_pool.wardboard_patient_placement(cr, self.wm_uid, [self.wb_id3])

    def test_05_device_session_start(self):
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

    def test_06_device_session_start_open_wizard(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.device_session_start(cr, self.wm_uid, [self.wb_id])
        res_id = self.devses_start_pool.search(cr, uid, [], order="id desc")[0]
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs',
                                                       'view_wardboard_device_session_start_form')[1]
        patient = self.patient_pool.browse(cr, uid, self.patients[0])
        self.assertDictEqual(res, {
            'name': 'Start Device Session: ,  ',
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.device.session.start',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': None,
            'view_id': view_id
        })

    def test_07_device_session_complete(self):
        cr, uid = self.cr, self.uid

        activity_id = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['data_model', '=', 'nh.clinical.device.session'],
            ['state', '=', 'started']])
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        devses_complete_id = self.devses_complete_pool.create(cr, uid, {
            'session_id': activity.data_ref.id, 'removal_reason': 'No reason', 'planned': 'planned'})
        res = self.devses_complete_pool.do_complete(cr, self.wm_uid, [devses_complete_id])
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_form')[1]
        self.assertEqual(activity.state, 'completed')
        self.assertDictEqual(res, {
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': self.wb_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'inline',
            'context': None,
            'view_id': view_id
        })

    def test_08_device_session_complete_open_wizard(self):
        cr, uid = self.cr, self.uid

        activity_id = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['data_model', '=', 'nh.clinical.device.session'],
            ['state', '=', 'completed']])
        activity = self.activity_pool.browse(cr, uid, activity_id[0])
        res = self.dev_session_pool.device_session_complete(cr, uid, [activity.data_ref.id])
        res_id = self.devses_complete_pool.search(cr, uid, [], order="id desc")[0]
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs',
                                                       'view_wardboard_device_session_complete_form')[1]
        self.assertDictEqual(res, {
            'name': "Complete Device Session: %s" % activity.data_ref.patient_id.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'wardboard.device.session.complete',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': None,
            'view_id': view_id
        })

    def test_09_get_logo(self):
        cr, uid = self.cr, self.uid

        patient = self.patient_pool.browse(cr, uid, self.patients[0])
        res = self.wardboard_pool._get_logo(cr, uid, [self.wb_id], 'company_logo', None)
        self.assertEqual(res[self.wb_id], patient.partner_id.company_id.logo)

    def test_10_fields_view_get(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.fields_view_get(cr, self.nurse_uid, view_id=False, view_type='form')
        self.assertTrue(res['fields']['o2target']['readonly'])
        res = self.wardboard_pool.fields_view_get(cr, self.wm_uid, view_id=False, view_type='form')
        self.assertFalse(res['fields']['o2target']['readonly'])
        res = self.wardboard_pool.fields_view_get(cr, self.wm_uid, view_id=False, view_type='tree')
        self.assertTrue(res)
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_chart_form')[1]
        res = self.wardboard_pool.fields_view_get(cr, self.wm_uid, view_id=view_id, view_type='form')
        self.assertTrue(res)

    def test_11_get_started_device_session_ids(self):
        cr, uid = self.cr, self.uid

        devtype_id = self.devtype_pool.search(cr, uid, [])[1]
        devcategory_id = self.devtype_pool.browse(cr, uid, devtype_id).category_id.id
        device_id = self.device_pool.create(cr, uid, {'type_id': devtype_id, 'serial_number': '000112'})

        devses_start_id = self.devses_start_pool.create(cr, uid, {
            'patient_id': self.patients[0], 'device_category_id': devcategory_id, 'device_type_id': devtype_id,
            'device_id': device_id, 'location': 'arm'})
        self.devses_start_pool.do_start(cr, self.wm_uid, [devses_start_id])

        res = self.wardboard_pool._get_started_device_session_ids(cr, self.wm_uid, [self.wb_id],
                                                                  'started_device_session_ids', None)
        ids = self.dev_session_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['activity_id.state', '=', 'started']])
        self.assertListEqual(res[self.wb_id], ids)

    def test_12_get_terminated_device_session_ids(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool._get_terminated_device_session_ids(cr, self.wm_uid, [self.wb_id],
                                                                  'terminated_device_session_ids', None)
        ids = self.dev_session_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['activity_id.state', 'in', ['completed', 'cancelled']]])
        self.assertListEqual(res[self.wb_id], ids)

    def test_13_get_data_ids_multi(self):
        cr, uid = self.cr, self.uid

        fields = ['spell_ids', 'move_ids', 'o2target_ids', 'uotarget_ids', 'weight_ids', 'blood_sugar_ids', 'mrsa_ids',
                  'diabetes_ids', 'pbp_monitoring_ids', 'weight_monitoring_ids', 'palliative_care_ids',
                  'post_surgery_ids', 'critical_care_ids', 'pbp_ids', 'ews_ids', 'gcs_ids', 'pain_ids',
                  'urine_output_ids', 'bowels_open_ids', 'ews_list_ids']
        res = self.wardboard_pool._get_data_ids_multi(cr, self.wm_uid, [self.wb_id], fields, None)

        self.assertListEqual(res[self.wb_id]['spell_ids'], [])
        ids = self.move_pool.search(cr, uid, [['patient_id', '=', self.patients[0]],
                                              ['activity_id.state', '=', 'completed']])
        self.assertListEqual(res[self.wb_id]['move_ids'], ids)

    def test_14_get_transferred_user_ids(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Get result for transferred patient
        res = self.wardboard_pool._get_transferred_user_ids(cr, self.wm_uid, [self.wb_id2],
                                                            'transferred_user_ids', None)
        self.assertSetEqual(set(res[self.wb_id2]), {self.wm_uid, self.dr_uid})

        # Scenario 2: Get result for NOT transferred patient
        res = self.wardboard_pool._get_transferred_user_ids(cr, self.wm_uid, [self.wb_id],
                                                            'transferred_user_ids', None)
        self.assertFalse(res[self.wb_id])

    def test_15_get_transferred_user_ids_search(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool._transferred_user_ids_search(
            cr, uid, 'nh.clinical.wardboard', 'transferred_user_ids', [['transferred_user_ids', 'in', [self.wm_uid]]])
        self.assertListEqual(res, [('id', 'in', [self.wb_id2])])

    def test_16_is_placed(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool._is_placed(cr, self.wm_uid, [self.wb_id], 'is_placed', None)
        self.assertTrue(res[self.wb_id])

    def test_17_prescribe_action(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.wardboard_prescribe(cr, self.wm_uid, [self.wb_id])
        wardboard = self.wardboard_pool.browse(cr, uid, self.wb_id)
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_prescribe_form')[1]
        self.assertDictEqual(res, {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': self.wb_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': None,
            'view_id': view_id
        })

    def test_18_news_chart_action(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.wardboard_chart(cr, self.wm_uid, [self.wb_id])
        wardboard = self.wardboard_pool.browse(cr, uid, self.wb_id)
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_chart_form')[1]
        self.assertDictEqual(res, {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': self.wb_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': None,
            'view_id': view_id
        })

    def test_19_weight_chart_action(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.wardboard_weight_chart(cr, self.wm_uid, [self.wb_id], {})
        wardboard = self.wardboard_pool.browse(cr, uid, self.wb_id)
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_weight_chart_form')[1]
        self.assertDictEqual(res, {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': self.wb_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'height': wardboard.height},
            'view_id': view_id
        })

    def test_20_blood_sugar_chart_action(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.wardboard_bs_chart(cr, self.wm_uid, [self.wb_id])
        wardboard = self.wardboard_pool.browse(cr, uid, self.wb_id)
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_bs_chart_form')[1]
        self.assertDictEqual(res, {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': self.wb_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': None,
            'view_id': view_id
        })

    def test_21_news_list_action(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.wardboard_ews(cr, self.wm_uid, [self.wb_id])
        wardboard = self.wardboard_pool.browse(cr, uid, self.wb_id)
        self.assertDictEqual(res, {
            'name': wardboard.full_name,
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.patient.observation.ews',
            'view_mode': 'tree',
            'view_type': 'tree',
            'target': 'new',
            'domain': [('patient_id', '=', wardboard.patient_id.id), ('state', '=', 'completed')],
            'context': None
        })

    def test_22_placement_action(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool.wardboard_place(cr, self.wm_uid, [self.wb_id3], {})
        wardboard = self.wardboard_pool.browse(cr, uid, self.wb_id3)
        placement_id = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[2]], ['state', '=', 'scheduled'],
            ['data_model', '=', 'nh.clinical.patient.placement']])[0]
        res_id = self.activity_pool.browse(cr, uid, placement_id).data_ref.id
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_clinical', 'view_patient_placement_complete')[1]
        self.assertDictEqual(res, {
            'name': wardboard.full_name + ' Placement',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.patient.placement',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'active_id': placement_id},
            'view_id': view_id
        })

    def test_23_write(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Write MRSA parameter
        self.assertTrue(self.wardboard_pool.write(cr, self.wm_uid, [self.wb_id], {'mrsa': 'no'}))
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'completed'],
            ['data_model', '=', 'nh.clinical.patient.mrsa']])
        self.assertTrue(activity_ids)

        # Scenario 2: Write Diabetes parameter
        self.assertTrue(self.wardboard_pool.write(cr, self.wm_uid, [self.wb_id], {'diabetes': 'no'}))
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'completed'],
            ['data_model', '=', 'nh.clinical.patient.diabetes']])
        self.assertTrue(activity_ids)

        # Scenario 3: Write PBP Monitoring parameter
        self.assertTrue(self.wardboard_pool.write(cr, self.wm_uid, [self.wb_id], {'pbp_monitoring': 'no'}))
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'completed'],
            ['data_model', '=', 'nh.clinical.patient.pbp_monitoring']])
        self.assertTrue(activity_ids)

        # Scenario 4: Write Weight Monitoring parameter
        self.assertTrue(self.wardboard_pool.write(cr, self.wm_uid, [self.wb_id], {'weight_monitoring': 'no'}))
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'completed'],
            ['data_model', '=', 'nh.clinical.patient.weight_monitoring']])
        self.assertTrue(activity_ids)

        # Scenario 5: Write O2 Target parameter
        self.assertTrue(self.wardboard_pool.write(cr, self.wm_uid, [self.wb_id], {'o2target': False}))
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'completed'],
            ['data_model', '=', 'nh.clinical.patient.o2target']])
        self.assertTrue(activity_ids)

        # Scenario 6: Write Palliative Care parameter
        self.assertTrue(self.wardboard_pool.write(cr, self.wm_uid, [self.wb_id], {'palliative_care': 'no'}))
        activity_ids = self.activity_pool.search(cr, uid, [
            ['patient_id', '=', self.patients[0]], ['state', '=', 'completed'],
            ['data_model', '=', 'nh.clinical.patient.palliative_care']])
        self.assertTrue(activity_ids)

    def test_24_get_cr_groups(self):
        cr, uid = self.cr, self.uid

        res, fold = self.wardboard_pool._get_cr_groups(cr, self.wm_uid, [self.wb_id], [])
        groups = [['NoScore', 'No Score Yet'], ['High', 'High Risk'], ['Medium', 'Medium Risk'], ['Low', 'Low Risk'],
                  ['None', 'No Risk']]
        self.assertListEqual(res, groups)
        self.assertDictEqual(fold, {g[0]: False for g in groups})

    def test_25_open_previous_spell_action(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Trigger action to open previous spell
        res = self.wardboard_pool.open_previous_spell(cr, self.wm_uid, [self.wb_id2])
        wardboard = self.wardboard_pool.browse(cr, uid, self.wb_id2)
        view_id = self.model_data.get_object_reference(cr, uid, 'nh_eobs', 'view_wardboard_form_discharged')[1]
        activity_ids = self.activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.spell'], ['patient_id', '=', self.patients[1]],
            ['sequence', '<', wardboard.spell_activity_id.sequence], ['state', '=', 'completed']
        ], order='sequence desc')
        res_id = self.activity_pool.browse(cr, uid, activity_ids[0]).data_ref.id
        self.assertDictEqual(res, {
            'name': 'Previous Spell',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.wardboard',
            'res_id': res_id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'context': None,
            'view_id': view_id
        })

        # Scenario 2: Attempt to trigger action without previous spell
        with self.assertRaises(except_orm):
            self.wardboard_pool.open_previous_spell(cr, self.wm_uid, [self.wb_id])

    def test_26_get_recently_discharged_uids(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool._get_recently_discharged_uids(cr, self.wm_uid, [self.wb_disc_id, self.wb_id3],
                                                                'recently_discharged_uids', None)

        self.assertListEqual(sorted(res[self.wb_disc_id]), sorted([self.wm_uid, self.dr_uid]))
        self.assertFalse(res[self.wb_id3])

    def test_27_recently_discharged_uids_search(self):
        cr, uid = self.cr, self.uid

        res = self.wardboard_pool._recently_discharged_uids_search(
            cr, uid, 'nh.clinical.wardboard', 'recently_discharged_uids',
            [['recently_discharged_uids', 'in', [self.wm_uid]]])
        self.assertListEqual(res, [('id', 'in', [self.wb_disc_id])])
