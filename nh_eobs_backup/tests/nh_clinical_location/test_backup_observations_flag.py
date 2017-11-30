from openerp.tests.common import TransactionCase


class TestBackupObservationsFlag(TransactionCase):
    """
    Test the backup_observations flag on the nh.clinical.location model
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestBackupObservationsFlag, self).setUp()
        self.location_model = self.env['nh.clinical.location']

    def test_backup_observations_property(self):
        """
        Test that the backup_observations flag is on the nh.clinical.locations
        model
        """
        flag_present = 'backup_observations' in self.location_model
        self.assertEqual(
            flag_present,
            True,
            'Flag not set on location class properly'
        )

    def test_backup_observations_default(self):
        """
        Test that the backup_observations flag defaults to False
        """
        flag_value = self.location_model._defaults['backup_observations']
        self.assertEqual(flag_value, False, 'Flag value not set correctly')
