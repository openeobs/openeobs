from openerp.tests.common import TransactionCase


class TestProcessPeriodDatetimes(TransactionCase):
    """
    Test that process_period_datetimes is returning datetimes in the period
    dictionary correctly
    """

    def setUp(self):
        super(TestProcessPeriodDatetimes, self).setUp()
        review_model = \
            self.env['nh.clinical.notification.food_fluid_review']
        period = {
            'period_start_datetime': '1988-01-12 07:00:00',
            'period_end_datetime': '1988-01-13 07:00:00',
        }
        self.period = review_model.process_period_datetimes(period)

    def test_converts_start_datetime(self):
        """
        Test that converts start datetime correctly
        """
        self.assertEqual(self.period.get('period_start_datetime'), '7am 12/01')

    def test_converts_end_datetime(self):
        """
        Test that converts end datetime correctly
        """
        self.assertEqual(self.period.get('period_end_datetime'), '7am 13/01')
