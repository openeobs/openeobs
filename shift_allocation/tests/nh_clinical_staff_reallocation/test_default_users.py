from openerp.tests.common import TransactionCase


# EOBS-549
class TestStaffReallocationDefaultUsers(TransactionCase):
    """
    Test the `_get_default_users` method of the
    `nh.clinical.staff.reallocation` model.
    """
    def setUp(self):
        super(TestStaffReallocationDefaultUsers, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        # Creates locations and users.
        self.test_utils.admit_and_place_patient()
        self.shift_coordinator = self.test_utils.create_shift_coordinator()
        self.nurse = self.test_utils.nurse
        self.hca = self.test_utils.hca
        self.nurse_2 = self.test_utils.create_nurse(allocate=False)
        self.hca_2 = self.test_utils.create_hca(allocate=False)

        expected_users_on_shift_ids = map(
            lambda e: e.id, [
                self.nurse, self.nurse_2, self.hca, self.hca_2
            ]
        )
        user_model = self.env['res.users']
        self.allocation_model = self.env['nh.clinical.staff.allocation']
        self.reallocation_model = self.env['nh.clinical.staff.reallocation']
        # Expected needs to be a recordset to match actual result type.
        self.expected_users_on_shift = \
            user_model.browse(expected_users_on_shift_ids)

        self._create_shift_change(
            self.test_utils.ward.id, expected_users_on_shift_ids)

    def _create_shift_change(self, ward_id, users):
        self.allocation = self.allocation_model.create({})
        # Have to assign users after creation because setting in creation
        # dictionary does not work. Not sure why.
        self.allocation.ward_id = ward_id
        self.allocation.user_ids = users
        self.allocation.complete()

    def test_returns_all_users_added_to_roll_call(self):
        """
        Ensure that all users added to the roll call of a shift are present
        in subsequent allocation records.

        The particular reason this regression test came about was because users
        who were added to the roll call but not allocated directly to beds did
        not appear in subsequent allocation wizards.
        """
        self.reallocation = self.reallocation_model.sudo(
            self.shift_coordinator).create({})
        actual_users_on_shift = self.reallocation.user_ids
        self.assertEqual(self.expected_users_on_shift, actual_users_on_shift)

    def test_returns_all_users_added_to_roll_call_shift_change_created(
            self):
        """
        During development it was discovered that creating a second allocation
        record (opening the shift change wizard again without confirming)
        before reallocation caused an error. This test checks that no error is
        raised and the correct users are still returned.
        """
        self.allocation_model.create({})
        self.reallocation = self.reallocation_model.sudo(
            self.shift_coordinator).create({})
        actual_users_on_shift = self.reallocation.user_ids
        self.assertEqual(self.expected_users_on_shift, actual_users_on_shift)
