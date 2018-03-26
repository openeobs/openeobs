from datetime import datetime

from openerp.tests.common import SingleTransactionCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestGetNextEwsTime(SingleTransactionCase):

    def setUp(self):
        def stub_datetime_now(*args, **kwargs):
            now = datetime.strptime('2017-08-06 13:00:00', DTF)
            return now
        self.datetime_utils_model = self.env['datetime_utils']
        self.datetime_utils_model._patch_method(
            'get_current_time', stub_datetime_now)

    def tearDown(self):
        self.datetime_utils_model._revert_method('get_current_time')

    def call_test(self, date_scheduled):
        patient_model = self.env['nh.clinical.patient']
        return patient_model.get_next_ews_time(date_scheduled)

    def test_date_scheduled_is_none(self):
        expected = '00:00 hours'
        actual = self.call_test(None)
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_one_second_in_the_future(self):
        expected = '00:01 hours'
        actual = self.call_test('2017-08-06 13:00:01')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_one_hour_in_the_future(self):
        expected = '01:00 hours'
        actual = self.call_test('2017-08-06 14:00:00')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_less_than_one_day_in_the_future(self):
        expected = '23:59 hours'
        actual = self.call_test('2017-08-07 12:59:59')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_one_day_in_the_future(self):
        expected = '1 day(s) 00:00 hours'
        actual = self.call_test('2017-08-07 13:00:00')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_more_than_one_day_in_the_future(self):
        expected = '1 day(s) 00:01 hours'
        actual = self.call_test('2017-08-07 13:00:01')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_right_now(self):
        expected = '1 day(s) 00:00 hours'
        actual = self.call_test('2017-08-06 13:00:00')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_one_second_in_the_past(self):
        expected = 'overdue: 0 day(s) 00:01 hours'
        actual = self.call_test('2017-08-06 12:59:59')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_less_than_one_day_in_the_past(self):
        expected = 'overdue: 23:59 hours'
        actual = self.call_test('2017-08-05 13:00:01')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_more_than_one_day_in_the_past(self):
        expected = 'overdue: 1 day(s) 00:01 hours'
        actual = self.call_test('2017-08-05 12:59:59')
        self.assertEqual(expected, actual)

    def test_date_scheduled_is_not_in_odoo_default_datetime_format(self):
        with self.assertRaises(ValueError):
            self.call_test('2017/08/05 12:59:59')
