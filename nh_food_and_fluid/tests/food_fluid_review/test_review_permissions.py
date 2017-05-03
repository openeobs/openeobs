from openerp.tests.common import TransactionCase
from datetime import datetime


TEST_SUMMARY = 'F&F - 3pm Fluid Intake Review'


class TestReviewPermissions(TransactionCase):
    """
    Test that only HCA, Nurses and Doctors can see the triggered F&F Review
    tasks
    """

    def setUp(self):
        super(TestReviewPermissions, self).setUp()
        self.test_util_model = self.env['nh.clinical.test_utils']
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.eobs_api_model = self.env['nh.eobs.api']
        self.test_util_model.admit_and_place_patient()
        self.shift_coordinator = \
            self.test_util_model.create_shift_coordinator()
        self.test_util_model.create_senior_manager()
        items_needed = [
            'ward',
            'senior_manager',
            'hca',
            'nurse',
            'bed',
            'doctor',
            'spell_activity'
        ]
        for item in items_needed:
            self.test_util_model.copy_instance_variable_if_exists(self, item)

        def patch_get_current_time(*args, **kwargs):
            as_string = kwargs.get('as_string')
            if as_string:
                return '1988-01-12 15:00:00'
            else:
                return datetime(1988, 1, 12, 15, 0, 0)
        self.review_model._patch_method(
            'get_current_time', patch_get_current_time)

        self.review_model.schedule_review(self.spell_activity)

    def tearDown(self):
        self.review_model._revert_method('get_current_time')
        super(TestReviewPermissions, self).tearDown()

    def test_hca_sees_task(self):
        """
        Test that once a review is triggered that the HCA associated with
        patient can see it
        """
        tasks = self.eobs_api_model.sudo(self.hca).get_activities()
        task_names = [rec.get('summary') for rec in tasks]
        self.assertTrue(TEST_SUMMARY in task_names)

    def test_nurse_sees_task(self):
        """
        Test that once a review is triggered that the Nurse associated with
        patient can see it
        """
        tasks = self.eobs_api_model.sudo(self.nurse).get_activities()
        task_names = [rec.get('summary') for rec in tasks]
        self.assertTrue(TEST_SUMMARY in task_names)

    def test_doctor_sees_task(self):
        """
        Test that once a review is triggered that that Doctor associated with
        patient can see it
        """
        tasks = self.eobs_api_model.sudo(self.doctor).get_activities()
        task_names = [rec.get('summary') for rec in tasks]
        self.assertTrue(TEST_SUMMARY in task_names)

    def test_shift_coordinator_cant_see_task(self):
        """
        Test that once a review is triggered that the shift coordinator
        for ward patient is on cannot see it
        """
        tasks = \
            self.eobs_api_model.sudo(self.shift_coordinator).get_activities()
        task_names = [rec.get('summary') for rec in tasks]
        self.assertFalse(TEST_SUMMARY in task_names)

    def test_senior_manager_cant_see_task(self):
        """
        Test that once a review is triggered that the senior manager
        for ward patient is on cannot see it
        """
        tasks = self.eobs_api_model.sudo(self.senior_manager).get_activities()
        task_names = [rec.get('summary') for rec in tasks]
        self.assertFalse(TEST_SUMMARY in task_names)
