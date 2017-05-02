from openerp import models, api
from openerp.osv import fields
from datetime import datetime


class FoodAndFluidReview(models.Model):
    """
    Food and Fluid Review task
    """

    _name = 'nh.clinical.notification.food_fluid_review'
    _inherit = 'nh.clinical.notification'

    _description = 'F&F - {} Fluid Intake Review'

    trigger_times = [15, 6]

    def get_current_time(self):
        """
        Get the current time. Making this a separate function makes it easier
        to patch
        """
        return datetime.now()

    @api.model
    def should_trigger_review(self):
        """
        Take the current localised time for the user and figure out if the
        review task should be triggered
        :return: True if correct localised time
        :rtype: bool
        """
        current_time = self.get_current_time()
        localised_time = fields.datetime.context_timestamp(
            self._cr, self._uid, current_time)
        if localised_time.hour in self.trigger_times:
            return True
        return False
