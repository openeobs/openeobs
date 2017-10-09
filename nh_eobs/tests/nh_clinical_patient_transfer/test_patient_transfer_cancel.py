# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestPatientTransferCancel(TransactionCase):

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

    def call_test(self):
        self._transfer_patient()
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
        self._transfer_patient()

        # Put another patient in their original bed.
        self.test_utils.create_patient()
        self.test_utils.admit_patient()
        self.test_utils.create_placement()
        self.test_utils.place_patient(self.test_utils.bed.id)

        self._cancel_transfer()

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
        placement record. Unfortunately this cannot be easily tested as it
        uses SQL to get records and SQL statements do not seem to have access
        to the test cursor so the test data is not returned by those
        queries.

        Instead this is tested less directly by asserting that the parent
        location of the latest placement is the original ward and not the
        destination ward of the cancelled transfer.
        """
        # Get latest placement
        placement = self.placement_model.search([
            ('patient_id', '=', self.patient.id),
        ], order='id desc', limit=1)
        placement.ensure_one()

        expected = self.test_utils.ward.id
        actual = placement.location_id.parent_id.id
        self.assertEqual(expected, actual)
