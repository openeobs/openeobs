# -*- coding: utf-8 -*-
from openerp import models, fields


class NhClinicalPatientObservationNeurological(models.Model):

    def init(self, cr):
        self.set_form_description()

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
    _limb_movement_selection = [
        ('normal power', 'Normal Power'),
        ('mild weakness', 'Mild Weakness'),
        ('severe weakness', 'Severe Weakness'),
        ('spastic flexion', 'Spastic Flexion'),
        ('extension', 'Extension'), ('no response', 'No Response'),
        ('not observable', 'Not Observable')
    ]
    _pupil_reaction_selection = [
        ('yes', 'Yes'), ('no', 'No'),
        ('sluggish', 'Sluggish')
    ]

    pupil_right_size = fields.Selection(_pupil_sizes, 'Right Pupil Size')
    pupil_left_size = fields.Selection(_pupil_sizes, 'Left Pupil Size')
    pupil_right_reaction = fields.Selection(
        _pupil_reaction_selection, 'Right Pupil Reaction'
    )
    pupil_left_reaction = fields.Selection(
        _pupil_reaction_selection, 'Left Pupil Reaction'
    )
    limb_movement_left_arm = fields.Selection(
        _limb_movement_selection, 'Limb Movement - Left Arm'
    )
    limb_movement_right_arm = fields.Selection(
        _limb_movement_selection, 'Limb Movement - Right Arm'
    )
    limb_movement_left_leg = fields.Selection(
        _limb_movement_selection, 'Limb Movement - Left Leg'
    )
    limb_movement_right_leg = fields.Selection(
        _limb_movement_selection, 'Limb Movement - Right leg'
    )

    def set_form_description(self):
        # env not available when called from init but pool is.
        converter = self.pool['field_to_form_description_converter']
        form_description_neuro_fields = converter.convert([
            self._fields['pupil_right_size'],
            self._fields['pupil_left_size'],
            self._fields['pupil_right_reaction'],
            self._fields['pupil_left_reaction'],
            self._fields['limb_movement_left_arm'],
            self._fields['limb_movement_right_arm'],
            self._fields['limb_movement_left_leg'],
            self._fields['limb_movement_right_leg']
        ])
        self._form_description.extend(form_description_neuro_fields)
