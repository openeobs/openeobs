# -*- coding: utf-8 -*-
import logging

from openerp import models, api
from openerp.addons.nh_eobs.report import helpers

_logger = logging.getLogger(__name__)


class NhClinicalObservationReport(models.Model):

    _name = 'report.nh.clinical.observation_report'
    _inherit = 'report.nh.clinical.observation_report'

    @api.model
    def get_ews_observations(self, data, spell_activity_id):
        ews_activities = super(NhClinicalObservationReport, self)\
            .get_ews_observations(data, spell_activity_id)

        return self.add_extra_ews_with_clinical_review_in_datetime_range(
            data, ews_activities, spell_activity_id
        )

    def add_extra_ews_with_clinical_review_in_datetime_range(
            self, data, ews_activities, spell_activity_id):
        ews_activities_outside_datetime_range = \
            self.get_ews_activity_ids_with_clinical_review_in_datetime_range(
                spell_activity_id, data.start_time, data.end_time
            )
        ews_activity_ids_outside_datetime_range = \
            [ews.id for ews in ews_activities_outside_datetime_range]
        extra_ews_activity_ids = self.get_ids_not_already_in_dict_list(
            ews_activities, ews_activity_ids_outside_datetime_range
        )

        activity_model = self.pool['nh.activity']
        extra_ews_activities = activity_model.read(
            self.env.cr, self.env.uid, extra_ews_activity_ids
        )
        self.convert_activities_dates_to_context_dates(extra_ews_activities)
        extra_ews_activities = self.get_model_values(
            'nh.clinical.patient.observation.ews', extra_ews_activities
        )
        extra_ews_activities = \
            self.convert_partial_reasons_to_labels(extra_ews_activities)
        self.add_triggered_action_keys_to_obs_dicts(extra_ews_activities)
        return self.add_extra_ews_to_list(ews_activities, extra_ews_activities)

    def get_ews_activity_ids_with_clinical_review_in_datetime_range(
            self, spell_activity_id, start_datetime, end_datetime
    ):
        domain = helpers.create_search_filter(
            spell_activity_id, 'nh.clinical.notification.clinical_review',
            start_datetime, end_datetime,
            states=None, date_field='date_scheduled'
        )
        activity_model = self.env['nh.activity']
        clinical_review_notifications = activity_model.search(domain)
        return [clinical_review.creator_id for clinical_review
                in clinical_review_notifications]

    @classmethod
    def get_ids_not_already_in_dict_list(cls, dict_list, ids):
        dict_list_ids = [d['id'] for d in dict_list]
        return list(set(ids) - set(dict_list_ids))

    @classmethod
    def add_extra_ews_to_list(cls, some_ews, more_ews):
        number_extra_ews = abs(len(some_ews) - len(more_ews))
        if number_extra_ews:
            _logger.info(
                "{} extra EWS observations added to the report from "
                "outside the date range specified but triggered a clinical "
                "review task that is within the date range."
                .format(number_extra_ews)
            )
        some_ews.extend(more_ews)
        return some_ews
