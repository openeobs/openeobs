from datetime import datetime
from openerp.tests.common import TransactionCase


class TestGetViewDescription(TransactionCase):
    """
    Test that the get_view_description override is returning the call to the
    review task template
    """

    def setUp(self):
        super(TestGetViewDescription, self).setUp()
        test_utils_model = self.env['nh.clinical.test_utils']
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        activity_model = self.env['nh.activity']
        self.dateutils_model = self.env['datetime_utils']
        test_utils_model.admit_and_place_patient()
        test_utils_model.create_and_complete_food_and_fluid_obs_activity(
            100, 0, '1988-01-12 12:00:00')

        def patch_get_current_time(*args, **kwargs):
            if kwargs.get('as_string'):
                return '1988-01-12 15:00:00'
            else:
                return datetime(1988, 1, 12, 15, 0, 0)

        def patch_get_review_task_summary(*args, **kwargs):
            return 'F&F Test'

        self.dateutils_model._patch_method(
            'get_current_time', patch_get_current_time
        )

        self.review_model._patch_method(
            'get_review_task_summary', patch_get_review_task_summary
        )

        review_act_id = \
            self.review_model.schedule_review(test_utils_model.spell_activity)
        self.input_fixture = [
            {'name': 'test_input_1'},
            {'name': 'test_input_2'}
        ]
        review_activity = activity_model.browse(review_act_id)
        self.view_desc = \
            review_activity.data_ref.get_view_description(self.input_fixture)
        self.view_data = self.view_desc[0].get('view_data')

    def tearDown(self):
        self.dateutils_model._revert_method('get_current_time')
        self.review_model._revert_method('get_review_task_summary')
        super(TestGetViewDescription, self).tearDown()

    def test_has_one_entry(self):
        """
        Test that the returned view_description has one entry
        """
        self.assertEqual(1, len(self.view_desc))

    def test_changes_form_desc_to_template(self):
        """
        Test that the view_description is prepending the template call
        """
        self.assertEqual(self.view_desc[0].get('type'), 'template')
        self.assertEqual(
            self.view_desc[0].get('template'), 'nh_food_and_fluid.review_task')

    def test_view_data_period_start(self):
        """
        Test that period start is 7am 12/01
        """
        self.assertEqual(
            self.view_data.get('period_start'), '7am 12/01')

    def test_view_data_period_end(self):
        """
        Test that period end is 7am 13/01
        """
        self.assertEqual(
            self.view_data.get('period_end'), '7am 13/01')

    def test_view_data_title(self):
        """
        Test that title is task summary - F&F Test
        """
        self.assertEqual(
            self.view_data.get('title'), '<strong>F&F Test</strong>')

    def test_view_data_score(self):
        """
        Test that score is 3
        """
        self.assertEqual(self.view_data.get('period_score'), 3)

    def test_view_data_fluid_intake(self):
        """
        Test that fluid intake is 100ml
        """
        self.assertEqual(self.view_data.get('period_fluid_intake'), '100ml')

    def test_view_data_fluid_balance(self):
        """
        Test that fluid balance is 100ml
        """
        self.assertEqual(self.view_data.get('period_fluid_balance'), '100ml')

    def test_view_data_escalation_tasks(self):
        """
        Test that escalation tasks is correct for score of 3
        """
        self.assertEqual(
            self.view_data.get('period_escalation_tasks'),
            ['Inform medical staff immediately']
        )
