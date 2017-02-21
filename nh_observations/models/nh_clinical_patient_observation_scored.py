# -*- coding: utf-8 -*-
import logging

from openerp import models, fields, api
from openerp.addons.nh_observations.observations \
    import NhClinicalPatientObservation


_logger = logging.getLogger(__name__)


class NhClinicalPatientObservationScored(models.AbstractModel):
    """
    Extends the 'nh.clinical.patient.observation' model to introduce the
    concept of a score. Provides a computed 'score' field with a default
    implementation for its calculation.
    """
    _name = 'nh.clinical.patient.observation_scored'
    _inherit = 'nh.clinical.patient.observation'

    @api.depends(NhClinicalPatientObservation.get_obs_field_names)
    def _get_score(self):
        """
        Calculates the score and sets it on the observation, causing it to be
        persisted in the database due to the score fields 'store' attribute.
        """
        for record in self:
            score = record.calculate_score(record, return_dictionary=False)
            record.score = score
            _logger.debug(
                "%s activity_id=%s gcs_id=%s score: %s"
                % (self._description, self.activity_id.id, self.id, score)
            )

    score = fields.Integer(
        compute='_get_score', string='Score', store=True
    )

    def calculate_score(self, record, return_dictionary=True):
        """
        Gets the values of the 'score fields' that contribute to the overall
        score of the observation and maps them to an integer score.

        This generic score calculation implementation is then to simply sum all
        the individual fields scores to get the overall score for the
        observation.

        :param record: Observation field values. If an Odoo record is passed
        then the 'score fields' are looked up for the calculation. If a
        dictionary of field data is passed, only the fields in the dictionary
        are used.
        :type record: record or dict
        :param return_dictionary: Would you like the score returned in a
        dictionary?
        :type return_dictionary: bool
        :returns: ``score``
        :rtype: dict or int
        """
        values_for_score_calculation = []
        fields_dict = record if isinstance(record, dict) \
            else record.get_necessary_fields_dict()

        for field in fields_dict.items():
            field_name = field[0]
            field_value = field[1]
            field_value = self.get_score_for_value(self, field_name,
                                                   field_value)
            values_for_score_calculation.append(field_value)

        score = sum(values_for_score_calculation)
        return {'score': score} if return_dictionary else score

    @classmethod
    def get_score_for_value(cls, model, field_name, field_value):
        """
        The values of 'score fields' are decoupled from the integer score that
        they contribute to the overall score of the observation. This is to
        make changes to the scoring system easier as score values themselves
        are not stored in the database, so adding or changing the scores
        certain field values map to has less impact.

        This method returns the integer score a field value represents based on
        the position it is declared in the fields 'selection' attribute.

        :param model:
        :type model: Odoo model instance.
        :param field_name:
        :type field_name: str
        :param field_value:
        :type field_value: str
        :return:
        :rtype: int
        """
        selection = model._fields[field_name].selection
        selection = reversed(selection)
        selection_values = \
            [value_and_label[0] for value_and_label in selection]
        field_score = selection_values.index(field_value)
        return field_score

    # TODO: EOBS-993 Make scored obs read method override dynamic
    @api.multi
    def read(self, fields=None, load='_classic_read',
             convert_field_values_to_scores=True):
        """
        An override of read to ensure that for scored observations, reads will
        by default return the mapped score values for fields rather then their
        actual field values. Usually when read is called instead of browse it
        is because the raw data is needed to send over the network. Often in
        these situations the score value is desirable over the normal
        score-agnostic value.

        The decision to make this behaviour default is based only on a few use
        cases encountered since starting to use this model, it may be that
        refactoring is appropriate in future.

        :param fields:
        :param load:
        :param convert_field_values_to_scores:
        :type convert_field_values_to_scores: bool
        :return:
        :rtype: list
        """
        obs = super(NhClinicalPatientObservationScored, self).read(
            fields=fields, load=load
        )
        obs_list = [obs] if not isinstance(obs, list) else obs
        if convert_field_values_to_scores and self._name == \
                'nh.clinical.patient.observation.neurological':
            self.convert_field_values_to_scores(obs_list)
        return obs

    def convert_field_values_to_scores(self, obs):
        """
        Converts the values of all 'score fields' to their individual field
        scores.

        :param obs:
        :type obs: list of dict
        :return:
        :rtype: list of dict
        """
        if not hasattr(self, '_scored'):
            return
        for ob in obs:
            for field_name in self._scored:
                field_value = ob.get(field_name)
                if field_value and field_value != 'NT':
                    field_score = self.get_score_for_value(self, field_name,
                                                           field_value)
                    ob[field_name] = str(field_score)

    def fields_view_get(self, *args, **kwargs):
        """
        Hack to allow display of field scores instead of field values in Odoo
        views. When an Odoo view is rendered the field definitions are
        retrieved via this method as well as the field values themselves.
        Validation occurs client-side and if it fails the values seem to be
        silently omitted from the view.

        This method intercepts the retrival of the field definition and
        converts the type of the fields to 'text', effectively allowing the
        converted score value of the field (which is a string representation
        of a number) to pass validation.

        :param args:
        :param kwargs:
        :return:
        """
        fields_view_dict = super(NhClinicalPatientObservationScored, self)\
            .fields_view_get(*args, **kwargs)
        if not hasattr(self, '_scored'):
            return fields_view_dict
        for scored_field_name in self._scored:
            scored_field = fields_view_dict['fields'].get(scored_field_name)
            if scored_field:
                scored_field['type'] = 'text'
                del scored_field['selection']
        return fields_view_dict

    # TODO Set once on model load rather than process every time.
    # Tried setting on init() but seems to only be called when module is
    # updated.
    @api.model
    def get_form_description(self, patient_id):
        """
        Returns a description in dictionary format of the input fields
        that would be required in the user gui to submit the
        observation.

        :param patient_id: :class:`patient<base.nh_clinical_patient>` id
        :type patient_id: int
        :returns: a list of dictionaries
        :rtype: list
        """
        form_description_model = self.env['nh.clinical.form_description']
        form_description = form_description_model.to_dict(self)
        form_description.append({
            'name': 'meta',
            'type': 'meta',
            'score': True,
        })
        return form_description
