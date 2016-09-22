from .reason_count_common import ReasonCountCommon


class TestNHClinicalWardDashboardAcuteEDCount(ReasonCountCommon):
    """
    Test that the Acute hospital ED count SQL View on ward dashboard is correct
    """

    def setUp(self):
        super(TestNHClinicalWardDashboardAcuteEDCount, self).setUp()
        self.reason = 'Acute hospital ED'

    def test_returns_correct_number_of_patients(self):
        self.returns_correct_number_of_patients()

    def test_returns_correct_number_of_patients_after_change(self):
        self.returns_correct_number_after_change()

    def test_returns_no_patients_when_no_pme(self):
        self.returns_no_patients_when_no_pme()
