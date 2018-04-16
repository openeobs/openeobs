from openerp.tests.common import SingleTransactionCase


class TestGetEwsTrend(SingleTransactionCase):

    def setUp(self):
        self.patient_model = self.env['nh.clinical.patient']

    def test_last_ews_score_is_less_than_the_one_before(self):
        expected = 'down'
        actual = self.patient_model.get_ews_trend(1, 2)
        self.assertEqual(expected, actual)

    def test_last_ews_score_is_equal_to_the_one_before(self):
        expected = 'same'
        actual = self.patient_model.get_ews_trend(1, 1)
        self.assertEqual(expected, actual)

    def test_last_ews_score_is_greater_than_the_one_before(self):
        expected = 'up'
        actual = self.patient_model.get_ews_trend(2, 1)
        self.assertEqual(expected, actual)

    def test_last_ews_score_is_none(self):
        expected = 'no latest'
        actual = self.patient_model.get_ews_trend(None, 2)
        self.assertEqual(expected, actual)

    def test_ews_score_before_last_is_none(self):
        expected = 'first'
        actual = self.patient_model.get_ews_trend(1, None)
        self.assertEqual(expected, actual)

    def test_both_last_ews_score_and_one_before_are_none(self):
        expected = 'none'
        actual = self.patient_model.get_ews_trend(None, None)
        self.assertEqual(expected, actual)
