# -*- coding: utf-8 -*-
from openerp import api
from openerp.models import Model


class NhEobsApi(Model):

    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    @api.model
    def get_active_observations(self, patient_id):
        active_obs = super(NhEobsApi, self).get_active_observations(patient_id)
        active_obs = list(active_obs)
        active_obs.append({
            'type': 'neurological',
            'name': 'Neurological'
        })
        return active_obs
