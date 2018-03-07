# Part of NHClinical. See LICENSE file for full copyright and licensing details
# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase

from openerp.addons.nh_clinical.tests.common import helpers


class TestAllocationWizards(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAllocationWizards, cls).setUpClass()
        cr, uid, = cls.cr, cls.uid
        helpers.create_test_data(cls, cr, uid)

    def test_01_nursing_staff_allocation(self):
        cr, uid = self.cr, self.uid
        wm_uid = self.users['wm'][0]
        # Step 1: The Ward Manager opens the wizard
        sawiz_id = self.staff_allocation.create(cr, wm_uid, {})
        self.assertTrue(sawiz_id, msg="Staff Allocation wizard not created")
        self.assertEqual(self.staff_allocation.read(
            cr, uid, sawiz_id, ['stage'])['stage'], 'wards')

        # Step 2: Selecting the Ward
        ward_id = self.location_pool.search(cr, uid,
                                            [['code', '=', 'WARD0']])[0]
        self.staff_allocation.write(cr, wm_uid, sawiz_id, {'ward_id': ward_id})
        self.staff_allocation.submit_wards(cr, wm_uid, sawiz_id)
        self.assertEqual(self.staff_allocation.read(
            cr, uid, sawiz_id, ['stage'])['stage'], 'review')
        location_ids = self.staff_allocation.read(
            cr, uid, sawiz_id, ['location_ids'])['location_ids']
        self.assertTrue(ward_id in location_ids,
                        msg="Ward ID missing from location ids")
        for bed_id in self.locations[ward_id]:
            self.assertTrue(bed_id in location_ids,
                            msg="Bed ID missing from location ids")

        # Step 3: De-allocation
        self.staff_allocation.deallocate(cr, wm_uid, sawiz_id)
        self.assertEqual(self.staff_allocation.read(
            cr, uid, sawiz_id, ['stage'])['stage'], 'users')
        self.assertEqual(len(self.users_pool.search(
            cr, uid, [['location_ids', 'in', location_ids]])), 1)
        self.assertEqual(self.users_pool.read(
            cr, uid, wm_uid, ['location_ids'])['location_ids'], [ward_id])
        allocating_ids = self.staff_allocation.read(
            cr, uid, sawiz_id, ['allocating_ids'])['allocating_ids']
        self.assertEqual(len(allocating_ids), len(location_ids)-1)
        for alid in allocating_ids:
            alloc_read = self.allocating.read(
                cr, uid, alid, ['location_id'])['location_id'][0]
            self.assertTrue(alloc_read in location_ids)

        # Step 4: Selecting the Nursing Staff
        user_ids = [self.users['ns'][0], self.users['ns'][1],
                    self.users['hc'][0]]
        self.staff_allocation.write(cr, wm_uid, sawiz_id,
                                    {'user_ids': [[6, 0, user_ids]]})
        self.staff_allocation.submit_users(cr, wm_uid, sawiz_id)
        self.assertEqual(self.staff_allocation.read(
            cr, uid, sawiz_id, ['stage'])['stage'], 'allocation')

        # Step 5: Allocating users to Beds
        view_fields = self.allocating.fields_view_get(cr, wm_uid)
        self.assertTrue(view_fields['fields']['nurse_id']['domain'])
        self.assertTrue(view_fields['fields']['hca_id']['domain'])
        nurse_ids = self.users_pool.search(
            cr, uid, view_fields['fields']['nurse_id']['domain'])
        hca_ids = self.users_pool.search(
            cr, uid, view_fields['fields']['hca_id']['domain'])
        for nid in nurse_ids:
            self.assertTrue(nid in user_ids)
        for hid in hca_ids:
            self.assertTrue(hid in user_ids)
        alternate = True
        for alid in allocating_ids:
            self.allocating.write(
                cr, wm_uid, alid,
                {'nurse_id': user_ids[0] if alternate else user_ids[1],
                 'hca_id': user_ids[2]})
            alternate = not alternate

        # Step 6: Complete Allocation
        self.staff_allocation.complete(cr, wm_uid, sawiz_id)
        nurse1_loc_ids = self.users_pool.read(
            cr, uid, user_ids[0], ['location_ids'])['location_ids']
        nurse2_loc_ids = self.users_pool.read(
            cr, uid, user_ids[1], ['location_ids'])['location_ids']
        hca_loc_ids = self.users_pool.read(
            cr, uid, user_ids[2], ['location_ids'])['location_ids']
        self.assertEqual(len(nurse1_loc_ids), 5)
        self.assertEqual(len(nurse2_loc_ids), 5)
        self.assertEqual(len(hca_loc_ids), 10)
        for loc_id in nurse1_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")
        for loc_id in nurse2_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")
        for loc_id in hca_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")

    def test_02_nursing_staff_reallocation(self):
        cr, uid = self.cr, self.uid
        wm_uid = self.users['wm'][0]
        ward_id = self.location_pool.search(cr, uid,
                                            [['code', '=', 'WARD0']])[0]

        # Step 1: The Ward Manager opens the wizard
        srwiz_id = self.staff_reallocation.create(cr, wm_uid, {})
        self.assertTrue(srwiz_id, msg="Staff Re-Allocation wizard not created")
        self.assertEqual(self.staff_reallocation.read(
            cr, uid, srwiz_id, ['stage'])['stage'], 'users')
        self.assertEqual(self.staff_reallocation.read(
            cr, uid, srwiz_id, ['ward_id'])['ward_id'][0], ward_id)
        location_ids = self.staff_reallocation.read(
            cr, uid, srwiz_id, ['location_ids'])['location_ids']
        self.assertTrue(ward_id in location_ids,
                        msg="Ward ID missing from location ids")
        for bed_id in self.locations[ward_id]:
            self.assertTrue(bed_id in location_ids,
                            msg="Bed ID missing from location ids")
        user_ids = self.staff_reallocation.read(
            cr, uid, srwiz_id, ['user_ids'])['user_ids']
        for u_id in user_ids:
            self.assertTrue(u_id in [self.users['ns'][0], self.users['ns'][1],
                                     self.users['hc'][0]])
        allocating_ids = self.staff_reallocation.read(
            cr, uid, srwiz_id, ['allocating_ids'])['allocating_ids']
        self.assertEqual(len(allocating_ids), len(location_ids)-1)
        for alid in allocating_ids:
            loc_id = self.allocating.read(
                cr, uid, alid, ['location_id'])['location_id'][0]
            self.assertTrue(loc_id in location_ids)
            nurse_id = self.allocating.read(
                cr, uid, alid, ['nurse_id'])['nurse_id'][0]
            self.assertTrue(nurse_id in user_ids)
            hca_id = self.allocating.read(
                cr, uid, alid, ['hca_id'])['hca_id'][0]
            self.assertTrue(hca_id in user_ids)

        # Step 2: Re-Selecting Nursing Staff
        user_ids = [self.users['ns'][0], self.users['ns'][2],
                    self.users['hc'][0]]
        self.staff_reallocation.write(cr, wm_uid, srwiz_id,
                                      {'user_ids': [[6, 0, user_ids]]})
        self.staff_reallocation.reallocate(cr, wm_uid, srwiz_id)
        allocating_ids = self.staff_reallocation.read(
            cr, uid, srwiz_id, ['allocating_ids'])['allocating_ids']
        self.assertEqual(self.staff_reallocation.read(
            cr, uid, srwiz_id, ['stage'])['stage'], 'allocation')
        for alid in allocating_ids:
            nurse_id = self.allocating.read(
                cr, uid, alid, ['nurse_id'])['nurse_id']
            hca_id = self.allocating.read(cr, uid, alid, ['hca_id'])['hca_id']
            if nurse_id:
                self.assertEqual(nurse_id[0], self.users['ns'][0])
            self.assertEqual(hca_id[0], self.users['hc'][0])

        # Step 3: Re-Allocating Users to Beds
        view_fields = self.allocating.fields_view_get(cr, wm_uid)
        self.assertTrue(view_fields['fields']['nurse_id']['domain'])
        self.assertTrue(view_fields['fields']['hca_id']['domain'])
        nurse_ids = self.users_pool.search(
            cr, uid, view_fields['fields']['nurse_id']['domain'])
        hca_ids = self.users_pool.search(
            cr, uid, view_fields['fields']['hca_id']['domain'])
        for nid in nurse_ids:
            self.assertTrue(nid in user_ids)
        for hid in hca_ids:
            self.assertTrue(hid in user_ids)
        for a in self.allocating.browse(cr, uid, allocating_ids):
            if not a.nurse_id:
                self.allocating.write(cr, wm_uid, a.id,
                                      {'nurse_id': user_ids[1]})

        # Step 4: Complete Re-Allocation
        self.staff_reallocation.complete(cr, wm_uid, srwiz_id)
        nurse1_loc_ids = self.users_pool.read(
            cr, uid, user_ids[0], ['location_ids'])['location_ids']
        nurse2_loc_ids = self.users_pool.read(
            cr, uid, user_ids[1], ['location_ids'])['location_ids']
        hca_loc_ids = self.users_pool.read(
            cr, uid, user_ids[2], ['location_ids'])['location_ids']
        self.assertEqual(len(nurse1_loc_ids), 5)
        self.assertEqual(len(nurse2_loc_ids), 5)
        self.assertEqual(len(hca_loc_ids), 10)
        for loc_id in nurse1_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")
        for loc_id in nurse2_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")
        for loc_id in hca_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")

    def test_03_nursing_new_shift_allocation(self):
        cr, uid = self.cr, self.uid
        wm_uid = self.users['wm'][1]

        # Step 0: Follow some Patients
        self.api_pool.admit(cr, self.admin_uid, 'hn0', {'location': 'WARD0'})
        self.api_pool.admit(cr, self.admin_uid, 'hn1', {'location': 'WARD0'})
        follow_id = self.follow_pool.create_activity(
            cr, uid, {'user_id': self.users['ns'][2]},
            {'patient_ids': [[6, 0, self.patients[:2]]]})
        self.activity_pool.complete(cr, uid, follow_id)

        # Step 1: The Ward Manager opens the wizard
        sawiz_id = self.staff_allocation.create(cr, wm_uid, {})
        self.assertTrue(sawiz_id, msg="Staff Allocation wizard not created")

        # Step 2: Selecting the Ward
        ward_id = self.location_pool.search(
            cr, uid, [['code', '=', 'WARD0']])[0]
        self.staff_allocation.write(cr, wm_uid, sawiz_id, {'ward_id': ward_id})
        self.staff_allocation.submit_wards(cr, wm_uid, sawiz_id)
        location_ids = self.staff_allocation.read(
            cr, uid, sawiz_id, ['location_ids'])['location_ids']

        # Step 3: De-allocation
        self.staff_allocation.deallocate(cr, wm_uid, sawiz_id)
        self.assertEqual(self.staff_allocation.read(
            cr, uid, sawiz_id, ['stage'])['stage'], 'users')
        self.assertEqual(len(self.users_pool.search(
            cr, uid, [['location_ids', 'in', location_ids]])), 1)
        allocating_ids = self.staff_allocation.read(
            cr, uid, sawiz_id, ['allocating_ids'])['allocating_ids']
        self.assertFalse(self.users_pool.search(
            cr, uid, [['following_ids', 'in', self.patients]]),
            msg="Patients still being followed after de-allocationg")

        # Step 4: Selecting the Nursing Staff
        user_ids = [self.users['ns'][0], self.users['ns'][1],
                    self.users['hc'][0]]
        self.staff_allocation.write(cr, wm_uid, sawiz_id,
                                    {'user_ids': [[6, 0, user_ids]]})
        self.staff_allocation.submit_users(cr, wm_uid, sawiz_id)

        # Step 5: Allocating users to Beds
        alternate = True
        for alid in allocating_ids:
            self.allocating.write(
                cr, wm_uid, alid,
                {'nurse_id': user_ids[0] if alternate else user_ids[1],
                 'hca_id': user_ids[2]})
            alternate = not alternate

        # Step 6: Complete Allocation
        self.staff_allocation.complete(cr, wm_uid, sawiz_id)
        nurse1_loc_ids = self.users_pool.read(
            cr, uid, user_ids[0], ['location_ids'])['location_ids']
        nurse2_loc_ids = self.users_pool.read(
            cr, uid, user_ids[1], ['location_ids'])['location_ids']
        hca_loc_ids = self.users_pool.read(
            cr, uid, user_ids[2], ['location_ids'])['location_ids']
        self.assertEqual(len(nurse1_loc_ids), 5)
        self.assertEqual(len(nurse2_loc_ids), 5)
        self.assertEqual(len(hca_loc_ids), 10)
        for loc_id in nurse1_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")
        for loc_id in nurse2_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")
        for loc_id in hca_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")

    def test_04_medical_staff_allocation(self):
        cr, uid = self.cr, self.uid
        wm_uid = self.users['wm'][1]
        ward_id = self.location_pool.search(cr, uid,
                                            [['code', '=', 'WARD0']])[0]

        # Step 1: The Ward Manager opens the wizard
        dawiz_id = self.doctor_allocation.create(cr, wm_uid, {})
        self.assertTrue(dawiz_id, msg="Medical Allocation wizard not created")
        self.assertEqual(self.doctor_allocation.read(
            cr, uid, dawiz_id, ['stage'])['stage'], 'review')
        self.assertEqual(self.doctor_allocation.read(
            cr, uid, dawiz_id, ['ward_id'])['ward_id'][0], ward_id)
        location_ids = self.doctor_allocation.read(
            cr, uid, dawiz_id, ['location_ids'])['location_ids']
        self.assertTrue(ward_id in location_ids,
                        msg="Ward ID missing from location ids")
        for bed_id in self.locations[ward_id]:
            self.assertTrue(bed_id in location_ids,
                            msg="Bed ID missing from location ids")
        doctor_ids = self.doctor_allocation.read(
            cr, uid, dawiz_id, ['doctor_ids'])['doctor_ids']
        self.assertFalse(doctor_ids,
                         msg="Found medical staff assigned to the Ward!")

        # Step 2: De-allocation
        self.doctor_allocation.deallocate(cr, wm_uid, dawiz_id)
        self.assertEqual(self.doctor_allocation.read(
            cr, uid, dawiz_id, ['stage'])['stage'], 'users')
        self.assertEqual(len(self.users_pool.search(
            cr, uid, [
                ['location_ids', 'in', location_ids],
                ['groups_id.name', 'in', ['NH Clinical Doctor Group']]
            ])), 0)

        # Step 3: Selecting the Medical Staff
        user_ids = [self.users['dr'][0], self.users['dr'][1]]
        self.doctor_allocation.write(cr, wm_uid, dawiz_id,
                                     {'user_ids': [[6, 0, user_ids]]})
        self.doctor_allocation.submit_users(cr, wm_uid, dawiz_id)
        doctor1_loc_ids = self.users_pool.read(
            cr, uid, user_ids[0], ['location_ids'])['location_ids']
        doctor2_loc_ids = self.users_pool.read(
            cr, uid, user_ids[0], ['location_ids'])['location_ids']
        self.assertEqual(len(doctor1_loc_ids), 1)
        self.assertEqual(len(doctor2_loc_ids), 1)
        for loc_id in doctor1_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")
        for loc_id in doctor2_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")

    def test_05_medical_staff_new_shift_allocation(self):
        cr, uid = self.cr, self.uid
        wm_uid = self.users['wm'][1]

        # Step 1: The Ward Manager opens the wizard
        dawiz_id = self.doctor_allocation.create(cr, wm_uid, {})
        self.assertTrue(dawiz_id, msg="Medical Allocation wizard not created")
        location_ids = self.doctor_allocation.read(
            cr, uid, dawiz_id, ['location_ids'])['location_ids']
        doctor_ids = self.doctor_allocation.read(
            cr, uid, dawiz_id, ['doctor_ids'])['doctor_ids']
        self.assertEqual(len(doctor_ids), 2)
        for d_id in doctor_ids:
            self.assertTrue(d_id in [self.users['dr'][0], self.users['dr'][1]])

        # Step 2: De-allocation
        self.doctor_allocation.deallocate(cr, wm_uid, dawiz_id)
        self.assertEqual(len(self.users_pool.search(cr, uid, [
            ['location_ids', 'in', location_ids],
            ['groups_id.name', 'in', ['NH Clinical Doctor Group']]])), 0)

        # Step 3: Selecting the Medical Staff
        user_ids = [self.users['dr'][2]]
        self.doctor_allocation.write(cr, wm_uid, dawiz_id,
                                     {'user_ids': [[6, 0, user_ids]]})
        self.doctor_allocation.submit_users(cr, wm_uid, dawiz_id)
        doctor_loc_ids = self.users_pool.read(
            cr, uid, user_ids[0], ['location_ids'])['location_ids']
        self.assertEqual(len(doctor_loc_ids), 1)
        for loc_id in doctor_loc_ids:
            self.assertTrue(loc_id in location_ids,
                            msg="User assigned to wrong location")
