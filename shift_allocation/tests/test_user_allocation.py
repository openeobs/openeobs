# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests import common
from lxml import etree


class TestUserAllocation(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestUserAllocation, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.activity_pool = cls.registry('nh.activity')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.group_pool = cls.registry('res.groups')
        cls.user_pool = cls.registry('res.users')
        cls.api_pool = cls.registry('nh.clinical.api')
        cls.allocating_pool = cls.registry('nh.clinical.allocating')
        cls.allocation_pool = cls.registry('nh.clinical.staff.allocation')
        cls.resp_pool = cls.registry(
            'nh.clinical.user.responsibility.allocation')

        cls.hospital_id = cls.location_pool.create(
            cr, uid, {'name': 'Test Hospital', 'code': 'TESTHOSP',
                      'usage': 'hospital'})
        cls.pos_id = cls.pos_pool.create(
            cr, uid, {'name': 'Test POS', 'location_id': cls.hospital_id})
        cls.admin_group_id = cls.group_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Admin Group']])[0]
        cls.hca_group_id = cls.group_pool.search(
            cr, uid, [['name', '=', 'NH Clinical HCA Group']])[0]
        cls.nurse_group_id = cls.group_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Nurse Group']])[0]
        cls.wm_group_id = cls.group_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Shift Coordinator Group']])[0]
        cls.sm_group_id = cls.group_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Senior Manager Group']])[0]
        cls.dr_group_id = cls.group_pool.search(
            cr, uid, [['name', '=', 'NH Clinical Doctor Group']])[0]
        cls.adt_uid = cls.user_pool.create(
            cr, uid, {'name': 'Test User', 'login': 'user_001',
                      'password': 'user_001',
                      'groups_id': [[4, cls.admin_group_id]],
                      'pos_id': cls.pos_id})
        cls.ward_id = cls.location_pool.create(
            cr, uid, {'name': 'Ward0', 'code': 'W0', 'usage': 'ward',
                      'parent_id': cls.hospital_id, 'type': 'poc'})
        cls.bed_id = cls.location_pool.create(
            cr, uid, {'name': 'Bed0', 'code': 'B0', 'usage': 'bed',
                      'parent_id': cls.ward_id, 'type': 'poc'})
        cls.hca_uid = cls.user_pool.create(
            cr, uid, {'name': 'HCA0', 'login': 'allo_hca0', 'password': 'hca0',
                      'groups_id': [[4, cls.hca_group_id]],
                      'location_ids': [[5]]})
        cls.nurse_uid = cls.user_pool.create(
            cr, uid, {'name': 'NURSE0', 'login': 'allo_n0', 'password': 'n0',
                      'groups_id': [[4, cls.nurse_group_id]],
                      'location_ids': [[5]]})
        cls.wm_uid = cls.user_pool.create(
            cr, uid, {'name': 'WM0', 'login': 'allo_wm0', 'password': 'wm0',
                      'groups_id': [[4, cls.wm_group_id]],
                      'location_ids': [[5]]})
        cls.sm_uid = cls.user_pool.create(
            cr, uid, {'name': 'SM0', 'login': 'allo_sm0', 'password': 'sm0',
                      'groups_id': [[4, cls.sm_group_id]],
                      'location_ids': [[5]]})
        cls.dr_uid = cls.user_pool.create(
            cr, uid, {'name': 'DR0', 'login': 'allo_dr0', 'password': 'dr0',
                      'groups_id': [[4, cls.dr_group_id]],
                      'location_ids': [[5]]})

    def test_01_allocation_fields_view_get(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Get Form view fields
        res = self.allocation_pool.fields_view_get(
            cr, uid, view_id=None, view_type='form', context=None,
            toolbar=True, submenu=False)
        doc = etree.XML(res['arch'])
        form_nodes = doc.xpath("//form")
        for form_node in form_nodes:
            self.assertEqual(form_node.attrib['edit'], '0')
            self.assertEqual(form_node.attrib['create'], '0')
            self.assertEqual(form_node.attrib['delete'], '0')
        close_nodes = doc.xpath("//button[@string='Close']")
        self.assertFalse(close_nodes, msg="Close button not removed")
        # Scenario 2: Get non Form view fields
        res = self.allocation_pool.fields_view_get(
            cr, uid, view_id=None, view_type='tree', context=None,
            toolbar=False, submenu=False)
        self.assertTrue(res, msg="No result returned")

    def test_02_allocation_submit_users(self):
        cr, uid = self.cr, self.uid

        allocation_id = self.allocation_pool.create(cr, self.adt_uid, {
            'ward_ids': [[6, 0, [self.ward_id]]],
            'user_ids': [[6, 0, [
                self.hca_uid, self.nurse_uid, self.wm_uid, self.sm_uid,
                self.dr_uid]]
            ]
        })
        allocation = self.allocation_pool.browse(cr, uid, allocation_id)
        self.assertEqual(allocation.stage, 'users')
        self.allocation_pool.submit_users(cr, self.adt_uid, [allocation_id])
        allocation = self.allocation_pool.browse(cr, uid, allocation_id)
        self.assertEqual(allocation.stage, 'allocation')
        for allocating in allocation.allocating_user_ids:
            self.assertTrue(
                allocating.user_id.id in [
                    self.hca_uid, self.nurse_uid, self.wm_uid, self.sm_uid,
                    self.dr_uid], msg="Wrong User ID")
            self.assertFalse(allocating.location_ids,
                             msg="Location list should be empty")

    def test_03_allocating_get_roles(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Get Clinical roles for every user type
        allocation_id = self.allocation_pool.search(
            cr, uid, [['create_uid', '=', self.adt_uid]])
        allocation = self.allocation_pool.browse(cr, uid, allocation_id[0])
        for allocating_user in allocation.allocating_user_ids:
            res = self.allocating_pool._get_roles(
                cr, uid, [allocating_user.id], ['roles'], None)
            if allocating_user.user_id.id == self.hca_uid:
                self.assertEqual(res[allocating_user.id], 'HCA ')
            elif allocating_user.user_id.id == self.nurse_uid:
                self.assertEqual(res[allocating_user.id], 'Nurse ')
            elif allocating_user.user_id.id == self.wm_uid:
                self.assertEqual(res[allocating_user.id], 'Shift Coordinator ')
            elif allocating_user.user_id.id == self.sm_uid:
                self.assertEqual(res[allocating_user.id], 'Senior Manager ')
            elif allocating_user.user_id.id == self.dr_uid:
                self.assertEqual(res[allocating_user.id], 'Doctor ')

    def test_04_allocating_fields_view_get(self):
        cr, uid = self.cr, self.uid

        # Scenario 1: Get Form view fields for user without allocation wizard
        res = self.allocating_pool.fields_view_get(
            cr, uid, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False)
        self.assertTrue(res, msg="No result returned")

        # Scenario 2: Get Form view fields for user with allocation wizard
        res = self.allocating_pool.fields_view_get(
            cr, self.adt_uid, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False)
        self.assertListEqual(res['fields']['location_ids']['domain'][0],
                             ['id', 'in', [self.bed_id]])

        # Scenario 3: Get non Form view fields
        res = self.allocating_pool.fields_view_get(
            cr, uid, view_id=None, view_type='tree', context=None,
            toolbar=False, submenu=False)
        self.assertTrue(res, msg="No result returned")

    def test_05_allocation_complete(self):
        cr, uid = self.cr, self.uid

        allocation_id = self.allocation_pool.search(
            cr, uid, [['create_uid', '=', self.adt_uid]])
        allocation = self.allocation_pool.browse(cr, uid, allocation_id[0])
        for allocating_user in allocation.allocating_user_ids:
            if allocating_user.user_id.id in [self.hca_uid, self.nurse_uid]:
                self.allocating_pool.write(
                    cr, self.adt_uid, allocating_user.id,
                    {'location_ids': [[6, 0, [self.bed_id]]]})
            else:
                self.allocating_pool.write(
                    cr, self.adt_uid, allocating_user.id,
                    {'location_ids': [[6, 0, [self.ward_id]]]})

        # Scenario 1: Complete Allocation
        self.allocation_pool.complete(cr, self.adt_uid, allocation_id)
        for allocating_user in allocation.allocating_user_ids:
            resp_id = self.resp_pool.search(
                cr, uid,
                [['responsible_user_id', '=', allocating_user.user_id.id]])
            self.assertTrue(resp_id,
                            msg="Missing Responsibility Allocation activity")
            resp = self.resp_pool.browse(cr, uid, resp_id[0])
            self.assertEqual(resp.activity_id.state, 'completed')
            if allocating_user.user_id.id in [self.hca_uid, self.nurse_uid]:
                self.assertEqual(resp.location_ids[0].id, self.bed_id)
            else:
                self.assertEqual(resp.location_ids[0].id, self.ward_id)
