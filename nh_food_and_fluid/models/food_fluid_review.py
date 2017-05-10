from openerp import models, api
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class FoodAndFluidReview(models.Model):
    """
    Food and Fluid Review task
    """

    _name = 'nh.clinical.notification.food_fluid_review'
    _inherit = 'nh.clinical.notification'

    _description = 'F&F - {} Fluid Intake Review'

    trigger_times = [15, 6]

    @api.model
    def should_trigger_review(self):
        """
        Take the current localised time for the user and figure out if the
        review task should be triggered
        :return: True if correct localised time
        :rtype: bool
        """
        dateutils_model = self.env['datetime_utils']
        localised_time = dateutils_model.get_localised_time()
        if localised_time.hour in self.trigger_times:
            return True
        return False

    @api.model
    def get_review_task_summary(self):
        """
        Get the summary for the review task
        :return: string for summary
        :rtype: str
        """
        dateutils_model = self.env['datetime_utils']
        localised_time = dateutils_model.get_localised_time()
        return self._description.format(
            datetime.strftime(localised_time, '%-I%p').lower())

    @api.model
    def trigger_review_tasks_for_active_periods(self):
        """
        Method to trigger F&F review tasks for any active periods in the system
        Called by Scheduled Action every hour
        """
        food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        is_time_to_trigger_review = self.should_trigger_review()
        if is_time_to_trigger_review:
            activity_model = self.env['nh.activity']
            spell_activities = activity_model.search(
                [
                    ['data_model', '=', 'nh.clinical.spell'],
                    ['state', 'not in', ['completed', 'cancelled']]
                ]
            )
            for spell_activity in spell_activities:
                if food_fluid_model.active_food_fluid_period(
                        spell_activity.id):
                    self.schedule_review(spell_activity)

    def schedule_review(self, spell_activity):
        """
        Create the activity for the Food and Fluid Review Task
        :param spell_activity: Activity for patient's spell
        :return: activity ID
        """
        dateutils_model = self.env['datetime_utils']
        return self.create_activity(
            {
                'parent_id': spell_activity.id,
                'spell_activity_id': spell_activity.id,
                'patient_id': spell_activity.patient_id.id,
                'summary': self.get_review_task_summary(),
                'location_id': spell_activity.location_id.id,
                'date_scheduled': dateutils_model.get_current_time(
                    as_string=True)
            },
            {
                'patient_id': spell_activity.patient_id.id
            }
        )

    @api.model
    def add_reviews_to_periods(self, patient_id, periods):
        """
        Add review task data to the periods dictionaries passed from
        get_periods_dictionaries on the F&F model
        :param patient_id: ID for the patient we're looking up reviews for
        :type patient_id: int
        :param periods: list of periods
        :type periods: list of dicts
        :return: list of periods with review data added
        """
        for period in periods:
            period['reviews'] = {}
            for review_time in self.trigger_times:
                period['reviews'][review_time] = self.get_review_data(
                    patient_id, period.get('period_start_datetime'),
                    review_time)
        return periods

    @api.model
    def get_review_data(self, patient_id, period_start, trigger_time):
        """
        Get data for the review in a given period for a given patient
        :param patient_id: Id of the patient we're looking up review for
        :type patient_id: int
        :param period_start: start of the period
        :type period_start: Odoo datetime string
        :param trigger_time: time the review was triggered (hour of day)
        :type trigger_time: int
        :return: dictionary of review score, state and user/reason
        """
        period_start_datetime = datetime.strptime(period_start, dtf)
        period_end_datetime = period_start_datetime.replace(hour=trigger_time)
        if trigger_time < 7:
            day_delta = timedelta(days=1)
            period_end_datetime = period_end_datetime + day_delta
        period_end = period_end_datetime.strftime(dtf)
        activity_domain = [
            ['patient_id', '=', patient_id],
            ['date_scheduled', '=', period_end]
        ]
        activity_model = self.env['nh.activity']
        review_activity = activity_model.search(activity_domain)
        if not review_activity:
            return None
        food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        obs_domain = [
            ['data_model', '=', 'nh.clinical.patient.observation.food_fluid'],
            ['patient_id', '=', patient_id],
            ['date_terminated', '>=', period_start],
            ['date_terminated', '<=', period_end]
        ]
        obs = activity_model.search(obs_domain)
        fluid_intake = food_fluid_model.\
            _calculate_total_fluid_intake_from_obs_activities(obs)
        score = food_fluid_model.calculate_period_score(fluid_intake)
        user_or_reason = review_activity.terminate_uid.name
        if review_activity.state is 'cancelled':
            user_or_reason = review_activity.cancel_reason_id.name
        return {
            'score': score,
            'state': review_activity.state,
            'user': user_or_reason
        }
