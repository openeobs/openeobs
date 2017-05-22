from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class TestGetReviewDataObsStop(TransactionCase):
    """
    Test functionality of getting review data for the period up to the
    review trigger time
    """

    def setUp(self):
        super(TestGetReviewDataObsStop, self).setUp()
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
        self.wardboard_model = self.env['nh.clinical.wardboard']
        pme_reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']

        self.obs_stop_reasons = pme_reason_model.search([])

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
        super(TestGetReviewDataObsStop, self).tearDown()

    def test_cancelled_task_stop_obs(self):
        """
        Test that if review was cancelled by a Stop Obs PME that it shows
        that as the cancel reason
        """
        self.review_model.with_context(
            {'review_date': '1988-01-12 15:00:00'}
        ).schedule_review(self.spell_activity)
        wardboard = self.wardboard_model.browse(self.spell_activity.id)
        wardboard.start_obs_stop(
            self.obs_stop_reasons[0],
            self.spell_activity.data_ref.id,
            self.spell_activity.id
        )
        review_data = self.review_model.get_review_data(
            self.spell_activity.patient_id.id,
            '1988-01-12 07:00:00', 15
        )
        self.assertEqual(review_data, {
            'score': 3,
            'user': 'Stop Obs - {}'.format(
                self.obs_stop_reasons[0].display_name),
            'state': 'Not Completed'
        })
