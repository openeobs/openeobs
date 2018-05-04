"""
Tests the method that provides the value for the computed field
`last_movement_datetime`. The field is used on the patient form to populate the
'Transfer In' value which is intended to indicate the datetime when the patient
was transferred into the current ward.
"""
from unittest import skip

from openerp.tests.common import SavepointCase


def _get_actual_last_movement_datetime(self):
    wardboard = self.wardboard_model.browse(self.spell.id)
    return wardboard.last_movement_datetime


class TestMovementsThatTakeTheCurrentServerTime(SavepointCase):
    """
    Tests actions that create movement records that do not have their move
    datetime explicitly set and instead default to the current server time.
    """
    def setUp(self):
        super(TestMovementsThatTakeTheCurrentServerTime, self).setUp()

        self.expected_last_movement_datetime = '2017-06-06 12:00:00'

        def _stub_get_current_time(*args, **kwargs):
            return self.expected_last_movement_datetime

        self.datetime_utils_model = self.env['datetime_utils']
        self.datetime_utils_model._patch_method(
            'get_current_time', _stub_get_current_time
        )

        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.wardboard_model = self.env['nh.clinical.wardboard']

    def tearDown(self):
        super(TestMovementsThatTakeTheCurrentServerTime, self).tearDown()
        self.datetime_utils_model._revert_method('get_current_time')

    def call_test(self):
        actual_last_movement_datetime = \
            _get_actual_last_movement_datetime(self)
        self.assertEqual(
            self.expected_last_movement_datetime, actual_last_movement_datetime
        )

    def test_patient_placed(self):
        self.call_test()

    def test_patient_transferred(self):
        self.test_utils_model.transfer_patient()
        self.call_test()

    def test_transfer_cancelled(self):
        self.test_utils_model.transfer_patient()
        self.test_utils_model.cancel_patient_transfer()
        self.call_test()

    def test_patient_discharged(self):
        self.test_utils_model.discharge_patient()
        self.call_test()

    def test_discharge_cancelled(self):
        self.test_utils_model.discharge_patient()
        self.test_utils_model.cancel_patient_discharge()
        self.call_test()


class TestMovementsWithMoveDatetimesExplicitlySet(SavepointCase):
    """
    Tests actions with which it is possible to set the exact move datetime to
    be passed to the created move records.
    """
    def setUp(self):
        super(TestMovementsWithMoveDatetimesExplicitlySet, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.setup_ward()
        self.test_utils_model.create_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.wardboard_model = self.env['nh.clinical.wardboard']

    def call_test(self):
        actual_last_movement_datetime = \
            _get_actual_last_movement_datetime(self)
        self.assertEqual(
            self.expected_last_movement_datetime, actual_last_movement_datetime
        )

    def test_patient_admitted_in_the_past(self):
        self.expected_last_movement_datetime = '2017-06-06 12:00:00'
        self.spell = self.test_utils_model.admit_patient(
            start_date=self.expected_last_movement_datetime)
        self.call_test()

    def test_discharge_patient(self):
        self.expected_last_movement_datetime = '2017-06-06 12:00:00'
        self.spell = self.test_utils_model.admit_patient(
            start_date=self.expected_last_movement_datetime)

        self.expected_last_movement_datetime = '2017-06-07 12:00:00'
        self.test_utils_model.discharge_patient(
            discharge_datetime=self.expected_last_movement_datetime)

        self.call_test()

    @skip('Test fails until EOBS-2586 is fixed.')
    def test_discharge_cancelled(self):
        self.expected_last_movement_datetime = '2017-06-06 12:00:00'
        self.spell = self.test_utils_model.admit_patient(
            start_date=self.expected_last_movement_datetime)

        discharge_datetime = '2017-07-07 12:00:00'
        self.test_utils_model.discharge_patient(
            discharge_datetime=discharge_datetime)

        self.test_utils_model.cancel_patient_discharge()

        self.call_test()
