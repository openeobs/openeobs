# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestFoodFluidIds(TransactionCase):
    """Test `food_fluid_ids` field on `nh.clinical.wardboard`."""
    def setUp(self):
        super(TestFoodFluidIds, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.food_fluid_obs_1 = \
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                fluid_taken=1000,
                patient_id=self.patient.id,
            )
        self.food_fluid_obs_2 = \
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                fluid_taken=1337,
                patient_id=self.patient.id,
            )
        self.food_fluid_obs_3 = \
            self.test_utils.create_and_complete_food_and_fluid_obs_activity(
                fluid_taken=666,
                patient_id=self.patient.id,
            )

    def test_food_fluid_ids(self):
        """
        Test `food_fluid_ids` field is correctly populated.
        """
        wardboard = self.wardboard_model.get_by_spell_activity_id(
            self.spell_activity.id
        )
        food_fluid_ids = [
            food_fluid.activity_id.id for
            food_fluid in wardboard.food_fluid_ids]
        food_fluid_ids.reverse()
        self.assertEqual(
            [
                self.food_fluid_obs_1,
                self.food_fluid_obs_2,
                self.food_fluid_obs_3
            ],
            food_fluid_ids
        )
