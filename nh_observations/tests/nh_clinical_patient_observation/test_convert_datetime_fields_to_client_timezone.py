# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestConvertDatetimeFieldsToClientTimezone(TransactionCase):

    def setUp(self):
        super(TestConvertDatetimeFieldsToClientTimezone, self).setUp()
        self.obs_model = self.env['nh.clinical.patient.observation']
        self.obs = self.obs_model.new({}).with_context({'tz': 'Europe/London'})

        self.fake_obs_dict_list = [{
            'date_started': None, 'date_terminated': None
        }]
        self.fake_obs_dict = self.fake_obs_dict_list[0]

    def call_test(self, date_started, date_terminated,
                  datetime_fields=None):
        if datetime_fields is None:
            datetime_fields = ['date_terminated', 'date_started']
        self.fake_obs_dict['date_terminated'] = date_terminated
        self.fake_obs_dict['date_started'] = date_started

        self.obs._convert_datetime_fields_to_client_timezone(
            self.fake_obs_dict_list, datetime_fields)

    def test_converts_timezones(self):
        date_terminated = '2017-05-03 17:00:00'
        date_started = '2017-05-03 16:00:00'

        self.call_test(date_started, date_terminated)

        expected = '2017-05-03 18:00:00'
        actual = self.fake_obs_dict.get('date_terminated')
        self.assertEqual(expected, actual)

    def test_handles_false(self):
        date_terminated = False
        date_started = '2017-05-03 16:00:00'

        # Implicit assertion that no exceptions are thrown.
        self.call_test(date_started, date_terminated)

        expected = False
        actual = self.fake_obs_dict.get('date_terminated')
        self.assertIs(expected, actual)

    def test_has_no_side_effects(self):
        date_terminated = '2017-05-03 17:00:00'
        date_started = '2017-05-03 16:00:00'

        expected = self.obs.date_terminated
        self.call_test(date_started, date_terminated)
        actual = self.obs.date_terminated

        self.assertEqual(expected, actual)
