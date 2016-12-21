# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    def get_open_obs(self, patient_id=None, data_model=None, user_id=None):
        api_model = self.pool['nh.eobs.api']
        activity_model = self.env['nh.activity']

        if not patient_id:
            patient_id = self.patient_id
        if not data_model:
            data_model = 'nh.clinical.patient.observation.ews'
        if not user_id:
            user_id = self.nurse.id

        ews_activity_search = activity_model.search(
            [
                ['data_model', '=', data_model],
                ['patient_id', '=', patient_id],
                ['state', '=', 'scheduled']
            ]
        )
        if ews_activity_search:
            self.ews_activity = ews_activity_search[0]
        else:
            raise ValueError('Could not find EWS Activity ID')

        api_model.assign(
            self.env.cr,
            user_id,
            self.ews_activity.id,
            {'user_id': user_id}
        )

    def complete_obs(self, obs_data, obs_id=None, user_id=None):
        api_pool = self.pool['nh.eobs.api']
        if not obs_id:
            obs_id = self.ews_activity.id
        if not user_id:
            user_id = self.nurse.id

        api_pool.complete(
            self.env.cr,
            user_id,
            obs_id,
            obs_data
        )

    # Utility methods
    def create_ews_obs_activity(self, patient_id, spell_id, obs_data):
        ews_model = self.env['nh.clinical.patient.observation.ews']
        activity_pool = self.pool['nh.activity']
        activity_model = self.env['nh.activity']

        obs_activity_id = ews_model.create_activity(
            {'date_scheduled': datetime.now(),
             'parent_id': spell_id},
            {'patient_id': patient_id}
        )
        activity_pool.submit(self.env.cr, self.env.uid,
                             obs_activity_id, obs_data)
        activity_pool.complete(self.env.cr, self.env.uid, obs_activity_id)
        return activity_model.browse(obs_activity_id)

    def refuse_open_obs(self, patient_id, spell_activity_id):
        activity_model = self.env['nh.activity']
        activity_pool = self.pool['nh.activity']
        ews_model = self.env['nh.clinical.patient.observation.ews']

        obs_activity_current = \
            ews_model.get_open_obs_activity(spell_activity_id)
        # If no existing obs then create one.
        if len(obs_activity_current) < 1:
            obs_activity_current_activity_id = ews_model.create_activity(
                {
                    'date_scheduled': datetime.now(),
                    'parent_id': spell_activity_id,
                    'creator_id': obs_activity_current.id
                },
                {'patient_id': patient_id}
            )
            obs_activity_current = \
                activity_model.browse(obs_activity_current_activity_id)

        activity_pool.submit(
            self.env.cr, self.env.uid,
            obs_activity_current.id,
            {
                'is_partial': True,
                'partial_reason': 'refused'
            }
        )
        activity_pool.complete(
            self.env.cr, self.env.uid, obs_activity_current.id
        )
        return ews_model.get_open_obs_activity(spell_activity_id)
