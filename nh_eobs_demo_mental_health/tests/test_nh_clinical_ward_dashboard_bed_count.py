from .location_patient_count_common import LocationPatientCountCommon


class TestNHClinicalWardDashboardBedCount(LocationPatientCountCommon):
    """
    Test that the patients on ward SQL View on ward dashboard is correct
    """

    def setUp(self):
        super(TestNHClinicalWardDashboardBedCount, self).setUp()
        self.table = 'bed'

    def test_returns_correct_number_of_locations(self):
        """
        Test that 30 beds in ward A
        """
        self.returns_correct_number_of_patients(30)
