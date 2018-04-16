# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from openerp.addons.nh_eobs.report.helpers import DataObj
from openerp.tests.common import TransactionCase


class TestGetEwsObservations(TransactionCase):

    def setUp(self):
        super(TestGetEwsObservations, self)\
            .setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()
        self.test_utils_model.copy_instance_variables(self)

        self.patient = self.test_utils_model.patient
        self.spell_activity = self.test_utils_model.spell_activity

        self.report_model = self.env['report.nh.clinical.observation_report']
        self.ews_model = self.env['nh.clinical.patient.observation.ews']
        self.clinical_review_model = \
            self.env['nh.clinical.notification.clinical_review']

        self.patient.follower_ids = [1]
        self.refused_obs = self.ews_model.get_open_obs_activity(
            self.spell_activity.id
        )
        self.test_utils_model.sudo(self.nurse.id).refuse_open_obs(
            self.patient.id, self.spell_activity.id
        )

        self.datetime_start = datetime.now() + timedelta(days=1)
        self.datetime_end = datetime.now() + timedelta(days=2)
        self.data = DataObj(self.spell_activity.id,
                            self.datetime_start, self.datetime_end)

    def create_clinical_review_activity_at_datetime(self, date_scheduled):
        return self.clinical_review_model.create_activity(
            {
                'date_scheduled': date_scheduled,
                'date_deadline': date_scheduled,
                'parent_id': self.spell_activity.id,
                'creator_id': self.refused_obs.id
            },
            {
                'patient_id': self.patient.id
            }
        )

    def call_test(self, within_datetime_range, extra_ews_expected,
                  complete_clinical_review=False):
        ews_activities_before = self.report_model.get_ews_observations(
            self.data, self.spell_activity.id
        )

        days = 1 if within_datetime_range else 0
        datetime_scheduled = datetime.now() + timedelta(days=days)
        activity_id = self.create_clinical_review_activity_at_datetime(
            datetime_scheduled
        )
        if complete_clinical_review:
            activity = self.env['nh.activity'].browse(activity_id)
            activity.complete()

        ews_activities_after = self.report_model.get_ews_observations(
            self.data, self.spell_activity.id
        )
        for ews_activity in ews_activities_after:
            self.assertTrue('triggered_actions' in ews_activity)
            if len(ews_activity['triggered_actions']) >= 1:
                self.assertEqual(
                    ews_activity['triggered_actions'][0]['summary'],
                    'Clinical Review'
                )
            if len(ews_activity['triggered_actions']) >= 2:
                self.assertEqual(
                    ews_activity['triggered_actions'][1]['summary'],
                    'Set Clinical Review Frequency'
                )

        self.assertEqual(len(ews_activities_after),
                         len(ews_activities_before) + extra_ews_expected)

    def test_clinical_review_outside_datetime_range(self):
        self.call_test(within_datetime_range=False, extra_ews_expected=0)

    def test_incomplete_clinical_review_within_datetime_range(self):
        self.call_test(within_datetime_range=True, extra_ews_expected=1)

    def test_complete_clinical_review_within_datetime_range(self):
        self.call_test(within_datetime_range=True, extra_ews_expected=1,
                       complete_clinical_review=True)
