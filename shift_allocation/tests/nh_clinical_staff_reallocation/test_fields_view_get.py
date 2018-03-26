# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


# EOBS-549, EOBS-2378
class TestFieldsViewGet(TransactionCase):
    """
    Test the field_view_get method override. This method returns a definition
    of the field which determines how it is displayed and how it behaves.
    Specifically this override is used to change the `domain` property of the
    field definition so that the when populating the field the users that are
    returned as part of the autocomplete feature are limited to only those
    users that are eligible for that field (nurses for the nurse field and
    hcas for the hca field).
    """
    def call_test(self):
        test_utils = self.env['nh.clinical.test_utils']
        test_utils.admit_and_place_patient()  # Creates locations and users.
        self.shift_coordinator = test_utils.create_shift_coordinator()
        self.nurse = test_utils.nurse
        self.hca = test_utils.hca
        self.nurse_2 = test_utils.create_nurse(allocate=False)
        self.hca_2 = test_utils.create_hca(allocate=False)

        self.expected_nurse_ids_available_for_allocation = map(
            lambda e: e.id, [
                self.nurse, self.nurse_2
            ]
        )
        self.expected_hca_ids_available_for_allocation = map(
            lambda e: e.id, [
                self.hca, self.hca_2
            ]
        )
        user_model = self.env['res.users']
        # Expected needs to be a recordset to match actual result type.
        self.expected_nurses_available_for_allocation = \
            user_model.browse(self.expected_nurse_ids_available_for_allocation)
        self.expected_hcas_available_for_allocation = \
            user_model.browse(self.expected_hca_ids_available_for_allocation)

        allocation_model = self.env['nh.clinical.staff.allocation']
        allocation = allocation_model.create({})
        # Have to assign users after creation because setting in creation
        # dictionary does not work. Not sure why.
        allocation.ward_id = test_utils.ward.id
        allocation.user_ids = self.expected_nurses_available_for_allocation \
            + self.expected_hcas_available_for_allocation
        allocation.complete()

        reallocation_model = self.env['nh.clinical.staff.reallocation'].sudo(
            self.shift_coordinator)
        reallocation_model.create({})

        allocating_model = self.env['nh.clinical.allocating'].sudo(
            self.shift_coordinator)
        fields_view = allocating_model.fields_view_get(view_type='form')
        nurse_id_field_domain = fields_view['fields']['nurse_id']['domain']
        hca_id_field_domain = fields_view['fields']['hca_ids']['domain']
        self.nurse_ids = nurse_id_field_domain[0][2]
        self.hca_ids = hca_id_field_domain[0][2]

    def test_returns_all_nurses_added_to_roll_call(self):
        """
        Only the nurses assigned to the shift are returned as autocomplete
        options in the allocating view.
        """
        self.call_test()
        self.assertEqual(
            sorted(self.expected_nurse_ids_available_for_allocation),
            sorted(self.nurse_ids)
        )

    def test_returns_all_hcas_added_to_roll_call(self):
        """
        Only the HCAs assigned to the shift are returned as autocomplete
        options in the allocating view.
        """
        self.call_test()
        self.assertEqual(
            sorted(self.expected_hca_ids_available_for_allocation),
            sorted(self.hca_ids)
        )
