# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


convert_activities_dates_to_context_dates_called = False


class TestAddExtraEwsWithClinicalReviewInDatetimeRange(TransactionCase):
    def setUp(self):
        super(TestAddExtraEwsWithClinicalReviewInDatetimeRange, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)

        self.report_model = self.env['report.nh.clinical.observation_report']
        self.report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']
        self.report_wizard = self.report_wizard_model.create({})

    def call_test(self):
        self.report_model.add_extra_ews_with_clinical_review_in_datetime_range(
            self.report_wizard, [], self.spell_activity.id)

    def test_calls_convert_activities_dates_to_context_dates(self):

        def mock_convert_activities_dates_to_context_dates(*args, **kwargs):
            global convert_activities_dates_to_context_dates_called
            convert_activities_dates_to_context_dates_called = True
            return mock_convert_activities_dates_to_context_dates.origin(
                *args, **kwargs)
        self.report_model._patch_method(
            'convert_activities_dates_to_context_dates',
            mock_convert_activities_dates_to_context_dates)

        try:
            self.call_test()
        finally:
            self.report_model._revert_method(
                'convert_activities_dates_to_context_dates')

        self.assertTrue(convert_activities_dates_to_context_dates_called)
