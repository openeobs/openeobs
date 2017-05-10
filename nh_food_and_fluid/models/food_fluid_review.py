import logging
from datetime import datetime

from openerp import models, api


_logger = logging.getLogger(__name__)


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

    def manage_review_tasks_for_active_periods(self):
        cancel_reason = self._get_cancel_reason()
        if cancel_reason:
            self.cancel_review_tasks(cancel_reason)

        self.trigger_review_tasks_for_active_periods()

    def _get_cancel_reason(self):
        """
        Attempt to get the appropriate reason for cancelling a food and fluid
        review task based on the current localised time.

        If the current localised time is not a valid time to be cancelling
        food and fluid review tasks (there should be set times this occurs
        based on the client's policy) then `None` is returned.
        :return:
        """
        datetime_utils = self.env['datetime_utils']
        now = datetime_utils.get_localised_time()

        if now.hour == 6:
            return self.env['ir.model.data'].get_object(
                'nh_food_and_fluid', 'cancel_reason_6am_review')
        elif now.hour == 14:
            return self.env['ir.model.data'].get_object(
                'nh_food_and_fluid', 'cancel_reason_not_performed')

        return None

    def cancel_review_tasks(self, cancel_reason, spell_activity_id=None):
        """
        Cancel all open review tasks activities with the passed cancel reason
        for either one spell or all spells.
        :param spell_activity_id:
        :type spell_activity_id: int
        :param cancel_reason:
        """
        open_activities = self.get_open_activities(
            spell_activity_id=spell_activity_id)
        if spell_activity_id and len(open_activities) > 1:
            _logger.error("There should not be more than one food and fluid "
                          "review task open at any one time. Cancelling all "
                          "such tasks for the spell anyway to reduce manual "
                          "cleanup but this needs to be fixed.")
        for activity in open_activities:
            activity.cancel_with_reason(activity.id, cancel_reason.id)

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
