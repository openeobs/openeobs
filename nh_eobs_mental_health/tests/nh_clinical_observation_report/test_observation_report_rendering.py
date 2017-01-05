# -*- coding: utf-8 -*-
# from datetime import datetime, timedelta
#
# import re
# from bs4 import BeautifulSoup
# from openerp.addons.nh_eobs.tests.nh_clinical_observation_report\
#     .observation_report_helpers import ObservationReportHelpers
#
#
# class TestObservationReportRendering(ObservationReportHelpers):
#
#     def setUp(self):
#         super(ObservationReportHelpers, self).setUp()
#         self.test_utils_model = self.env['nh.clinical.test_utils']
#         self.test_utils_model.admit_and_place_patient()
#
#         self.spell = self.test_utils_model.spell
#         self.spell_activity = self.test_utils_model.spell_activity
#         self.patient = self.test_utils_model.patient
#
#         self.report_model = self.env['report.nh.clinical.observation_report']
#         self.ews_model = self.env['nh.clinical.patient.observation.ews']
#         self.activity_model = self.env['nh.activity']
#
#         self.patient.follower_ids = [1]
#         self.refused_obs_activity = \
#             self.ews_model.get_open_obs_activity(self.spell_activity.id)
#         self.test_utils_model.refuse_open_obs(self.patient.id,
#                                               self.spell_activity.id)
#
#         self.report_data = {
#             'spell_id': self.spell.id,
#             'start_date': None,
#             'end_date': None,
#             'ews_only': True
#         }
#         self.datetime_start = datetime.now() + timedelta(days=1)
#         self.datetime_end = datetime.now() + timedelta(days=2)
#
#         self.expected_score_regex = r'\s*Partial - N/A\s*Reason: {}\s*'
#         self.expected_clinical_risk_regex = r'\s*Partial - N/A\s*'
#
#     def tearDown(self):
#         super(ObservationReportHelpers, self).tearDown()
#
#     def create_clinical_review_activity_at_datetime(self, date_scheduled):
#         self.clinical_review_model = \
#             self.env['nh.clinical.notification.clinical_review']
#         return self.clinical_review_model.create_activity(
#             {
#                 'date_scheduled': date_scheduled,
#                 'date_deadline': date_scheduled,
#                 'parent_id': self.spell_activity.id,
#                 'creator_id': self.refused_obs_activity.id
#             },
#             {
#                 'patient_id': self.patient.id
#             }
#         )
#
#     def call_test(self, score_regex, clinical_risk_regex,
#                   clinical_review_triggered=False,
#                   clinical_review_completed=False):
#         if clinical_review_triggered or clinical_review_completed:
#             datetime_scheduled = datetime.now() + timedelta(days=7)
#             activity_id = self.create_clinical_review_activity_at_datetime(
#                 datetime_scheduled
#             )
#         if clinical_review_completed:
#             self.activity_model.complete(activity_id)
#
#         report_html = self.report_model.render_html(data=self.report_data)
#         beautiful_report = BeautifulSoup(report_html, 'html.parser')
#
#         score = beautiful_report.select('#triggered_actions_score')[0]
#         score_text = score.getText()
#         clinical_risk = \
#             beautiful_report.select('#triggered_actions_clinical_risk')[0]
#         clinical_risk_text = clinical_risk.getText()
#
#         pattern = re.compile(score_regex)
#         match = pattern.match(score_text)
#         self.assertTrue(match)
#         pattern = re.compile(clinical_risk_regex)
#         match = pattern.match(clinical_risk_text)
#         self.assertTrue(match)
#
#         if clinical_review_triggered:
#             triggered_actions = \
#                 beautiful_report.select('.triggered_action_task')
#             self.assertEqual(len(triggered_actions), 1)
#
#             triggered_action_task_headers = \
#                 beautiful_report.select('.triggered_action_task_header')
#             self.assertEqual(len(triggered_action_task_headers), 1)
#
#             triggered_action_task_header = triggered_action_task_headers[0]
#             self.assert_clinical_review_task_existence(
#                 triggered_action_task_header
#             )
#
#         if clinical_review_completed:
#             triggered_actions = \
#                 beautiful_report.select(r'.triggered_action_task')
#             self.assertEqual(len(triggered_actions), 2)
#
#             triggered_action_task_headers = \
#                 beautiful_report.select(r'.triggered_action_task_header')
#             self.assertEqual(len(triggered_action_task_headers), 2)
#
#             triggered_action_task_header = triggered_action_task_headers[0]
#             self.assert_clinical_review_task_existence(
#                 triggered_action_task_header
#             )
#             triggered_action_task_header = triggered_action_task_headers[1]
#             self.assert_clinical_review_frequency_task_existence(
#                 triggered_action_task_header
#             )
#
#     def assert_clinical_review_task_existence(self, element):
#         clinical_review_regex = r'\s*Clinical Review\s*'
#         pattern = re.compile(clinical_review_regex)
#         match = pattern.match(element.getText())
#         self.assertTrue(match)
#
#     def assert_clinical_review_frequency_task_existence(self, element):
#         clinical_review_frequency_regex = \
#             r'\s*Set Clinical Review Frequency\s*'
#         pattern = re.compile(clinical_review_frequency_regex)
#         match = pattern.match(element.getText())
#         self.assertTrue(match)
#
#     def test_partial_with_reason_refused(self):
#         self.call_test(self.expected_score_regex.format('Refusal'),
#                        self.expected_clinical_risk_regex)
#
#     def test_partial_with_reason_other_than_refused(self):
#         self.refused_obs_activity.data_ref.partial_reason = 'asleep'
#         self.call_test(self.expected_score_regex.format('Asleep'),
#                        self.expected_clinical_risk_regex)
#
#     def test_clinical_review_task_triggered(self):
#         self.call_test(self.expected_score_regex.format('Refusal'),
#                        self.expected_clinical_risk_regex,
#                        clinical_review_triggered=True)
#
#     def test_set_clinical_review_frequency_task_triggered(self):
#         self.call_test(self.expected_score_regex.format('Refusal'),
#                        self.expected_clinical_risk_regex,
#                        clinical_review_completed=True)
