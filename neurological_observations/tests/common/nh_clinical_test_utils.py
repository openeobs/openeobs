# -*- coding: utf-8 -*-
from openerp.addons.neurological_observations.tests.common \
    import neurological_fixtures
from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    def create_and_complete_neuro_obs(self, patient_id, data, user=None):
        user_id = user.id if user else self.env.uid
        activity_pool = \
            self.pool['nh.clinical.patient.observation.neurological']
        neuro_obs_data = neurological_fixtures.SAMPLE_DATA
        neuro_obs_data['patient_id'] = patient_id
        neuro_obs_activity_id = activity_pool.create_activity(
            self.env.cr, user_id, vals_data=neuro_obs_data
        )
        activity_pool.submit(self.env.cr, user_id, neuro_obs_activity_id, data)
        activity_pool.complete(self.env.cr, user_id, neuro_obs_activity_id)
