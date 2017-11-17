from openerp.tests.common import TransactionCase
from datetime import datetime


class TestGetScheduleTimesFromPolicy(TransactionCase):
    """
    Test that .get_next_scheduled_time() method of the
    nh.clinical.observation.weight model
    """

    SCHEDULED_DATE = datetime(1988, 1, 12, 6, 0, 0)

    def setUp(self):
        """
        Set up the tests
        """
        super(TestGetScheduleTimesFromPolicy, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.weight_model = self.env['nh.clinical.patient.observation.weight']
        self.datetime_utils = self.env['datetime_utils']
        self.test_utils.create_patient_and_spell()

        def patch_get_current_time(*args, **kwargs):
            return self.SCHEDULED_DATE

        self.datetime_utils._patch_method(
            'get_current_time',
            patch_get_current_time
        )

        weight_act = self.weight_model.create_activity(
            {},
            {
                'patient_id': self.test_utils.patient.id
            }
        )
        self.weight_ob = self.weight_model.search(
            [
                ['activity_id', '=', weight_act]
            ]
        )
        self.weight_ob._POLICY = {
            'schedule': [[13, 37]]
        }

    def tearDown(self):
        """
        Clean up after tests
        """
        self.datetime_utils._revert_method('get_current_time')
        super(TestGetScheduleTimesFromPolicy, self).tearDown()

    def test_changes_hours(self):
        """
        Test that it changes the hours of the returned datetimes, based on
        the policy list
        """
        times = self.weight_ob.get_schedule_times_from_policy()
        self.assertEqual(times[0].hour, 13)

    def test_changes_minutes(self):
        """
        Test that it changes the minutes of the returned datetimes, based on
        the policy list
        """
        times = self.weight_ob.get_schedule_times_from_policy()
        self.assertEqual(times[0].minute, 37)

    def test_multiple_times(self):
        """
        Test that if the policy has multiple times then it returns multiple
        times
        """
        self.weight_ob._POLICY['schedule'].append([21, 12])
        times = self.weight_ob.get_schedule_times_from_policy()
        self.assertEqual(len(times), 2)
