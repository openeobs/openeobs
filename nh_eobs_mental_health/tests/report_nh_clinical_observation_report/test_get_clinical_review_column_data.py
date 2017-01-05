# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestClinicalReviewColumnData(TransactionCase):

    def setUp(self):
        super(TestClinicalReviewColumnData, self).setUp()
        self.report_model = self.env['report.nh.clinical.observation_report']

        self.mock_refusal_episode = {
            'count': 1,
            'first_refusal_date_terminated': '2017-01-03 17:49:11.36621',
            'freq_date_terminated': None,
            'freq_state': None,
            'freq_terminate_uid': None,
            'review_date_terminated': None,
            'review_state': None,
            'review_terminate_uid': None,
            'spell_activity_id': 10
        }
        self.na = 'N/A'
        self.task_in_progress = 'Task in progress'

    def call_test(self, review_state=None):
        if review_state is 'started':
            self.mock_refusal_episode['clinical_review_state'] = review_state
        elif review_state is 'completed':
            self.mock_refusal_episode['clinical_review_state'] = review_state
            self.mock_refusal_episode['review_date_terminated'] = \
                '2017-02-03 13:45:16:35541'
            self.mock_refusal_episode['review_terminate_uid'] = 1

        self.clinical_review_column_data = \
            self.report_model.get_clinical_review_column_data(
                self.mock_refusal_episode)

    def test_review_state_none_returns_not_applicable(self):
        self.call_test()
        self.assertEqual(self.clinical_review_column_data,
                         self.na)

    def test_review_state_started_returns_task_in_progress(self):
        self.call_test('started')
        self.assertEqual(self.clinical_review_column_data,
                         self.task_in_progress)

    def test_review_state_completed_returns_date_terminated_and_uid_dict(self):
        self.call_test('completed')
        expected = {
            'date': self.mock_refusal_episode['review_date_terminated'],
            'by': self.mock_refusal_episode['review_terminate_uid']
        }
        self.assertEqual(self.clinical_review_column_data,
                         expected)
