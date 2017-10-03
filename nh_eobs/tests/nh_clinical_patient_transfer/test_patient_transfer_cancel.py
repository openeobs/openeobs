# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestPatientTransferCancel(TransactionCase):

    def setUp(self):
        super(TestPatientTransferCancel, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.placement_model = self.env['nh.clinical.patient.placement']
        self.bed_id_before_transfer = self.patient.current_location_id

    def call_test(self):
        self.placement_ward_a = self.placement_model.search([
            ('patient_id', '=', self.patient.id),
        ])
        self.placement_ward_a.ensure_one()

        ward_b_code = self.test_utils.other_ward.code
        self.test_utils.transfer_patient(ward_b_code)
        self.bed_id_after_transfer = self.patient.current_location_id

        self.placement_ward_b = self.get_open_placements()
        self.placement_ward_b.ensure_one()

        self.transfer_model = self.env['nh.clinical.patient.transfer']
        transfer = self.transfer_model.search([
            ('patient_id', '=', self.patient.id)
        ])
        transfer.ensure_one()
        transfer.cancel(transfer.activity_id.id)

    def test_new_placement_scheduled_when_original_bed_is_not_available(self):
        """
        If the bed the patient was in before is no longer available then a new
        placement should be created for their original ward.
        """
        self.call_test()
        placement = self.get_open_placements()
        self.assertEqual(1, len(placement))
        self.assertEqual('scheduled', placement.state)
        self.assertNotEqual(placement.id, self.placement_ward_a.id)
        self.assertNotEqual(placement.id, self.placement_ward_b.id)

    def test_only_shift_coordinator_from_original_ward_in_user_ids(self):
        """
        Regression for EOBS-1631. Patients should not be visible in the
        'Patients by Ward' view after their transfer to that ward has been
        cancelled.

        It seems that this view only shows placements when the ID of the
        viewing user (a shift coordinator) is in the `user_ids` of the
        placement record. Therefore asserting that the shift coordinator's
        user ID is not present should assert that it is not visible in the
        'Patients by Ward' view.
        """
        ward_a = self.test_utils.ward
        shift_coordinator_ward_a = self.test_utils.create_shift_coordinator(
            ward_a.id)
        ward_b = self.test_utils.other_ward
        shift_coordinator_ward_b = self.test_utils.create_shift_coordinator(
            ward_b.id)

        self.call_test()

        placement = self.get_open_placements()
        placement.ensure_one()

        self.assertNotIn(shift_coordinator_ward_b.id, placement.user_ids)
        self.assertIn(shift_coordinator_ward_a.id, placement.user_ids)
