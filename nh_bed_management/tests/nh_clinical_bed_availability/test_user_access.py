from openerp.tests.common import TransactionCase
from openerp.exceptions import AccessError


class TestUserAccess(TransactionCase):
    """
    Test that only the Bed Manager can access the Bed Availability model.
    As the menu permissions are tied to access to the model this will also
    test that the Bed Management menu section and it's items are only available
    to Bed Managers
    """

    def setUp(self):
        super(TestUserAccess, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.bed_availability = self.env['nh.clinical.bed_availability']
        self.test_utils.create_locations()
        self.access_error = 'Sorry, you are not allowed to access this ' \
                            'document. Only users with the following access ' \
                            'level are currently allowed to do that:\n- NH ' \
                            'Clinical/NH Clinical Bed Manager Group\n\n' \
                            '(Document model: nh.clinical.bed_availability)'

    def test_hca_cant_access(self):
        """ Test that HCA can't access Bed Availability model """
        hca = self.test_utils.create_hca()
        with self.assertRaises(AccessError) as error:
            self.bed_availability.sudo(hca).read()
        self.assertEqual(error.exception.value, self.access_error)

    def test_nurse_cant_access(self):
        """ Test that Nurse can't access Bed Availability model """
        nurse = self.test_utils.create_nurse()
        with self.assertRaises(AccessError) as error:
            self.bed_availability.sudo(nurse).read()
        self.assertEqual(error.exception.value, self.access_error)

    def test_doctor_cant_accesss(self):
        """ Test that Doctor can't access Bed Availability model """
        self.test_utils.create_doctor()
        with self.assertRaises(AccessError) as error:
            self.bed_availability.sudo(self.test_utils.doctor).read()
        self.assertEqual(error.exception.value, self.access_error)

    def test_shift_coordinator_cant_access(self):
        """ Test that Shift Coordinator can't access Bed Availability model
        """
        shift_coordinator = self.test_utils.create_shift_coordinator()
        with self.assertRaises(AccessError) as error:
            self.bed_availability.sudo(shift_coordinator).read()
        self.assertEqual(error.exception.value, self.access_error)

    def test_senior_manager_cant_access(self):
        """ Test that Senior Manager can't access Bed Availability model """
        self.test_utils.create_senior_manager()
        with self.assertRaises(AccessError) as error:
            self.bed_availability.sudo(self.test_utils.senior_manager).read()
        self.assertEqual(error.exception.value, self.access_error)

    def test_system_admin_cant_access(self):
        """ Test that System Admin can't access Bed Availability model """
        self.test_utils.create_system_admin()
        with self.assertRaises(AccessError) as error:
            self.bed_availability.sudo(self.test_utils.system_admin).read()
        self.assertEqual(error.exception.value, self.access_error)

    def test_bed_manager_can_access(self):
        """ Test that Bed Manager can access Bed Availability model """
        self.test_utils.create_bed_manager()
        beds = self.bed_availability.sudo(self.test_utils.bed_manager).read()
        self.assertIsNotNone(beds)
