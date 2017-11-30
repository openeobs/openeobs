from openerp.tests.common import TransactionCase


class TestSetLocations(TransactionCase):
    """
    Test the setting of the locations to backup via the settings wizard
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestSetLocations, self).setUp()
        self.settings_model = self.env['base.config.settings']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_locations()
        self.hospital = self.test_utils.hospital
        self.ward = self.test_utils.ward
        self.bed = self.test_utils.bed
        self.other_ward = self.test_utils.create_location(
            'ward', self.hospital.id)

    def change_locations(self, ids):
        """
        Helper method to set the locations

        :param ids: ID of locations to set
        """
        record = self.settings_model.create(
            {
                'locations_to_print': [[6, 0, ids]]
            }
        )
        record.set_locations()

    def test_setting_ward(self):
        """
        Test setting a single location
        """
        self.change_locations([self.ward.id])
        self.assertTrue(self.ward.backup_observations)

    def test_setting_wards(self):
        """
        Test setting multiple locations
        """
        self.change_locations([self.ward.id, self.other_ward.id])
        self.assertTrue(self.ward.backup_observations)
        self.assertTrue(self.other_ward.backup_observations)

    def test_setting_bed(self):
        """
        Test that including a bed in the locations doesn't result in the bed
        being included
        """
        self.change_locations([self.ward.id, self.other_ward.id, self.bed.id])
        self.assertTrue(self.ward.backup_observations)
        self.assertTrue(self.other_ward.backup_observations)
        self.assertFalse(self.bed.backup_observations)

    def test_setting_hospital(self):
        """
        Test that including a hospital in the locations doesn't result in the
        hospital being included
        """
        self.change_locations(
            [self.ward.id, self.other_ward.id, self.hospital.id])
        self.assertTrue(self.ward.backup_observations)
        self.assertTrue(self.other_ward.backup_observations)
        self.assertFalse(self.hospital.backup_observations)

    def test_clearing_location(self):
        """
        Test removing a single location when many are set
        """
        initial_ids = [self.ward.id, self.other_ward.id]
        new_ids = [self.ward.id]
        self.change_locations(initial_ids)
        self.change_locations(new_ids)
        self.assertTrue(self.ward.backup_observations)
        self.assertFalse(self.other_ward.backup_observations)

    def test_clearing_all(self):
        """
        Test removing all locations
        """
        initial_ids = [self.ward.id, self.other_ward.id]
        self.change_locations(initial_ids)
        self.change_locations([])
        self.assertFalse(self.ward.backup_observations)
        self.assertFalse(self.other_ward.backup_observations)
