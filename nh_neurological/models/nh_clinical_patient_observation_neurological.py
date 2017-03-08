# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.addons.nh_observations import fields as obs_fields


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
        ['NO', 'Not Observable']
    ]
    _pupil_reaction_selection = [
        ('+', '+'),
        ('-', '-'),
        ('NT', 'Not Testable')
    ]
    _limb_movement_selection = [
        ('NP', 'Normal Power'),
        ('MW', 'Mild Weakness'),
        ('SW', 'Severe Weakness'),
        ('SF', 'Spastic Flexion'),
        ('EX', 'Extension'),
        ('NR', 'No Response'),
        ('NO', 'Not Observable')
    ]

    _description = "Neurological Observation"
    # TODO Remove when EOBS-982 complete.
    # Also decides the order fields are displayed in the mobile view.
    _required = [
        'eyes', 'verbal', 'motor', 'pupil_right_size', 'pupil_right_reaction',
        'pupil_left_size', 'pupil_left_reaction',
        'limb_movement_left_arm', 'limb_movement_right_arm',
        'limb_movement_left_leg', 'limb_movement_right_leg'
    ]

    pupil_right_size = obs_fields.Selection(
        _pupil_size_selection, 'Pupil Right - Size')
    pupil_right_reaction = obs_fields.Selection(
        _pupil_reaction_selection, 'Pupil Right - Reaction'
    )
    pupil_left_size = obs_fields.Selection(
        _pupil_size_selection, 'Pupil Left - Size')
    pupil_left_reaction = obs_fields.Selection(
        _pupil_reaction_selection, 'Pupil Left - Reaction'
    )
    limb_movement_left_arm = obs_fields.Selection(
        _limb_movement_selection, 'Limb Movement - Left Arm'
    )
    limb_movement_right_arm = obs_fields.Selection(
        _limb_movement_selection, 'Limb Movement - Right Arm'
    )
    limb_movement_left_leg = obs_fields.Selection(
        _limb_movement_selection, 'Limb Movement - Left Leg'
    )
    limb_movement_right_leg = obs_fields.Selection(
        _limb_movement_selection, 'Limb Movement - Right Leg'
    )

    @api.model
    def get_form_description(self, patient_id):
        """
        Returns a list of dicts that represent the form description used by
        the mobile

        :param patient_id: ID for the patient
        :return: list of dicts
        """
        form_description = super(NhClinicalPatientObservationNeurological,
                                 self).get_form_description(patient_id)
        for item in form_description:
            if item.get('type') == 'meta':
                item['partial_flow'] = 'score'
        return form_description

    @classmethod
    def get_data_visualisation_resource(cls):
        """
        Returns URL of JS file to plot data visualisation so can be loaded on
        mobile and desktop

        :return: URL of JS file to plot graph
        :rtype: str
        """
        return '/nh_neurological/static/src/js/chart.js'
