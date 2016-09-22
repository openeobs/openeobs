from .reason_count_common import ReasonCountCommon


class TestNHClinicalWardDashboardOnWardCount(ReasonCountCommon):
    """
    Test that the obs stop count SQL View on ward dashboard is correct
    """

    def setUp(self):
        super(TestNHClinicalWardDashboardOnWardCount, self).setUp()
        self.reason = 'on ward'

    def get_reason_id(self):
        reason_model = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        return reason_model.search([
            ['display_text', '=', 'AWOL']
        ]).id

    def test_returns_correct_number_of_patients(self):
        self.returns_correct_number_of_patients(count=25)

    def test_returns_correct_number_of_patients_after_change(self):
        self.returns_correct_number_after_change(count=24)

    def test_returns_correct_number_of_patients_when_no_pme(self):
        self.returns_correct_number_of_patients_when_no_pme(count=28)
