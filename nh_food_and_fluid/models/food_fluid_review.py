from openerp import models, api
from openerp.osv import fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class FoodAndFluidReview(models.Model):
    """
    Food and Fluid Review task
    """

    _name = 'nh.clinical.notification.food_fluid_review'
    _inherit = 'nh.clinical.notification'

    _description = 'F&F - {} Fluid Intake Review'

    trigger_times = [15, 6]

    @staticmethod
    def get_current_time(as_string=False):
        """
        Get the current time. Making this a separate function makes it easier
        to patch
        :param as_string: Should return datetime as string
        :return: datetime or string representation of datetime
        """
        current_datetime = datetime.now()
        if as_string:
            return datetime.strftime(current_datetime, DTF)
        return current_datetime

    @api.model
    def get_localised_time(self):
        """
        Get the localised time for datetime.now()
        """
        current_time = self.get_current_time()
        return fields.datetime.context_timestamp(
            self._cr, self._uid, current_time)

    @api.model
    def should_trigger_review(self):
        """
        Take the current localised time for the user and figure out if the
        review task should be triggered
        :return: True if correct localised time
        :rtype: bool
        """
        localised_time = self.get_localised_time()
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
        localised_time = self.get_localised_time()
        return self._description.format(
            datetime.strftime(localised_time, '%-I%p').lower())

    @api.model
    def active_food_fluid_period(self, spell_activity_id):
        """
        Check to see if any food and fluid observations have been submitted in
        this period
        :param spell_activity_id: ID of patient's spell activity
        :return: True if food and fluid observation have been submitted in the
        current period
        :rtype: bool
        """
        current_time = self.get_current_time(as_string=True)
        food_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        obs_for_period = food_fluid_model.get_obs_activities_for_period(
            spell_activity_id, current_time)
        return any(obs_for_period)

    @api.model
    def trigger_review_tasks_for_active_periods(self):
        """
        Method to trigger F&F review tasks for any active periods in the system
        Called by Scheduled Action every hour
        """
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
                if self.active_food_fluid_period(spell_activity.id):
                    self.schedule_review(spell_activity)

    def schedule_review(self, spell_activity):
        """
        Create the activity for the Food and Fluid Review Task
        :param spell_activity: Activity for patient's spell
        :return: activity ID
        """
        return self.create_activity({
            'parent_id': spell_activity.id,
            'spell_activity_id': spell_activity.id,
            'patient_id': spell_activity.patient_id.id,
            'summary': self.get_review_task_summary(),
            'location_id': spell_activity.location_id.id,
            'date_scheduled': self.get_current_time(as_string=True)
        }, {})
