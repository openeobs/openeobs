from openerp.tests.common import TransactionCase


class TestWeightSchedule(TransactionCase):
    """
    Test that .get_next_scheduled_time() method of the
    nh.clinical.observation.weight model
    """

    CALLED_GET_TIMES = False
    CALLED_GET_NEXT_TIME = False
    SCHEDULED_DATE = '1988-01-12 06:00:00'

    def setUp(self):
        """
        Set up the tests
        """
        super(TestWeightSchedule, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.weight_model = self.env['nh.clinical.patient.observation.weight']
        self.CALLED_GET_TIMES = False
        self.CALLED_GET_NEXT_TIME = False

        def patch_get_schedule_times(*args, **kwargs):
            self.CALLED_GET_TIMES = True
            return []

        def patch_get_next_scheduled_time(*args, **kwargs):
            self.CALLED_GET_NEXT_TIME = True
            return self.SCHEDULED_DATE

        self.weight_model._patch_method(
            'get_next_scheduled_time',
            patch_get_next_scheduled_time
        )

        self.weight_model._patch_method(
            'get_schedule_times_from_policy',
            patch_get_schedule_times
        )

        self.test_utils.create_patient_and_spell()
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

    def tearDown(self):
        """
        Clean up after tests
        """
        self.weight_model._revert_method('get_next_scheduled_time')
        self.weight_model._revert_method('get_schedule_times_from_policy')
        super(TestWeightSchedule, self).tearDown()

    def test_gets_scheduled_times(self):
        """
        Test that schedule() calls get_scheduled_times_from_policy() to get
        the times the observation should be scheduled at
        """
        self.weight_ob.schedule(self.weight_ob.activity_id.id)
        self.assertTrue(self.CALLED_GET_TIMES)

    def test_get_next_time(self):
        """
        Test that schedule() calls get_next_scheduled_time() to get the time
        the observation should be scheduled for
        """
        self.weight_ob.schedule(self.weight_ob.activity_id.id)
        self.assertTrue(self.CALLED_GET_NEXT_TIME)

    def test_no_date_scheduled(self):
        """
        Test that if no date_scheduled supplied it creates one using the policy
        """
        self.weight_ob.schedule(self.weight_ob.activity_id.id)
        self.assertEqual(
            self.weight_ob.activity_id.date_scheduled,
            self.SCHEDULED_DATE
        )

    def test_date_schedule_provided(self):
        """
        Test that when date_schedule is supplied that it uses that
        """
        schedule_date = '1990-04-13 06:00:00'
        self.weight_ob.schedule(self.weight_ob.activity_id.id, schedule_date)
        self.assertEqual(
            self.weight_ob.activity_id.date_scheduled,
            schedule_date
        )
