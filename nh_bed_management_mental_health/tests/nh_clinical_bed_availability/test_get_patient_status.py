# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.tests.common import TransactionCase


class TestPatientStatus(TransactionCase):

    def setUp(self):
        super(TestPatientStatus, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        self.bed = self.test_utils.bed
        self.other_bed = self.test_utils.other_bed
        self.ward = self.test_utils.ward

        self.bed_availability_model = self.env['nh.clinical.bed_availability']

        self.in_ward = 'In Ward'
        self.off_ward = 'Off Ward'

    def test_returns_in_ward_if_patient_allocated_to_bed(self):
        record = self.bed_availability_model.create({
            'location': self.bed.id
        })
        patient_status = record.patient_status
        self.assertEqual(self.in_ward, patient_status)

    def test_returns_off_ward_if_patient_current_location_different(self):
        """
        Patient is allocated to their bed but the current location is not the
        bed.
        """
        record = self.bed_availability_model.create({
            'location': self.bed.id
        })
        self.assertEqual(self.in_ward, record.patient_status)

        self.test_utils.start_pme()

        # Must manually recompute. Odoo does this for us when a view is
        # reloaded.
        self.env.add_todo(record._fields['patient_status'], record)
        record.recompute()

        patient_status = record.patient_status
        self.assertTrue(self.off_ward in patient_status)

    def test_pme_reason_included_when_patient_off_ward(self):
        """
        The patient status should contain a basic status followed by a hyphen
        and the reason for the patient being off ward.
        """
        datetime_utils = self.env['datetime_utils']

        def mock_get_current_time(*args, **kwargs):
            now = datetime(
                year=2017, month=04, day=27, hour=16)
            return now
        datetime_utils._patch_method('get_current_time', mock_get_current_time)

        try:
            record = self.bed_availability_model.create({
                'location': self.bed.id
            })
            self.assertEqual(self.in_ward, record.patient_status)

            pme_reason_model = \
                self.env['nh.clinical.patient_monitoring_exception.reason']
            expected_pme_reason = 'At Home'
            pme_reason = pme_reason_model.create({
                'display_text': expected_pme_reason
            })
            self.test_utils.start_pme(reason=pme_reason)

            obs_stop_model = self.env['nh.clinical.pme.obs_stop']
            obs_stop = obs_stop_model.get_latest_activity(
                self.spell_activity.id)
            obs_stop.date_started = '2017-04-27 10:15:00'

            # Must manually recompute. Odoo does this for us when a view is
            # reloaded.
            self.env.add_todo(record._fields['patient_status'], record)
            record.recompute()

            expected_time_elapsed = '5 Hours'
            expected = '{} - {} ({})'.format(
                self.off_ward, expected_pme_reason, expected_time_elapsed)
            actual = record.patient_status

            self.assertEqual(expected, actual)
        finally:
            datetime_utils._revert_method('get_current_time')

    def test_returns_false_if_no_patient_allocated_to_bed(self):
        move_model = self.env['nh.clinical.patient.move']
        move_activity_id = move_model.create_activity(
            {
                'spell_activity_id': self.spell_activity.id
            },
            {
                'patient_id': self.patient.id,
                'location_id': self.other_bed.id
            }
        )
        move_model.complete(move_activity_id)

        record = self.bed_availability_model.create({
            'location': self.bed.id
        })
        expected = False
        actual = record.patient_status
        self.assertEqual(expected, actual)
