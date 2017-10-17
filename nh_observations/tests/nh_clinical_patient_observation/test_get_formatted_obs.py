# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


convert_datetime_fields_to_client_timezone_called = False


class TestGetFormattedObs(TransactionCase):

    def setUp(self):
        super(TestGetFormattedObs, self).setUp()
        test_utils = self.env['nh.clinical.test_utils']
        test_utils.create_patient_and_spell()
        test_utils.copy_instance_variables(self)

    def test_calls_convert_datetime_fields_to_client_timezone(self):
        obs_model = self.env['nh.clinical.patient.observation']

        def mock_convert_datetime_fields_to_client_timezone(*args, **kwargs):
            global convert_datetime_fields_to_client_timezone_called
            convert_datetime_fields_to_client_timezone_called = True
            return mock_convert_datetime_fields_to_client_timezone.origin(
                *args, **kwargs)
        obs_model._patch_method(
            '_convert_datetime_fields_to_client_timezone',
            mock_convert_datetime_fields_to_client_timezone)

        try:
            obs_model.get_formatted_obs(
                convert_datetimes_to_client_timezone=True)
        finally:
            obs_model._revert_method(
                '_convert_datetime_fields_to_client_timezone')

        self.assertTrue(convert_datetime_fields_to_client_timezone_called)
