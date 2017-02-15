# -*- coding: utf-8 -*-
"""
Extends the 'nh.clinical.patient.observation' model to introduce the concept
of a score. Provides a computed 'score' field with a default implementation for
its calculation.
"""
import logging

from openerp import models, fields, api
from openerp.addons.nh_observations.observations \
    import NhClinicalPatientObservation


_logger = logging.getLogger(__name__)


class NhClinicalPatientObservationScored(models.AbstractModel):

    _name = 'nh.clinical.patient.observation_scored'
    _inherit = 'nh.clinical.patient.observation'

    @api.depends(NhClinicalPatientObservation.get_obs_field_names)
    def _get_score(self):
        for record in self:
            score = record.calculate_score(record, return_dictionary=False)
            record.score = score
            _logger.debug(
                "%s activity_id=%s gcs_id=%s score: %s"
                % (self._description, self.activity_id.id, self.id, score)
            )

    def calculate_score(self, record, return_dictionary=True):
        """
        Sums all necessary observation fields that can be cast to an int.
        Fields that cannot be cast to an int are disregarded from the
        calculation.

        :param record: Observation field values.
        :type record: record or dict
        :param return_dictionary: Would you like the score returned in a
        dictionary?
        :type return_dictionary: bool
        :returns: ``score``
        :rtype: dict or int
        """
        values_for_score_calculation = []
        fields_dict = record if type(record) is dict \
            else record.get_necessary_fields_dict()

        for field in fields_dict.items():
            field_name = field[0]
            field_value = field[1]
            field_value = self.get_score_for_value(self, field_name,
                                                   field_value)
            values_for_score_calculation.append(field_value)

        score = sum(values_for_score_calculation)
        return {'score': score} if return_dictionary else score

    @staticmethod
    def get_score_for_value(model, field_name, field_value):
        selection = model._fields[field_name].selection
        selection = reversed(selection)
        selection_values = \
            [value_and_label[0] for value_and_label in selection]
        selection_index = selection_values.index(field_value)
        return selection_index

    score = fields.Integer(
        compute='_get_score', string='Score', store=True
    )

    # TODO: EOBS-993 Make scored obs read method override dynamic
    def read(self, *args, **kwargs):
        obs = super(NhClinicalPatientObservationScored, self).read(
            *args, **kwargs
        )
        if not hasattr(obs, '__iter__'):
            obs = [obs]
        if self._name == 'nh.clinical.patient.observation.neurological':
            for ob in obs:
                for field_name in ['eyes', 'verbal', 'motor']:
                    field_value = ob.get(field_name)
                    if field_value:
                        ob[field_name] = self.get_score_for_value(
                            self, field_name, field_value
                        )
        return obs
