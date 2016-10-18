from openerp.tests.common import SingleTransactionCase


class TestPatientBoard(SingleTransactionCase):
    """
    Test that the override of the patient_board method on nh.eob.ward_dashboard
    is returning the correct search filter by default
    """

    def setUp(self):
        super(TestPatientBoard, self).setUp()
        dashboard_model = self.env['nh.eobs.ward.dashboard']
        self.dashboard = dashboard_model.browse(0)

    def test_acuity_index_is_default(self):
        """
        Make sure that the acuity_index search filter is the default search
        filter
        """
        patient_board = self.dashboard.patient_board()
        context = patient_board.get('context', {})
        self.assertTrue('search_default_acuity_index' in context)
        self.assertEqual(context.get('search_default_acuity_index'), 1)

    def test_clinical_risk_absent(self):
        """
        Make sure that the old clinical_risk search filter is no longer used
        """
        patient_board = self.dashboard.patient_board()
        self.assertFalse(
            'search_default_clinical_risk' in patient_board.get('context'))
