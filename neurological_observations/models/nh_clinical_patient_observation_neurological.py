# -*- coding: utf-8 -*-
from openerp import models, fields, api


class NhClinicalPatientObservationNeurological(models.Model):

    _name = 'nh.clinical.patient.observation.neurological'
    _inherit = 'nh.clinical.patient.observation.gcs'

    _pupil_size_selection = [
        ['8', '8mm'],
        ['7', '7mm'],
        ['6', '6mm'],
        ['5', '5mm'],
        ['4', '4mm'],
        ['3', '3mm'],
        ['2', '2mm'],
        ['1', '1mm'],
        ['not observable', 'Not Observable']
    ]
    _limb_movement_selection = [
        ('normal power', 'Normal Power'),
        ('mild weakness', 'Mild Weakness'),
        ('severe weakness', 'Severe Weakness'),
        ('spastic flexion', 'Spastic Flexion'),
        ('extension', 'Extension'),
        ('no response', 'No Response'),
        ('not observable', 'Not Observable')
    ]
    _pupil_reaction_selection = [
        ('yes', 'Yes'), ('no', 'No'),
        ('sluggish', 'Sluggish')
    ]

    pupil_right_size = fields.Selection(_pupil_size_selection,
                                        'Pupil Right - Size')
    pupil_left_size = fields.Selection(_pupil_size_selection,
                                       'Pupil Left - Size')
    pupil_right_reaction = fields.Selection(
        _pupil_reaction_selection, 'Pupil Left - Reaction'
    )
    pupil_left_reaction = fields.Selection(
        _pupil_reaction_selection, 'Pupil Right - Reaction'
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

    # TODO Set once on model load rather than process every time.
    # Tried setting on init() but seems to only be called when module is
    # updated.
    @api.model
    def get_form_description(self, patient_id):
        form_description = list(self._form_description) # Make a copy.
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
        form_description.extend(form_description_neuro_fields)
        return form_description
