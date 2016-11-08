# -*- coding: utf-8 -*-
from datetime import datetime

from openerp.models import AbstractModel


class ObservationTestUtils(AbstractModel):

    _name = 'observation_test_utils'

    def refuse_open_obs(self, patient_id, spell_id):
        activity_model = self.env['nh.activity']
        activity_pool = self.pool['nh.activity']
        ews_model = self.env['nh.clinical.patient.observation.ews']

        obs_activity_current = \
            ews_model.get_open_obs_activity(spell_id)
        # If no existing obs then create one.
        if len(obs_activity_current) < 1:
            obs_activity_current_activity_id = ews_model.create_activity(
                {'date_scheduled': datetime.now(),
                 'parent_id': spell_id},
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
        activity_pool.complete(self.env.cr, self.env.uid,
                                    obs_activity_current.id)
        return ews_model.get_open_obs_activity(spell_id)

    def create_obs(self, patient_id, spell_id, obs_data):
        ews_model = self.env['nh.clinical.patient.observation.ews']
        activity_pool = self.pool['nh.activity']
        activity_model = self.env['nh.activity']

        obs_activity_id = ews_model.create_activity(
            {'date_scheduled': datetime.now(),
             'parent_id': spell_id},
            {'patient_id': patient_id}
        )
        activity_pool.submit(self.env.cr, self.env.uid,
                                  obs_activity_id,
                                  obs_data)
        activity_pool.complete(self.env.cr, self.env.uid,
                                    obs_activity_id)
        return activity_model.browse(obs_activity_id)
