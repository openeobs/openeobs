# -*- coding: utf-8 -*-
from openerp import models


class NeurologicalFields(models.AbstractModel):

    _name = 'nh.clinical.test.neurological.common'

    def get_gcs_fields(self):
        self.neuro_model = \
            self.env['nh.clinical.patient.observation.neurological']
        return [
            self.neuro_model._fields['eyes'],
            self.neuro_model._fields['verbal'],
            self.neuro_model._fields['motor']
        ]

    def get_pupil_size_fields(self):
        self.neuro_model = \
            self.env['nh.clinical.patient.observation.neurological']
        return [
            self.neuro_model._fields['pupil_right_size'],
            self.neuro_model._fields['pupil_left_size']
        ]

    def get_pupil_reaction_fields(self):
        self.neuro_model = \
            self.env['nh.clinical.patient.observation.neurological']
        return [
            self.neuro_model._fields['pupil_right_reaction'],
            self.neuro_model._fields['pupil_left_reaction']
        ]

    def get_limb_movement_fields(self):
        self.neuro_model = \
            self.env['nh.clinical.patient.observation.neurological']
        return [
            self.neuro_model._fields['limb_movement_left_arm'],
            self.neuro_model._fields['limb_movement_right_arm'],
            self.neuro_model._fields['limb_movement_left_leg'],
            self.neuro_model._fields['limb_movement_right_leg']
        ]

    def get_all_fields(self):
        return self.get_gcs_fields() + \
               self.get_pupil_size_fields() + \
               self.get_pupil_reaction_fields() + \
               self.get_limb_movement_fields()

    def get_mandatory_fields(self):
        return self.get_gcs_fields()

    def get_field_names(self, fields):
        return [field.name for field in fields]

    def get_field_labels(self, fields):
        return [field.string for field in fields]

    def get_mandatory_field_names(self):
        fields = self.get_mandatory_fields()
        return [field.name for field in fields]

    def get_valid_value_for_field(self, field_name):
        self.neuro_model = \
            self.env['nh.clinical.patient.observation.neurological']

        fields = self.neuro_model.fields_get([field_name])
        field = fields[field_name]
        selection = field['selection']
        return selection[0][0]
