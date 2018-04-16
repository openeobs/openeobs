# -*- coding: utf-8 -*-
"""Encapsulates commonly used test methods."""
from datetime import datetime

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data
from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    # Utility methods
    def create_and_complete_ews_obs_activity(
            self, patient_id, spell_id, obs_data=None, risk='no'):
        """
        Creates an EWS observation with the given clinical risk, then completes
        it.

        :param patient_id:
        :type patient_id: int
        :param spell_id:
        :type spell_id: int
        :param obs_data:
        :type obs_data: dict
        :return:
        """
        if obs_data is None:
            obs_data = self._get_risk_data(risk)

        ews_model = self.env['nh.clinical.patient.observation.ews']
        activity_pool = self.pool['nh.activity']
        activity_model = self.env['nh.activity']

        obs_activity_id = ews_model.create_activity(
            {
                'date_scheduled': datetime.now(),
                'parent_id': spell_id
            },
            {
                'patient_id': patient_id
            }
        )
        activity_pool.submit(self.env.cr, self.env.uid,
                             obs_activity_id, obs_data)
        activity_pool.complete(self.env.cr, self.env.uid, obs_activity_id)
        return activity_model.browse(obs_activity_id)

    @staticmethod
    def _get_risk_data(risk):
        risk = risk.upper()
        variable_name = '{}_RISK_DATA'.format(risk)
        obs_data = getattr(clinical_risk_sample_data, variable_name)
        return obs_data

    def complete_obs(self, obs_data, obs_activity_id=None, user_id=None):
        activity_model = self.env['nh.activity']
        if user_id is None:
            user_id = self.env.uid
        if obs_activity_id is None:
            obs_activity_id = self.get_open_obs()

        obs_activity = activity_model.browse(obs_activity_id)
        obs_activity.submit(obs_data)
        return obs_activity.complete()

    def complete_open_obs_as_partial(self, patient_id, spell_activity_id,
                                     reason):
        """
        Get the currently open observation and partially complete it giving the
        passed partial reason. Return the newly created observation.

        :param patient_id:
        :type patient_id: int
        :param spell_activity_id:
        :type spell_activity_id: int
        :param reason:
        :type reason: str
        :return: Next observation created after the completed partial one.
        """
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
                'partial_reason': reason
            }
        )
        activity_pool.complete(
            self.env.cr, self.env.uid, obs_activity_current.id
        )
        return ews_model.get_open_obs_activity(spell_activity_id)

    def refuse_open_obs(self, patient_id, spell_activity_id):
        """
        Get the currently open observation and partially complete it giving a
        'refused' partial reason. Return the next created observation.

        :param patient_id:
        :type patient_id: int
        :param spell_activity_id:
        :type spell_activity_id: int
        :return: Next observation created after the completed partial one.
        """
        return self.complete_open_obs_as_partial(
            patient_id, spell_activity_id, 'refused')
