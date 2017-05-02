from openerp.tests.common import TransactionCase


class TestActiveFoodFluidPeriod(TransactionCase):
    """
    Test that the active Food & Fluid Period is calculated
    """

    def test_second_before_period(self):
        """
        Test that period is not active if last obs was at 06:59:59 that morning
        """
        self.assertTrue(False)

    def test_second_into_period(self):
        """
        Test that period is active if last obs was at 07:00:00 that morning
        """
        self.assertTrue(False)

    def test_second_after_period(self):
        """
        Test that period is not active if last obs was at 07:00:00 the next
        morning
        """
        self.assertTrue(False)

    def test_second_before_period_end(self):
        """
        Test that period is active if last obs was at 06:59:59 the next
        morning
        """
        self.assertTrue(False)

    def test_no_observations_in_period(self):
        """
        Test that period is not active if no observations of any type were
        recorded during that period
        """
        self.assertTrue(False)

    def test_other_observation_in_period(self):
        """
        Test that period is not active if observations of other types but
        no food and fluid observations were recorded during that period
        """
        self.assertTrue(False)
