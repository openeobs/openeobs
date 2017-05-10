from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class TestGetReviewData(TransactionCase):
    """
    Test functionality of getting review data for the period up to the
    review trigger time
    """

    def setUp(self):
        super(TestGetReviewData, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)
        vals = ['nurse', 'other_ward', 'hospital']
        for val in vals:
            self.test_utils.copy_instance_variable_if_exists(self, val)
        self.food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        self.review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        self.datetime_utils = self.env['datetime_utils']
        self.activity_model = self.env['nh.activity']
        self.api_model = self.env['nh.eobs.api']

        ff_times = ['08', '11', '14', '17', '20', '23']
        for ff_time in ff_times:
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                fluid_taken=200,
                completion_datetime='1988-01-12 {}:00:00'.format(ff_time)
            )

        def patch_get_current_time(*args, **kwargs):
            review_date = args[0]._context.get('review_date')
            return_string = kwargs.get('as_string')
            if review_date:
                if return_string:
                    return review_date
                return datetime.strptime(review_date, dtf)
            return patch_get_current_time.origin(*args, **kwargs)

        self.datetime_utils._patch_method(
            'get_current_time', patch_get_current_time)

    def tearDown(self):
        self.datetime_utils._revert_method('get_current_time')
        super(TestGetReviewData, self).tearDown()

    def test_normal_3pm(self):
        """
        Test that normal 3pm review has score of 3, user is nurse and state is
        completed
        """
        review_id = self.review_model.with_context(
            {'review_date': '1988-01-12 15:00:00'}
        ).schedule_review(self.spell_activity)
        self.activity_model.sudo(self.nurse).complete(review_id)
        review_data = self.review_model.get_review_data(
            self.spell_activity.patient_id.id,
            '1988-01-12 07:00:00', 15
        )
        self.assertEqual(review_data, {
            'score': 3,
            'user': self.nurse.name,
            'state': 'completed'
        })

    def test_normal_6am(self):
        """
        Test that normal 6am review has score of 1, user is nurse and state is
        completed
        """
        review_id = self.review_model.with_context(
            {'review_date': '1988-01-13 06:00:00'}
        ).schedule_review(self.spell_activity)
        self.activity_model.sudo(self.nurse).complete(review_id)
        review_data = self.review_model.get_review_data(
            self.spell_activity.patient_id.id,
            '1988-01-12 07:00:00', 6
        )
        self.assertEqual(review_data, {
            'score': 1,
            'user': self.nurse.name,
            'state': 'completed'
        })

    def test_normal_score_difference(self):
        """
        Test that the the 3pm score is greater or equal to the 6am score under
        normal circumstances
        """
        review_id = self.review_model.with_context(
            {'review_date': '1988-01-12 15:00:00'}
        ).schedule_review(self.spell_activity)
        self.activity_model.sudo(self.nurse).complete(review_id)
        review_id = self.review_model.with_context(
            {'review_date': '1988-01-13 06:00:00'}
        ).schedule_review(self.spell_activity)
        self.activity_model.sudo(self.nurse).complete(review_id)
        review_data_3pm = self.review_model.get_review_data(
            self.spell_activity.patient_id.id,
            '1988-01-12 07:00:00', 15
        )
        review_data_6am = self.review_model.get_review_data(
            self.spell_activity.patient_id.id,
            '1988-01-12 07:00:00', 6
        )
        self.assertGreaterEqual(
            review_data_3pm.get('score'), review_data_6am.get('score'))

    def test_missing_3pm_review(self):
        """
        Test that the 3pm review is missing if no review task was generated for
        3pm
        """
        review_data = self.review_model.get_review_data(
            self.spell_activity.patient_id.id,
            '1988-01-12 07:00:00', 15
        )
        self.assertIsNone(review_data)

    def test_missing_6am_review(self):
        """
        Test that the 6am review is missing if no review task was generated for
        6am
        """
        review_data = self.review_model.get_review_data(
            self.spell_activity.patient_id.id,
            '1988-01-12 07:00:00', 6
        )
        self.assertIsNone(review_data)

    # def test_cancelled_task_stop_obs(self):
    #     """
    #     Test that if review was cancelled by a Stop Obs PME that it shows
    #     that as the cancel reason
    #     """
    #     self.review_model.with_context(
    #         {'review_date': '1988-01-12 15:00:00'}
    #     ).schedule_review(self.spell_activity)
    #     wardboard = self.wardboard_model.browse(self.spell_activity.id)
    #     wardboard.start_obs_stop(
    #         self.pme_reason[0],
    #         self.spell_activity.data_ref.id,
    #         self.spell_activity.id
    #     )
    #     self.assertTrue(False)
    #
    # def test_cancelled_task_transfer(self):
    #     """
    #     Test that if review was cancelled by a transfer that it shows that
    #     as the cancel reason
    #     """
    #     self.review_model.with_context(
    #         {'review_date': '1988-01-12 15:00:00'}
    #     ).schedule_review(self.spell_activity)
    #     self.api_model.transfer(
    #         self.patient.other_identifier,
    #        {'location': self.other_ward.code})
    #     review_data = self.review_model.get_review_data(
    #         self.spell_activity.patient_id.id,
    #         '1988-01-12 07:00:00', 15
    #     )
    #     self.assertEqual(review_data, {
    #         'score': 3,
    #         'user': self.nurse.name,
    #         'state': 'cancelled'
    #     })
    #
    # def test_cancelled_task_discharge(self):
    #     """
    #     Test that is review was cancelled by a discharge that is shows that
    #     as the cancel reason
    #     """
    #     self.review_model.with_context(
    #         {'review_date': '1988-01-12 15:00:00'}
    #     ).schedule_review(self.spell_activity)
    #     self.api_model.discharge(
    #         self.patient.other_identifier, {'location': self.hospital.code})
    #     review_data = self.review_model.get_review_data(
    #         self.spell_activity.patient_id.id,
    #         '1988-01-12 07:00:00', 15
    #     )
    #     self.assertEqual(review_data, {
    #         'score': 3,
    #         'user': self.nurse.name,
    #         'state': 'completed'
    #     })
    #
    # def test_cancelled_by_6am_reason(self):
    #     """
    #     Test that a 3pm review which was cancelled by a 6am review task
    #     triggering shows that as the cancel reason
    #     """
    #     review_id = self.review_model.with_context(
    #         {'review_date': '1988-01-12 15:00:00'}
    #     ).schedule_review(self.spell_activity)
    #     self.activity_model.sudo(self.nurse).complete(review_id)
    #     review_id = self.review_model.with_context(
    #         {'review_date': '1988-01-13 06:00:00'}
    #     ).schedule_review(self.spell_activity)
    #     self.activity_model.sudo(self.nurse).complete(review_id)
    #     review_data = self.review_model.get_review_data(
    #         self.spell_activity.patient_id.id,
    #         '1988-01-12 07:00:00', 15
    #     )
    #     self.assertEqual(review_data, {
    #         'score': 3,
    #         'user': '6am Review',
    #         'state': 'cancelled'
    #     })
    #
    # def test_cancelled_by_2pm_reason(self):
    #     """
    #     Test that a 6am review which was cancelled by the task not being
    #     completed before 2pm in the next period shows 'Not performed' as the
    #     reason
    #     """
    #     review_id = self.review_model.with_context(
    #         {'review_date': '1988-01-12 15:00:00'}
    #     ).schedule_review(self.spell_activity)
    #     self.activity_model.sudo(self.nurse).complete(review_id)
    #     review_id = self.review_model.with_context(
    #         {'review_date': '1988-01-13 06:00:00'}
    #     ).schedule_review(self.spell_activity)
    #     self.activity_model.sudo(self.nurse).complete(review_id)
    #     review_data = self.review_model.get_review_data(
    #         self.spell_activity.patient_id.id,
    #         '1988-01-12 07:00:00', 6
    #     )
    #     self.assertEqual(review_data, {
    #         'score': 1,
    #         'user': 'Not Performed',
    #         'state': 'cancelled'
    #     })
