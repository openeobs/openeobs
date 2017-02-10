# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.addons.nh_observations import fields


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
    _pupil_reaction_selection = [
        ('+', '+'),
        ('-', '-'),
        ('not testable', 'Not Testable')
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
    # TODO Remove when EOBS-982 complete.
    _required = [
        'eyes', 'verbal', 'motor', 'pupil_right_size', 'pupil_left_size',
        'pupil_left_reaction', 'pupil_right_reaction',
        'limb_movement_left_arm', 'limb_movement_right_arm',
        'limb_movement_left_leg', 'limb_movement_right_leg'
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
        form_description_model = self.env['nh.clinical.form_description']
        form_description_neuro_fields = form_description_model.to_dict(self)

        # Remove duplicates
        form_description_field_names = [field['name'] for field in form_description]
        form_description_neuro_fields = \
            [field for field in form_description_neuro_fields
             if field['name'] not in form_description_field_names]

        form_description.extend(form_description_neuro_fields)
        return form_description
