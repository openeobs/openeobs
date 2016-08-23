from openerp.tests.common import SingleTransactionCase


class TestUsers(SingleTransactionCase):

    def setUp(self):
        """***setup user management tests***"""
        super(TestUsers, self).setUp()
        self.users_pool = self.registry('res.users')
        self.groups_pool = self.registry('res.groups')
        self.activity_pool = self.registry('nh.activity')
        self.location_pool = self.registry('nh.clinical.location')
        self.responsibility_allocation = self.registry(
            'nh.clinical.responsibility.allocation')
        self.userboard = self.registry('nh.clinical.userboard')
        self.userboard_admin = self.registry('nh.clinical.admin.userboard')
        self.apidemo = self.registry('nh.clinical.api.demo')

    def test_responsibility_allocation(self):
        cr, uid = self.cr, self.uid
        users = {
            'shift_coordinators': {
                'wm1': ['wm1', 'U'],
                'wm2': ['wm2', 'T']
            },
            'nurses': {
                'nurse1': ['nurse1', ['U0', 'U1']],
                'nurse2': ['nurse2', ['T0', 'T1']]
            },
            'hcas': {
                'hca1': ['hca1', ['U0', 'U1', 'T0', 'T1']]
            },
            'doctors': {
                'doctor1': ['doctor1', ['U0', 'U1', 'T0', 'T1']]
            }
        }

        self.apidemo.build_unit_test_env(cr, uid, context='eobs', users=users)

        wm1_id = self.users_pool.search(cr, uid, [('login', '=', 'wm1')])[0]

        nurse1_id = self.users_pool.search(cr, uid,
                                           [('login', '=', 'nurse1')])[0]

        ward_U_id = self.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        ward_T_id = self.location_pool.search(cr, uid, [('code', '=', 'T')])[0]

        # Adding and Removing a ward responsibility to a ward manager
        ra_id = self.responsibility_allocation.create(
            cr, uid, {'user_id': wm1_id,
                      'location_ids': [[6, False, [ward_T_id, ward_U_id]]]})
        self.responsibility_allocation.submit(cr, uid, [ra_id])
        spell_ids = self.activity_pool.search(
            cr, uid, [('data_model', '=', 'nh.clinical.spell'),
                      ('location_id', 'in', [ward_U_id, ward_T_id])])
        for spell_id in spell_ids:
            self.assertTrue(self.activity_pool.search(
                cr, uid, [('id', '=', spell_id),
                          ('user_ids', 'in', [wm1_id])]))
        ra_id = self.responsibility_allocation.create(
            cr, uid, {'user_id': wm1_id,
                      'location_ids': [[6, False, [ward_U_id]]]})
        self.responsibility_allocation.submit(cr, uid, [ra_id])
        spell_ids = self.activity_pool.search(
            cr, uid, [('data_model', '=', 'nh .clinical.spell'),
                      ('location_id', 'in', [ward_T_id])])
        for spell_id in spell_ids:
            self.assertFalse(self.activity_pool.search(
                cr, uid, [('id', '=', spell_id),
                          ('user_ids', 'in', [wm1_id])]))
        # Adding and Removing responsibilities to a nurse
        ra_id = self.responsibility_allocation.create(
            cr, uid, {'user_id': nurse1_id,
                      'location_ids': [[6, False, [ward_T_id]]]})
        self.responsibility_allocation.submit(cr, uid, [ra_id])
        observation_ids = self.activity_pool.search(
            cr, uid, [('data_model', 'ilike', '%observation%'),
                      ('location_id', 'child_of', [ward_T_id])])
        notification_ids = self.activity_pool.search(
            cr, uid, [('data_model', 'ilike', '%notification%'),
                      ('location_id', 'child_of', [ward_T_id])])
        for activity_id in observation_ids+notification_ids:
            self.assertTrue(self.activity_pool.search(
                cr, uid, [('id', '=', activity_id),
                          ('user_ids', 'in', [nurse1_id])]))
        observation_ids = self.activity_pool.search(
            cr, uid, [('data_model', 'ilike', '%observation%'),
                      ('location_id', 'child_of', [ward_U_id])])
        notification_ids = self.activity_pool.search(
            cr, uid, [('data_model', 'ilike', '%notification%'),
                      ('location_id', 'child_of', [ward_U_id])])
        for activity_id in observation_ids+notification_ids:
            self.assertFalse(self.activity_pool.search(
                cr, uid, [('id', '=', activity_id),
                          ('user_ids', 'in', [nurse1_id])]))

    def test_staff_management_create_and_update(self):
        cr, uid = self.cr, self.uid

        # STAFF MANAGEMENT CREATE
        # Creating a HCA
        new_hca_id = self.userboard.create(
            cr, uid, {'name': 'Demo HCA', 'login': 'demohca',
                      'password': 'demohca', 'hca': True})
        self.assertTrue(new_hca_id, msg='Error on userboard create')
        check_user_id = self.users_pool.search(cr, uid,
                                               [('login', '=', 'demohca')])
        self.assertTrue(check_user_id, msg='HCA user was not created')
        hca_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in hca_user.groups_id]
        self.assertTrue('NH Clinical HCA Group' in check_groups,
                        msg='HCA user does not have HCA group')
        # Creating a Nurse
        new_nurse_id = self.userboard.create(
            cr, uid, {'name': 'Demo Nurse', 'login': 'demonurse',
                      'password': 'demonurse', 'nurse': True})
        self.assertTrue(new_nurse_id, msg='Error on userboard create')
        check_user_id = self.users_pool.search(cr, uid,
                                               [('login', '=', 'demonurse')])
        self.assertTrue(check_user_id, msg='Nurse user was not created')
        nurse_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertTrue('NH Clinical Nurse Group' in check_groups,
                        msg='Nurse user does not have Nurse group')
        # Creating a Doctor
        new_doctor_id = self.userboard.create(
            cr, uid, {'name': 'Demo Doctor', 'login': 'demodoctor',
                      'password': 'demodoctor', 'doctor': True})
        self.assertTrue(new_doctor_id, msg='Error on userboard create')
        check_user_id = self.users_pool.search(cr, uid,
                                               [('login', '=', 'demodoctor')])
        self.assertTrue(check_user_id, msg='Doctor user was not created')
        doctor_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in doctor_user.groups_id]
        self.assertTrue('NH Clinical Doctor Group' in check_groups,
                        msg='Doctor user does not have Doctor group')
        # Creating a Ward Manager
        new_shift_coordinator_id = self.userboard.create(
            cr, uid, {'name': 'Demo Shift Coordinator',
                      'login': 'demoshift_coordinator',
                      'password': 'demoshift_coordinator',
                      'shift_coordinator': True})
        self.assertTrue(new_shift_coordinator_id,
                        msg='Error on userboard create')
        check_user_id = self.users_pool.search(
            cr, uid, [('login', '=', 'demoshift_coordinator')])
        self.assertTrue(check_user_id,
                        msg='Shift Coordinator user was not created')
        shift_coordinator_user = self.users_pool.browse(cr, uid,
                                                        check_user_id[0])
        check_groups = [g.name for g in shift_coordinator_user.groups_id]
        self.assertTrue(
            'NH Clinical Shift Coordinator Group' in check_groups,
            msg='Shift Coordinator user does not have Shift Coordinator group')
        self.assertTrue(
            'Contact Creation' in check_groups,
            msg='Shift Coordinator user does not have Contact Creation group')
        # STAFF MANAGEMENT UPDATE
        # Adding HCA Group
        self.assertTrue(self.userboard.write(
            cr, uid, [new_nurse_id], {'hca': True}),
            msg='Error on Userboard write')
        nurse_user = self.users_pool.browse(cr, uid, new_nurse_id)
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertTrue(
            'NH Clinical HCA Group' in check_groups,
            msg='Nurse user does not have HCA group (after update)')
        self.assertTrue(
            'NH Clinical Nurse Group' in check_groups,
            msg='Nurse user does not have Nurse group (after update)')
        # Adding Nurse Group
        self.assertTrue(self.userboard.write(
            cr, uid, [new_shift_coordinator_id], {'nurse': True}),
            msg='Error on Userboard write')
        shift_coordinator_user = self.users_pool.browse(
            cr, uid, new_shift_coordinator_id
        )
        check_groups = [g.name for g in shift_coordinator_user.groups_id]
        self.assertTrue('NH Clinical Shift Coordinator Group' in check_groups,
                        msg='Shift Coordinator user does not have Shift '
                            'Coordinator group (after update)')
        self.assertTrue('NH Clinical Nurse Group' in check_groups,
                        msg='Shift Coordinator user does not have Nurse '
                            'group (after update)')
        self.assertTrue('Contact Creation' in check_groups,
                        msg='Shift Coordinator user does not have Contact '
                            'Creation group (after update)')
        # Adding Ward Manager Group
        self.assertTrue(self.userboard.write(
            cr, uid, [new_hca_id], {'shift_coordinator': True}),
            msg='Error on Userboard write')
        hca_user = self.users_pool.browse(cr, uid, new_hca_id)
        check_groups = [g.name for g in hca_user.groups_id]
        self.assertTrue('NH Clinical HCA Group' in check_groups,
                        msg='HCA user does not have HCA group (after update)')
        self.assertTrue(
            'NH Clinical Shift Coordinator Group' in check_groups,
            msg='HCA user does not have Shift Coordinator group (after update)'
        )
        self.assertTrue(
            'Contact Creation' in check_groups,
            msg='HCA user does not have Contact Creation group (after update)'
        )
        # Adding Doctor Group and Removing HCA Group
        self.assertTrue(self.userboard.write(
            cr, uid, [new_nurse_id], {'hca': False, 'doctor': True}),
            msg='Error on Userboard write')
        nurse_user = self.users_pool.browse(cr, uid, new_nurse_id)
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertFalse('NH Clinical HCA Group' in check_groups,
                         msg='Nurse user has HCA group (after 2nd update)')
        self.assertTrue(
            'NH Clinical Nurse Group' in check_groups,
            msg='Nurse user does not have Nurse group (after 2nd update)')
        self.assertTrue(
            'NH Clinical Doctor Group' in check_groups,
            msg='Nurse user does not have Doctor group (after 2nd update)')

    def test_admin_user_management_create_and_update(self):
        cr, uid = self.cr, self.uid

        # STAFF MANAGEMENT CREATE
        # Creating a HCA
        new_hca_id = self.userboard_admin.create(
            cr, uid, {'name': 'Demo HCA', 'login': 'adminhca',
                      'password': 'adminhca', 'hca': True})
        self.assertTrue(new_hca_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid,
                                               [('login', '=', 'adminhca')])
        self.assertTrue(check_user_id, msg='HCA user was not created')
        hca_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in hca_user.groups_id]
        self.assertTrue('NH Clinical HCA Group' in check_groups,
                        msg='HCA user does not have HCA group')
        # Creating a Nurse
        new_nurse_id = self.userboard_admin.create(
            cr, uid, {'name': 'Demo Nurse', 'login': 'adminnurse',
                      'password': 'adminnurse', 'nurse': True})
        self.assertTrue(new_nurse_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid,
                                               [('login', '=', 'adminnurse')])
        self.assertTrue(check_user_id, msg='Nurse user was not created')
        nurse_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertTrue('NH Clinical Nurse Group' in check_groups,
                        msg='Nurse user does not have Nurse group')
        # Creating a Doctor
        new_doctor_id = self.userboard_admin.create(
            cr, uid, {'name': 'Demo Doctor', 'login': 'admindoctor',
                      'password': 'admindoctor', 'doctor': True})
        self.assertTrue(new_doctor_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid,
                                               [('login', '=', 'admindoctor')])
        self.assertTrue(check_user_id, msg='Doctor user was not created')
        doctor_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in doctor_user.groups_id]
        self.assertTrue('NH Clinical Doctor Group' in check_groups,
                        msg='Doctor user does not have Doctor group')
        # Creating a Ward Manager
        new_shift_coordinator_id = self.userboard_admin.create(
            cr, uid, {'name': 'Demo Shift Coordinator',
                      'login': 'adminshift_coordinator',
                      'password': 'adminshift_coordinator',
                      'shift_coordinator': True})
        self.assertTrue(new_shift_coordinator_id,
                        msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(
            cr, uid, [('login', '=', 'adminshift_coordinator')])
        self.assertTrue(check_user_id,
                        msg='Shift Coordinator user was not created')
        shift_coordinator_user = self.users_pool.browse(cr, uid,
                                                        check_user_id[0])
        check_groups = [g.name for g in shift_coordinator_user.groups_id]
        self.assertTrue(
            'NH Clinical Shift Coordinator Group' in check_groups,
            msg='Shift Coordinator user does not have Shift Coordinator group')
        self.assertTrue(
            'Contact Creation' in check_groups,
            msg='Shift Coordinator user does not have Contact Creation group')
        # Creating an Admin
        new_admin_id = self.userboard_admin.create(
            cr, uid, {'name': 'Demo Admin', 'login': 'admintest',
                      'password': 'admintest', 'admin': True})
        self.assertTrue(new_admin_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid,
                                               [('login', '=', 'admintest')])
        self.assertTrue(check_user_id, msg='Admin user was not created')
        admin_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in admin_user.groups_id]
        self.assertTrue('NH Clinical Admin Group' in check_groups,
                        msg='Admin user does not have Admin group')
        self.assertTrue('Contact Creation' in check_groups,
                        msg='Admin user does not have Contact Creation group')
        # STAFF MANAGEMENT UPDATE
        # Adding HCA Group
        self.assertTrue(self.userboard_admin.write(
            cr, uid, [new_nurse_id], {'hca': True}),
            msg='Error on Userboard write')
        nurse_user = self.users_pool.browse(cr, uid, new_nurse_id)
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertTrue(
            'NH Clinical HCA Group' in check_groups,
            msg='Nurse user does not have HCA group (after update)')
        self.assertTrue(
            'NH Clinical Nurse Group' in check_groups,
            msg='Nurse user does not have Nurse group (after update)')
        # Adding Nurse Group
        self.assertTrue(self.userboard_admin.write(
            cr, uid, [new_shift_coordinator_id], {'nurse': True}),
            msg='Error on Userboard write')
        shift_coordinator_user = self.users_pool.browse(cr, uid,
                                                   new_shift_coordinator_id)
        check_groups = [g.name for g in shift_coordinator_user.groups_id]
        self.assertTrue('NH Clinical Shift Coordinator Group' in check_groups,
                        msg='Shift Coordinator user does not have Shift '
                            'Coordinator group (after update)')
        self.assertTrue('NH Clinical Nurse Group' in check_groups,
                        msg='Shift Coordinator user does not have Nurse '
                            'group (after update)')
        self.assertTrue('Contact Creation' in check_groups,
                        msg='Shift Coordinator user does not have Contact '
                            'Creation group (after update)')
        # Adding Ward Manager Group
        self.assertTrue(self.userboard_admin.write(
            cr, uid, [new_hca_id], {'shift_coordinator': True}),
            msg='Error on Userboard write')
        hca_user = self.users_pool.browse(cr, uid, new_hca_id)
        check_groups = [g.name for g in hca_user.groups_id]
        self.assertTrue('NH Clinical HCA Group' in check_groups,
                        msg='HCA user does not have HCA group (after update)')
        self.assertTrue(
            'NH Clinical Shift Coordinator Group' in check_groups,
            msg='HCA user does not have Shift Coordinator group (after update)'
        )
        self.assertTrue(
            'Contact Creation' in check_groups,
            msg='HCA user does not have Contact Creation group (after update)')
        # Adding Doctor Group and Removing HCA Group
        self.assertTrue(self.userboard_admin.write(
            cr, uid, [new_nurse_id], {'hca': False, 'doctor': True}),
            msg='Error on Userboard write')
        nurse_user = self.users_pool.browse(cr, uid, new_nurse_id)
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertFalse('NH Clinical HCA Group' in check_groups,
                         msg='Nurse user has HCA group (after 2nd update)')
        self.assertTrue(
            'NH Clinical Nurse Group' in check_groups,
            msg='Nurse user does not have Nurse group (after 2nd update)')
        self.assertTrue(
            'NH Clinical Doctor Group' in check_groups,
            msg='Nurse user does not have Doctor group (after 2nd update)')
        # Adding Admin Group
        self.assertTrue(self.userboard_admin.write(
            cr, uid, [new_doctor_id], {'admin': True}),
            msg='Error on Userboard write')
        doctor_user = self.users_pool.browse(cr, uid, new_doctor_id)
        check_groups = [g.name for g in doctor_user.groups_id]
        self.assertTrue(
            'NH Clinical Admin Group' in check_groups,
            msg='Doctor user does not have Admin group (after update)')
        self.assertTrue(
            'NH Clinical Doctor Group' in check_groups,
            msg='Doctor user does not have Doctor group (after update)')
        self.assertTrue('Contact Creation' in check_groups,
                        msg='Doctor user does not have Contact Creation '
                            'group (after update)')
