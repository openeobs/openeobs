# -*- coding: utf-8 -*-
from openerp import models


class NhClinicalTestUtils(models.AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    def create_and_complete_food_and_fluid_obs_activity(
            self, fluid_taken=None, completion_datetime=None, patient_id=None
    ):
        activity_model = self.env['nh.activity']
        obs_food_and_fluid_activity_id = \
            self.create_food_and_fluid_obs_activity(fluid_taken, patient_id)

        activity_model.submit(obs_food_and_fluid_activity_id, {})
        activity_model.complete(obs_food_and_fluid_activity_id)

        activity_obs = activity_model.browse(obs_food_and_fluid_activity_id)
        if completion_datetime:
            activity_obs.date_terminated = completion_datetime
        return obs_food_and_fluid_activity_id

    def create_food_and_fluid_obs_activity(self, fluid_taken=None,
                                           patient_id=None):
        if not patient_id and not hasattr(self, 'patient'):
            raise ValueError("No patient ID available for obs creation.")
        if not patient_id:
            patient_id = self.patient.id

        food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        obs_data = {
            'patient_id': patient_id,
            'passed_urine':
                food_and_fluid_model._passed_urine_options[0][0],
            'bowels_open':
                food_and_fluid_model._bowels_open_options[0][0]
        }
        if fluid_taken:
            obs_data['fluid_taken'] = fluid_taken

        food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        obs_food_and_fluid_activity_id = food_and_fluid_model.create_activity(
            activity_vals={}, data_vals=obs_data
        )
        return obs_food_and_fluid_activity_id
