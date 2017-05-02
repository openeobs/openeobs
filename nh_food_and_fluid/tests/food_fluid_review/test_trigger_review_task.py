from openerp.tests.common import TransactionCase
from datetime import datetime


class TestTriggerReviewTask(TransactionCase):
    """
    Test that the trigger review task method is only called when it's the
    correct time and the patient has an active F&F period
    """

    def setUp(self):
        super(TestTriggerReviewTask, self).setUp()
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)
        self.test_utils_model.copy_instance_variable_if_exists(self, 'nurse')
        self.nurse.write({'tz': 'Etc/UTC'})

        def patch_active_food_fluid_period(*args, **kwargs):
            obj = args[0]
            return obj._context.get('active_period', False)

        def patch_should_trigger_review(*args, **kwargs):
            obj = args[0]
            return obj._context.get('correct_time', False)

        def patch_get_current_time(*args, **kwargs):
            obj = args[0]
            hours = obj._context.get('hours', 15)
            now_time = datetime.now()
            current_time = now_time.replace(hour=hours)
            return current_time

        self.review_model._patch_method(
            'active_food_fluid_period', patch_active_food_fluid_period)
        self.review_model._patch_method(
            'should_trigger_review', patch_should_trigger_review)
        self.review_model._patch_method(
            'get_current_time', patch_get_current_time
        )

    def tearDown(self):
        self.review_model._revert_method('active_food_fluid_period')
        self.review_model._revert_method('should_trigger_review')
        self.review_model._revert_method('get_current_time')
        super(TestTriggerReviewTask, self).tearDown()

    def get_open_reviews(self):
        """
        Get the currently open reviews for the spell
        :return: list o' review objects
        """
        activity_model = self.env['nh.activity']
        return activity_model.search(
            [
                ['data_model', '=',
                 'nh.clinical.notification.food_fluid_review'],
                ['state', 'not in', ['completed', 'cancelled']],
                ['parent_id', '=', self.spell_activity.id]
            ]
        )

    def get_number_of_open_reviews(self):
        """
        Get a count of the currently open F&F review tasks
        :return: count of currently open F&F review tasks
        """
        reviews = self.get_open_reviews()
        return len(reviews.ids)

    def test_not_active_correct_time(self):
        """
        Test that task is not created when F&F period is not active but
        is the correct time
        """
        initial_count = self.get_number_of_open_reviews()
        ctx = self.env.context.copy()
        ctx.update({'correct_time': True})
        self.review_model.sudo(self.nurse).with_context(ctx)\
            .trigger_review_tasks_for_active_periods()
        self.assertEqual(initial_count, self.get_number_of_open_reviews())

    def test_active_correct_time(self):
        """
        Test that task is created when F&F period is active and is the correct
        time
        """
        initial_count = self.get_number_of_open_reviews()
        ctx = self.env.context.copy()
        ctx.update({'correct_time': True, 'active_period': True})
        self.review_model.sudo(self.nurse).with_context(ctx) \
            .trigger_review_tasks_for_active_periods()
        self.assertEqual(
            (initial_count + 1), self.get_number_of_open_reviews())

    def test_not_active_incorrect_time(self):
        """
        Test that task is not created when F&F is not active and is not the
        correct time
        """
        initial_count = self.get_number_of_open_reviews()
        self.review_model.sudo(self.nurse) \
            .trigger_review_tasks_for_active_periods()
        self.assertEqual(initial_count, self.get_number_of_open_reviews())

    def test_active_incorrect_time(self):
        """
        Test that task is not created when F&F is active but is not the correct
        time
        """
        initial_count = self.get_number_of_open_reviews()
        ctx = self.env.context.copy()
        ctx.update({'active_period': True})
        self.review_model.sudo(self.nurse).with_context(ctx) \
            .trigger_review_tasks_for_active_periods()
        self.assertEqual(initial_count, self.get_number_of_open_reviews())

    def test_3pm_task_name(self):
        """
        Test that the 3pm task name is 'F&F - 3pm Fluid Intake Review'
        """
        ctx = self.env.context.copy()
        ctx.update(
            {
                'correct_time': True,
                'active_period': True,
                'hours': 15
            }
        )
        self.review_model.sudo(self.nurse).with_context(ctx) \
            .trigger_review_tasks_for_active_periods()
        review = self.get_open_reviews()[:1]
        self.assertEqual(review.summary, 'F&F - 3pm Fluid Intake Review')

    def test_6am_task_name(self):
        """
        Test that the 6am task name is 'F&F - 6am Fluid Intake Review'
        """
        ctx = self.env.context.copy()
        ctx.update(
            {
                'correct_time': True,
                'active_period': True,
                'hours': 6
            }
        )
        self.review_model.sudo(self.nurse).with_context(ctx) \
            .trigger_review_tasks_for_active_periods()
        review = self.get_open_reviews()[:1]
        self.assertEqual(review.summary, 'F&F - 6am Fluid Intake Review')
