from .user_management_case import UserManagementCase
from openerp.osv.orm import except_orm


class TestActivateDeactivate(UserManagementCase):
    """
    Test that when user presses activate/deactivate button for user that
    it does indeed activate / deactivate their account
    """

    def setUp(self):
        super(TestActivateDeactivate, self).setUp()
        self.hca = self.test_utils_model.create_hca()
        self.deactivated_hca = self.test_utils_model.create_hca()
        self.user_management_model.sudo(self.shift_coordinator.id)\
            .browse(self.deactivated_hca.id).deactivate()

    def test_deactivate_other_user(self):
        """
        Test that user can deactivate any subordinate users
        """
        record = self.user_management_model.sudo(self.shift_coordinator.id)\
            .browse(self.hca.id)
        self.assertTrue(record.deactivate())
        self.assertFalse(self.hca.active, msg="User not deactivated")

    def test_raises_on_deactivating_self(self):
        """
        Test that user cannot deactive themselves
        """
        record = self.user_management_model.sudo(self.shift_coordinator.id)\
            .browse(self.shift_coordinator.id)
        with self.assertRaises(except_orm):
            record.deactivate()

    def test_reactivate(self):
        """
        Test that can reactivate deactivated users
        """
        record = self.user_management_model.sudo(self.shift_coordinator.id)\
            .browse(self.deactivated_hca.id)
        self.assertTrue(record.activate())
        self.assertTrue(self.deactivated_hca.active, msg="User not activated")

    def test_search_read_shows_deactivated(self):
        """
        Test that search_read on nh.clinical.user.management will return
        deactivated user
        """
        domain = [
            ['login', 'not in', ['adt', 'admin']],
            ['active', '=', False]
        ]
        deactivated_ids = \
            [rec.get('id') for rec in self.user_management_model
                .sudo(self.shift_coordinator).search_read(domain)]
        self.assertTrue(self.deactivated_hca.id in deactivated_ids)
