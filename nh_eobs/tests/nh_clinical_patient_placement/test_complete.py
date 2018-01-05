from openerp.tests.common import TransactionCase
import mock


class TestPlacementComplete(TransactionCase):
    """
    Test the complete() method of nh.clinical.patient.placement
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestPlacementComplete, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_locations()
        self.test_utils.create_users()
        self.test_utils.create_patient()
        self.test_utils.admit_patient()
        self.test_utils.create_placement()

    @mock.patch('openerp.addons.nh_eobs.helpers.refresh_views')
    def test_refresh_materialised_views(self, mock_refresh):
        """
        Test that the refresh_materialised_views() decorator is called on
        completing a placement

        :param mock_refresh: Patched out function that refreshes the
            materialised views
        """
        self.test_utils.place_patient()
        self.assertTrue(mock_refresh.called)

    @mock.patch('openerp.addons.nh_eobs.helpers.refresh_views')
    def test_refresh_ews0(self, mock_refresh):
        """
        test that the ews0 view refreshed

        :param mock_refresh: Patched out function that refreshes the
            materialised views
        """
        self.test_utils.place_patient()
        self.assertEqual(mock_refresh.call_args[0][1], ('ews0',))
