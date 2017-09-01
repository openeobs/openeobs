# -*- coding: utf-8 -*-
from openerp import models


class NhClinicalTestUtils(models.AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    def create_and_complete_food_and_fluid_obs_activity(
            self, fluid_taken=None, fluid_output=None,
            completion_datetime=None, patient_id=None):
        activity_model = self.env['nh.activity']
        obs_food_and_fluid_activity_id = \
            self.create_food_and_fluid_obs_activity(fluid_taken, fluid_output,
                                                    patient_id)
        activity = activity_model.browse(obs_food_and_fluid_activity_id)
        activity.submit({})
        activity.complete()
        if completion_datetime:
            activity.date_terminated = completion_datetime
        return obs_food_and_fluid_activity_id

    def create_food_and_fluid_obs_activity(self, fluid_taken=None,
                                           fluid_output=None, patient_id=None):
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
        if fluid_output:
            obs_data['fluid_output'] = fluid_output

        food_and_fluid_model = \
            self.env['nh.clinical.patient.observation.food_fluid']
        obs_food_and_fluid_activity_id = food_and_fluid_model.create_activity(
            activity_vals={}, data_vals=obs_data
        )
        return obs_food_and_fluid_activity_id

    def create_f_and_f_review_activity(self, spell_activity=None):
        food_and_fluid_review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        activity_model = self.env['nh.activity']

        if not spell_activity:
            spell_activity = self.spell_activity

        f_and_f_review_activity_id = \
            food_and_fluid_review_model.schedule_review(spell_activity)
        f_and_f_review_activity = activity_model.browse(
            f_and_f_review_activity_id)

        return f_and_f_review_activity
