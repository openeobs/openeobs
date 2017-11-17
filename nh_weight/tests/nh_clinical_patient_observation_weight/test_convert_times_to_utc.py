from openerp.tests.common import TransactionCase
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import pytz


class TestConvertTimesToUTC(TransactionCase):
    """
    Test that .convert_times_to_utc() method of the
    nh.clinical.observation.weight model
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestConvertTimesToUTC, self).setUp()
        self.weight_model = self.env['nh.clinical.patient.observation.weight']

    def test_changes_to_utc(self):
        """
        Test that when given a list of dates and the user is in
        """
        times = [
            datetime(2017, 6, 6, 12, 0, 0, tzinfo=pytz.timezone('Etc/GMT+1'))
        ]
        converted_times = self.weight_model.convert_times_to_utc(times)
        self.assertEqual(
            '2017-06-06 11:00:00',
            converted_times[0].strftime(DTF)
        )
