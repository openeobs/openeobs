from openerp.tests.common import SingleTransactionCase


class TestWardDashboard(SingleTransactionCase):
    """
    Test that the ward dashboard has the correct columns with the correct
    value
    """

    def setUp(self):
        super(TestWardDashboard, self).setUp()
        cr, uid = self.cr, self.uid
        ward_dashboard_model = self.registry('nh.eobs.ward.dashboard')
        location_model = self.registry('nh.clinical.location')
        ward_a = location_model.search(
            cr, uid, [['code', '=', 'A']])[0]
        self.ward_dashboard = ward_dashboard_model.read(cr, uid, ward_a)

    def test_has_acute_ed_count(self):
        """ Check that has 1 Acute hospital ED PME patient """
        self.assertEqual(self.ward_dashboard.get('acute_hospital_ed_count'), 1)

    def test_has_awol_count(self):
        """ Check that has 1 AWOL PME patient """
        self.assertEqual(self.ward_dashboard.get('awol_count'), 1)

    def test_has_capacity_count(self):
        """ Check that has -10 capacity """
        self.assertEqual(self.ward_dashboard.get('capacity_count'), -10)

    def test_has_extended_leave_count(self):
        """ Check that has 1 extended leave PME patient """
        self.assertEqual(self.ward_dashboard.get('extended_leave_count'), 1)

    def test_has_on_ward_count(self):
        """ Check that has 25 patients on ward """
        self.assertEqual(self.ward_dashboard.get('on_ward_count'), 25)

    def test_has_workload_count(self):
        """ Check has 40 patients as workload """
        self.assertEqual(self.ward_dashboard.get('workload_count'), 40)
