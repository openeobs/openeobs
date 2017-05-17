from openerp.tests.common import TransactionCase
from datetime import datetime


class TestGetOpenReviewsForPatient(TransactionCase):
    """
    Test that functionality to get open review for patient returns the
    open review task
    """

    def setUp(self):
        super(TestGetOpenReviewsForPatient, self).setUp()
        self.test_util_model = self.env['nh.clinical.test_utils']
        self.dateutils_model = self.env['datetime_utils']
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

        self.dateutils_model._patch_method(
            'get_current_time', patch_get_current_time)

        def patch_get_localised_time(*args, **kwargs):
            return datetime(1988, 1, 12, 15, 0, 0)

        self.dateutils_model._patch_method(
            'get_localised_time', patch_get_localised_time
        )

    def tearDown(self):
        self.dateutils_model._revert_method('get_current_time')
        self.dateutils_model._revert_method('get_localised_time')
        super(TestGetOpenReviewsForPatient, self).tearDown()

    def test_returns_open_review(self):
        """
        Test that if there is an open review for the patient it's returned
        by get_open_review_for_patient
        """
        self.review_model.schedule_review(self.spell_activity)
        open_reviews = self.review_model.get_open_reviews_for_patient(
            self.spell_activity.patient_id.id
        )
        self.assertEqual(len(open_reviews), 1)

    def test_returns_empty_recordset_no_review(self):
        """
        Test that if there's no open review for the patient it returns an
        empty recordset
        """
        open_reviews = self.review_model.get_open_reviews_for_patient(
            self.spell_activity.patient_id.id
        )
        self.assertEqual(len(open_reviews), 0)
