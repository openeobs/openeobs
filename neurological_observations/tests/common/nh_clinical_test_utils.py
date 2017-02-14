# -*- coding: utf-8 -*-
from openerp.addons.neurological_observations.tests.common import neurological_fixtures
from openerp.models import AbstractModel


class NhClinicalTestUtils(AbstractModel):

    _name = 'nh.clinical.test_utils'
    _inherit = 'nh.clinical.test_utils'

    def create_and_complete_neuro(self, data):
        neuro_model = self.env['nh.clinical.patient.observation.neurological']
        data = neurological_fixtures.SAMPLE_DATA
        neuro_obs = neuro_model.create(data)
        neuro_obs.complete()