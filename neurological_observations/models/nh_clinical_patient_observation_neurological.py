# -*- coding: utf-8 -*-
from openerp import models, fields

class NhClinicalPatientObservationEws(models.Model):

    _name = 'nh.clinical.patient.observation.neurological'
    _inherit = 'nh.clinical.patient.observation.gcs'

    _pupil_sizes = [
        ['8', '8mm'],
        ['7', '7mm'],
        ['6', '6mm'],
        ['5', '5mm'],
        ['4', '4mm'],
        ['3', '3mm'],
        ['2', '2mm'],
        ['1', '1mm'],
    ]

    pupil_right_size = fields.Selection(_pupil_sizes, 'Right Pupil Size'),
    pupil_left_size = fields.Selection(_pupil_sizes, 'Left Pupil Size'),
    pupil_right_reaction = fields.Selection(
        [['yes', 'Yes'], ['no', 'No'], ['sluggish', 'Sluggish']],
        'Right Pupil Reaction'
    ),
    pupil_left_reaction = fields.Selection(
        [['yes', 'Yes'], ['no', 'No'], ['sluggish', 'Sluggish']],
        'Left Pupil Reaction'
    )

    def get_form_description(self, cr, uid, patient_id, context=None):
        form_description = list(self._form_description)
        form_description.append({
            'name': 'pupil_right_size',
            'type': 'selection',
            'label': 'Right Pupil Size',
            'selection': self._pupil_sizes,
            'selection_type': 'text',
            'initially_hidden': False
        })
        form_description.append({
            'name': 'pupil_right_reaction',
            'type': 'selection',
            'label': 'Right Pupil Reaction',
            'selection': [['yes', 'Yes'], ['no', 'No'], ['sluggish', 'Sluggish']],
            'selection_type': 'text',
            'initially_hidden': False,
        })
        form_description.append({
            'name': 'pupil_left_size',
            'type': 'selection',
            'label': 'Left Pupil Size (mm)',
            'selection': self._pupil_sizes,
            'selection_type': 'text',
            'initially_hidden': False
        })
        form_description.append({
            'name': 'pupil_left_reaction',
            'type': 'selection',
            'label': 'Left Pupil Reaction',
            'selection': [['yes', 'Yes'], ['no', 'No'], ['sluggish', 'Sluggish']],
            'selection_type': 'text',
            'initially_hidden': False,
        })
        return form_description
