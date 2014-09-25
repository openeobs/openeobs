from openerp.tests.common import SingleTransactionCase

class TestUsers(SingleTransactionCase):

    def setUp(self):
        """***setup user management tests***"""
        super(TestUsers, self).setUp()
        cr, uid, = self.cr, self.uid

        self.users_pool = self.registry('res.users')
        self.groups_pool = self.registry('res.groups')
        self.activity_pool = self.registry('t4.activity')
        self.location_pool = self.registry('t4.clinical.location')
        # self.responsibility_allocation_wiz = self.registry('t4skr.responsibility.allocation.wizard')
        self.userboard = self.registry('t4.clinical.userboard')
        self.userboard_admin = self.registry('t4.clinical.admin.userboard')
        
    def test_staff_management_create_and_update(self):
        cr, uid = self.cr, self.uid

        # STAFF MANAGEMENT CREATE
        # Creating a HCA
        new_hca_id = self.userboard.create(cr, uid, {'name': 'Demo HCA', 'login': 'demohca', 'password': 'demohca', 'hca': True})
        self.assertTrue(new_hca_id, msg='Error on userboard create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'demohca')])
        self.assertTrue(check_user_id, msg='HCA user was not created')        
        hca_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in hca_user.groups_id]
        self.assertTrue('T4 Clinical HCA Group' in check_groups, msg='HCA user does not have HCA group')
        # Creating a Nurse
        new_nurse_id = self.userboard.create(cr, uid, {'name': 'Demo Nurse', 'login': 'demonurse', 'password': 'demonurse', 'nurse': True})
        self.assertTrue(new_nurse_id, msg='Error on userboard create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'demonurse')])
        self.assertTrue(check_user_id, msg='Nurse user was not created')
        nurse_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertTrue('T4 Clinical Nurse Group' in check_groups, msg='Nurse user does not have Nurse group')
        # Creating a Doctor
        new_doctor_id = self.userboard.create(cr, uid, {'name': 'Demo Doctor', 'login': 'demodoctor', 'password': 'demodoctor', 'doctor': True})
        self.assertTrue(new_doctor_id, msg='Error on userboard create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'demodoctor')])
        self.assertTrue(check_user_id, msg='Doctor user was not created')
        doctor_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in doctor_user.groups_id]
        self.assertTrue('T4 Clinical Doctor Group' in check_groups, msg='Doctor user does not have Doctor group')
        # Creating a Ward Manager
        new_ward_manager_id = self.userboard.create(cr, uid, {'name': 'Demo Ward Manager', 'login': 'demoward_manager', 'password': 'demoward_manager', 'ward_manager': True})
        self.assertTrue(new_ward_manager_id, msg='Error on userboard create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'demoward_manager')])
        self.assertTrue(check_user_id, msg='Ward Manager user was not created')
        ward_manager_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in ward_manager_user.groups_id]
        self.assertTrue('T4 Clinical Ward Manager Group' in check_groups, msg='Ward Manager user does not have Ward Manager group')
        self.assertTrue('Contact Creation' in check_groups, msg='Ward Manager user does not have Contact Creation group')
        # STAFF MANAGEMENT UPDATE
        # Adding HCA Group
        self.assertTrue(self.userboard.write(cr, uid, [new_nurse_id], {'hca': True}), msg='Error on Userboard write')
        nurse_user = self.users_pool.browse(cr, uid, new_nurse_id)
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertTrue('T4 Clinical HCA Group' in check_groups, msg='Nurse user does not have HCA group (after update)')
        self.assertTrue('T4 Clinical Nurse Group' in check_groups, msg='Nurse user does not have Nurse group (after update)')        
        # Adding Nurse Group
        self.assertTrue(self.userboard.write(cr, uid, [new_ward_manager_id], {'nurse': True}), msg='Error on Userboard write')
        ward_manager_user = self.users_pool.browse(cr, uid, new_ward_manager_id)
        check_groups = [g.name for g in ward_manager_user.groups_id]
        self.assertTrue('T4 Clinical Ward Manager Group' in check_groups, msg='Ward Manager user does not have Ward Manager group (after update)')
        self.assertTrue('T4 Clinical Nurse Group' in check_groups, msg='Ward Manager user does not have Nurse group (after update)')
        self.assertTrue('Contact Creation' in check_groups, msg='Ward Manager user does not have Contact Creation group (after update)')        
        # Adding Ward Manager Group
        self.assertTrue(self.userboard.write(cr, uid, [new_hca_id], {'ward_manager': True}), msg='Error on Userboard write')
        hca_user = self.users_pool.browse(cr, uid, new_hca_id)
        check_groups = [g.name for g in hca_user.groups_id]
        self.assertTrue('T4 Clinical HCA Group' in check_groups, msg='HCA user does not have HCA group (after update)')
        self.assertTrue('T4 Clinical Ward Manager Group' in check_groups, msg='HCA user does not have Ward Manager group (after update)')
        self.assertTrue('Contact Creation' in check_groups, msg='HCA user does not have Contact Creation group (after update)')
        # Adding Doctor Group and Removing HCA Group
        self.assertTrue(self.userboard.write(cr, uid, [new_nurse_id], {'hca': False, 'doctor': True}), msg='Error on Userboard write')
        nurse_user = self.users_pool.browse(cr, uid, new_nurse_id)
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertFalse('T4 Clinical HCA Group' in check_groups, msg='Nurse user has HCA group (after 2nd update)')
        self.assertTrue('T4 Clinical Nurse Group' in check_groups, msg='Nurse user does not have Nurse group (after 2nd update)')
        self.assertTrue('T4 Clinical Doctor Group' in check_groups, msg='Nurse user does not have Doctor group (after 2nd update)')
        
    def test_admin_user_management_create_and_update(self):
        cr, uid = self.cr, self.uid

        # STAFF MANAGEMENT CREATE
        # Creating a HCA
        new_hca_id = self.userboard_admin.create(cr, uid, {'name': 'Demo HCA', 'login': 'adminhca', 'password': 'adminhca', 'hca': True})
        self.assertTrue(new_hca_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'adminhca')])
        self.assertTrue(check_user_id, msg='HCA user was not created')        
        hca_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in hca_user.groups_id]
        self.assertTrue('T4 Clinical HCA Group' in check_groups, msg='HCA user does not have HCA group')
        # Creating a Nurse
        new_nurse_id = self.userboard_admin.create(cr, uid, {'name': 'Demo Nurse', 'login': 'adminnurse', 'password': 'adminnurse', 'nurse': True})
        self.assertTrue(new_nurse_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'adminnurse')])
        self.assertTrue(check_user_id, msg='Nurse user was not created')
        nurse_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertTrue('T4 Clinical Nurse Group' in check_groups, msg='Nurse user does not have Nurse group')
        # Creating a Doctor
        new_doctor_id = self.userboard_admin.create(cr, uid, {'name': 'Demo Doctor', 'login': 'admindoctor', 'password': 'admindoctor', 'doctor': True})
        self.assertTrue(new_doctor_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'admindoctor')])
        self.assertTrue(check_user_id, msg='Doctor user was not created')
        doctor_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in doctor_user.groups_id]
        self.assertTrue('T4 Clinical Doctor Group' in check_groups, msg='Doctor user does not have Doctor group')
        # Creating a Ward Manager
        new_ward_manager_id = self.userboard_admin.create(cr, uid, {'name': 'Demo Ward Manager', 'login': 'adminward_manager', 'password': 'adminward_manager', 'ward_manager': True})
        self.assertTrue(new_ward_manager_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'adminward_manager')])
        self.assertTrue(check_user_id, msg='Ward Manager user was not created')
        ward_manager_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in ward_manager_user.groups_id]
        self.assertTrue('T4 Clinical Ward Manager Group' in check_groups, msg='Ward Manager user does not have Ward Manager group')
        self.assertTrue('Contact Creation' in check_groups, msg='Ward Manager user does not have Contact Creation group')
        # Creating an Admin
        new_admin_id = self.userboard_admin.create(cr, uid, {'name': 'Demo Admin', 'login': 'admintest', 'password': 'admintest', 'admin': True})
        self.assertTrue(new_admin_id, msg='Error on userboard_admin create')
        check_user_id = self.users_pool.search(cr, uid, [('login', '=', 'admintest')])
        self.assertTrue(check_user_id, msg='Admin user was not created')
        admin_user = self.users_pool.browse(cr, uid, check_user_id[0])
        check_groups = [g.name for g in admin_user.groups_id]
        self.assertTrue('T4 Clinical Admin Group' in check_groups, msg='Admin user does not have Admin group')
        self.assertTrue('Contact Creation' in check_groups, msg='Admin user does not have Contact Creation group')
        # STAFF MANAGEMENT UPDATE
        # Adding HCA Group
        self.assertTrue(self.userboard_admin.write(cr, uid, [new_nurse_id], {'hca': True}), msg='Error on Userboard write')
        nurse_user = self.users_pool.browse(cr, uid, new_nurse_id)
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertTrue('T4 Clinical HCA Group' in check_groups, msg='Nurse user does not have HCA group (after update)')
        self.assertTrue('T4 Clinical Nurse Group' in check_groups, msg='Nurse user does not have Nurse group (after update)')        
        # Adding Nurse Group
        self.assertTrue(self.userboard_admin.write(cr, uid, [new_ward_manager_id], {'nurse': True}), msg='Error on Userboard write')
        ward_manager_user = self.users_pool.browse(cr, uid, new_ward_manager_id)
        check_groups = [g.name for g in ward_manager_user.groups_id]
        self.assertTrue('T4 Clinical Ward Manager Group' in check_groups, msg='Ward Manager user does not have Ward Manager group (after update)')
        self.assertTrue('T4 Clinical Nurse Group' in check_groups, msg='Ward Manager user does not have Nurse group (after update)')
        self.assertTrue('Contact Creation' in check_groups, msg='Ward Manager user does not have Contact Creation group (after update)')        
        # Adding Ward Manager Group
        self.assertTrue(self.userboard_admin.write(cr, uid, [new_hca_id], {'ward_manager': True}), msg='Error on Userboard write')
        hca_user = self.users_pool.browse(cr, uid, new_hca_id)
        check_groups = [g.name for g in hca_user.groups_id]
        self.assertTrue('T4 Clinical HCA Group' in check_groups, msg='HCA user does not have HCA group (after update)')
        self.assertTrue('T4 Clinical Ward Manager Group' in check_groups, msg='HCA user does not have Ward Manager group (after update)')
        self.assertTrue('Contact Creation' in check_groups, msg='HCA user does not have Contact Creation group (after update)')
        # Adding Doctor Group and Removing HCA Group
        self.assertTrue(self.userboard_admin.write(cr, uid, [new_nurse_id], {'hca': False, 'doctor': True}), msg='Error on Userboard write')
        nurse_user = self.users_pool.browse(cr, uid, new_nurse_id)
        check_groups = [g.name for g in nurse_user.groups_id]
        self.assertFalse('T4 Clinical HCA Group' in check_groups, msg='Nurse user has HCA group (after 2nd update)')
        self.assertTrue('T4 Clinical Nurse Group' in check_groups, msg='Nurse user does not have Nurse group (after 2nd update)')
        self.assertTrue('T4 Clinical Doctor Group' in check_groups, msg='Nurse user does not have Doctor group (after 2nd update)')
        # Adding Admin Group
        self.assertTrue(self.userboard_admin.write(cr, uid, [new_doctor_id], {'admin': True}), msg='Error on Userboard write')
        doctor_user = self.users_pool.browse(cr, uid, new_doctor_id)
        check_groups = [g.name for g in doctor_user.groups_id]
        self.assertTrue('T4 Clinical Admin Group' in check_groups, msg='Doctor user does not have Admin group (after update)')
        self.assertTrue('T4 Clinical Doctor Group' in check_groups, msg='Doctor user does not have Doctor group (after update)')
        self.assertTrue('Contact Creation' in check_groups, msg='Doctor user does not have Contact Creation group (after update)')