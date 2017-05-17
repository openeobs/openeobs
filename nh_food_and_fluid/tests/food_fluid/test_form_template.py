from openerp.tests.common import TransactionCase


class TestFormTemplate(TransactionCase):
    """
    Test that the form template is rendered with and without the review
    task if there is an open review task for the patient
    """

    def setUp(self):
        super(TestFormTemplate, self).setUp()
        self.food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.activity_model = self.env['nh.activity']
        # patch get_open_reviews_for_patient to change if included or not

        def patch_get_open_reviews_for_patient(*args, **kwargs):
            obj = args[0]
            if obj._context.get('review_open'):
                return self.activity_model.new({
                    'data_model': 'nh.clinical.notification.food_fluid_review'
                })

    def test_review_task_present_when_task_open(self):
        """
        Test that the review task is included in the template if there is a
        currently open review task for the patient
        """
        self.assertTrue(False)

    def test_review_task_not_present_when_closed(self):
        """
        Test that the review task is not included in the template if there
        is no currently open review task for the patient
        """
        self.assertTrue(False)
