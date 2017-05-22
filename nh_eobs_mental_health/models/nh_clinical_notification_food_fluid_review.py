import logging
from openerp import models

_logger = logging.getLogger(__name__)


class FoodAndFluidReviewMentalHealth(models.Model):
    """
    Food and Fluid Review task
    """
    _name = 'nh.clinical.notification.food_fluid_review'
    _inherit = 'nh.clinical.notification.food_fluid_review'

    def get_spells_to_create_reviews_for(self):
        """
        Get a list of spell activities to create Food and Fluid Reviews for
        """
        spell_activities = super(FoodAndFluidReviewMentalHealth, self)\
            .get_spells_to_create_reviews_for()
        return [spell_activity for spell_activity in spell_activities
                if not spell_activity.data_ref.obs_stop]
