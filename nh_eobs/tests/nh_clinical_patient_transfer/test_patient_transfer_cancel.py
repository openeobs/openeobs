# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestPatientTransferCancel(TransactionCase):
    """
    Test cancelling of a patient transfer.
    """
    def setUp(self):
        super(TestPatientTransferCancel, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient(create_placement=False)
        self.test_utils.copy_instance_variables(self)

        self.placement_model = self.env['nh.clinical.patient.placement']
        self.placement_ward_a = self.placement_model.search([
            ('patient_id', '=', self.patient.id),
        ])
        self.placement_ward_a.ensure_one()
        self.bed_id_before_transfer = self.patient.current_location_id

    def call_test(self, original_bed_available=True):
        self._transfer_patient()

        if not original_bed_available:
            # Put another patient in their original bed.
            self.test_utils.create_patient()
            self.test_utils.admit_patient()
            self.test_utils.create_placement()
            self.test_utils.place_patient(self.test_utils.bed.id)

        self._cancel_transfer()

    def _transfer_patient(self):
        ward_b_code = self.test_utils.other_ward.code
        self.test_utils.transfer_patient(ward_b_code)
        self.bed_id_after_transfer = self.patient.current_location_id

        self.placement_ward_b = self.get_open_placements()
        self.placement_ward_b.ensure_one()

    def _cancel_transfer(self):
        self.transfer_model = self.env['nh.clinical.patient.transfer']
        transfer = self.transfer_model.search([
            ('patient_id', '=', self.patient.id)
        ])
        transfer.ensure_one()

        transfer.cancel(transfer.activity_id.id)

    def get_open_placements(self):
        return self.placement_model.search([
            ('patient_id', '=', self.patient.id),
            ('state', 'not in', ['completed', 'cancelled'])
        ])

    def test_no_open_placements_when_original_bed_is_available(self):
        """
        If the bed the patient was in before is still
        available, then the new, scheduled placement should
        be cancelled leaving no open placements.
        """
        self.call_test()
        placements = self.get_open_placements()
        self.assertEqual(0, len(placements))

    def test_new_placement_scheduled_when_original_bed_is_not_available(self):
        """
        If the bed the patient was in before is no longer available then a new
        placement should be created for their original ward.
        The first 2 placements should be closed.
        """
        self.call_test(original_bed_available=False)
        placement = self.get_open_placements()
        self.assertEqual(1, len(placement))
        self.assertEqual('scheduled', placement.state)
        self.assertNotEqual(placement.id, self.placement_ward_a.id)
        self.assertNotEqual(placement.id, self.placement_ward_b.id)

    def test_open_placement_is_for_original_ward(self):
        """
        When the patient's original bed is no longer available a new placement
        is scheduled, that placement should be for the original ward.
        """
        self.call_test(original_bed_available=False)
        placement = self.get_open_placements()
        expected = self.test_utils.ward.id
        actual = placement.suggested_location_id.id
        self.assertEqual(expected, actual)
