from .reason_count_common import ReasonCountCommon


class TestAWOLCount(ReasonCountCommon):
    """
    Test that the AWOL count SQL View on ward dashboard is correct
    """

    def setUp(self):
        super(TestAWOLCount, self).setUp()
        self.reason = 'AWOL'

    def test_returns_correct_number_of_patients(self):
        self.returns_correct_number_of_patients()

    def test_returns_correct_number_of_patients_after_change(self):
        self.returns_correct_number_after_change()

    def test_returns_no_patients_when_no_pme(self):
        self.returns_no_patients_when_no_pme()
