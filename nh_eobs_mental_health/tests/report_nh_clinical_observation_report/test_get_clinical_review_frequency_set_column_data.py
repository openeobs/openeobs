# -*- coding: utf-8 -*-
from copy import deepcopy

from openerp.tests.common import TransactionCase

from . import patient_refusal_event_fixtures


class TestGetClinicalReviewFrequencySetColumnData(TransactionCase):

    def setUp(self):
        super(TestGetClinicalReviewFrequencySetColumnData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.refusal_episode_fixture = \
            deepcopy(patient_refusal_event_fixtures.refusal_episode_first)
        self.not_applicable = 'N/A'
        self.task_in_progress = 'Task in progress'

    def call_test(self, review_state=None):
        if review_state is 'started':
            self.refusal_episode_fixture['freq_state'] = review_state
        elif review_state is 'completed':
            self.refusal_episode_fixture['freq_state'] = review_state
            self.refusal_episode_fixture['freq_date_terminated'] = \
                '2017-02-03 13:45:16:35541'
            self.refusal_episode_fixture['freq_terminate_uid'] = 1

        self.clinical_review_frequency_set_column_data = \
            self.report_model.get_clinical_review_frequency_set_column_data(
                self.refusal_episode_fixture)

    def test_review_state_none_returns_not_applicable(self):
        self.call_test()
        self.assertEqual(self.clinical_review_frequency_set_column_data,
                         self.not_applicable)

    def test_review_state_started_returns_task_in_progress(self):
        self.call_test('started')
        self.assertEqual(self.clinical_review_frequency_set_column_data,
                         self.task_in_progress)

    def test_review_state_completed_returns_date_terminated_and_uid_dict(self):
        self.call_test('completed')
        expected = {
            'date_terminated':
                self.refusal_episode_fixture['freq_date_terminated'],
            'user_id': self.refusal_episode_fixture['freq_terminate_uid']
        }
        self.assertEqual(self.clinical_review_frequency_set_column_data,
                         expected)
