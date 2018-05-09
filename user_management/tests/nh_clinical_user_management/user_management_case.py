from openerp import SUPERUSER_ID
from openerp.tests.common import TransactionCase


class UserManagementCase(TransactionCase):
    """
    Common functionality for testing nh.clinical.user.management
    """
    def setUp(self):
        super(UserManagementCase, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.create_locations()
        self.test_utils_model.copy_instance_variables(self)
        self.shift_coordinator = \
            self.test_utils_model.create_shift_coordinator()

        self.superuser = self.env(user=SUPERUSER_ID).user

        self.category_model = self.env['res.partner.category']
        self.hca_role = self.category_model.search([('name', '=', 'HCA')])[0]
        self.nurse_role = \
            self.category_model.search([('name', '=', 'Nurse')])[0]
        self.shift_coordinator_role = \
            self.category_model.search([('name', '=', 'Shift Coordinator')])[0]

        self.user_management_model = self.env['nh.clinical.user.management']
