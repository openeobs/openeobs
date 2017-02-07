# -*- coding: utf-8 -*-
from openerp.models import Model


class NhEobsApi(Model):

    _name = 'nh.eobs.api'
    _inherit = 'nh.eobs.api'

    # TODO Change this to be a field so that it can be overridden.
    _active_observations = [
        {
            'type': 'ews',
            'name': 'NEWS'
        },
        {
            'type': 'height',
            'name': 'Height'
        },
        {
            'type': 'weight',
            'name': 'Weight'
        },
        {
            'type': 'blood_product',
            'name': 'Blood Product'
        },
        {
            'type': 'blood_sugar',
            'name': 'Blood Sugar'
        },
        {
            'type': 'stools',
            'name': 'Bowel Open'
        },
        {
            'type': 'gcs',
            'name': 'Glasgow Coma Scale (GCS)'
        },
        {
            'type': 'pbp',
            'name': 'Postural Blood Pressure'
        },
        {
            'type': 'neurological',
            'name': 'Neurological'
        }
    ]