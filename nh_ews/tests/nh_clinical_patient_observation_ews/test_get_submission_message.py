# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestGetSubmissionMessage(TransactionCase):

    def setUp(self):
        super(TestGetSubmissionMessage, self).setUp()
        self.ews_model = self.env['nh.clinical.patient.observation.ews']

        def mock_get_triggered_tasks(*args, **kwargs):
            context = self.env.context
            if context and context.get('test'):
                test = context.get('test')
                if test == 'triggered_tasks':
                    return [
                        {'a_task': 'do some stuff yo'},
                        {'THE_TASK': 'DO ME'},
                        {'la_task': 'je m\'apelle task'}
                    ]
                if test == 'no_triggered_tasks':
                    return []
            return mock_get_triggered_tasks.origin(*args, **kwargs)

        self.ews_model._patch_method('get_triggered_tasks',
                                     mock_get_triggered_tasks)

        self.obs = self.ews_model.new({})

    def test_partial_with_clinical_risk(self):
        self.obs.is_partial = True
        self.obs.respiration_rate = 11
        self.obs.indirect_oxymetry_spo2 = 80
        self.obs.body_temperature = 42
        self.obs.pulse_rate = 50
        self.obs.oxygen_administration_flag = False
        self.obs.avpu_text = 'A'

        expected = \
            '<strong>At least High clinical risk</strong>, ' \
            'real risk may be higher <br>' \
            '<strong>At least 7 NEWS score</strong>, ' \
            'real NEWS score may be higher<br>' \
            'This Partial Observation will not update the ' \
            'NEWS score and clinical risk of the ' \
            'patient'
        actual = self.obs.get_submission_message()

        self.assertEqual(expected, actual)

    def test_partial_with_no_clinical_risk(self):
        self.obs.is_partial = True

        expected = \
            '<strong>Clinical risk:</strong> Unknown<br>' \
            '<strong>NEWS Score:</strong> Unknown<br>' \
            'This Partial Observation will not update the ' \
            'NEWS score and clinical risk of the patient'
        actual = self.obs.get_submission_message()

        self.assertEqual(expected, actual)

    def test_full_with_triggered_tasks(self):
        self.obs.is_partial = False
        self.env.context = {'test': 'triggered_tasks'}

        expected = 'Here are related tasks based on the observation'
        actual = self.obs.get_submission_message()

        self.assertEqual(expected, actual)

    def test_full_with_no_triggered_tasks(self):
        self.obs.is_partial = False
        self.env.context = {'test': 'no_triggered_tasks'}

        expected = ''
        actual = self.obs.get_submission_message()

        self.assertEqual(expected, actual)

    def tearDown(self):
        self.ews_model._revert_method('get_triggered_tasks')
        super(TestGetSubmissionMessage, self).tearDown()
