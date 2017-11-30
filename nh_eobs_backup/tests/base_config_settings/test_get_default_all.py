from openerp.tests.common import TransactionCase


class TestGetDefaultAll(TransactionCase):
    """
    Test the setting of the locations to backup via the settings wizard
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestGetDefaultAll, self).setUp()
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
        :return: Locations
        """
        record = self.settings_model.create(
            {
                'locations_to_print': [[6, 0, ids]]
            }
        )
        record.set_locations()
        return self.settings_model.get_default_all().get('locations_to_print')

    def test_setting_ward(self):
        """
        Test setting a single location
        """
        self.assertEqual(
            self.change_locations([self.ward.id]),
            [self.ward.id]
        )

    def test_setting_wards(self):
        """
        Test setting multiple locations
        """
        ids = [self.ward.id, self.other_ward.id]
        self.assertEqual(
            self.change_locations(ids),
            ids
        )

    def test_setting_bed(self):
        """
        Test that including a bed in the locations doesn't result in the bed
        being included
        """
        ids = [self.ward.id, self.other_ward.id, self.bed.id]
        self.assertEqual(
            self.change_locations(ids),
            ids[:2]
        )

    def test_setting_hospital(self):
        """
        Test that including a hospital in the locations doesn't result in the
        hospital being included
        """
        ids = [self.ward.id, self.other_ward.id, self.hospital.id]
        self.assertEqual(
            self.change_locations(ids),
            ids[:2]
        )

    def test_clearing_location(self):
        """
        Test removing a single location when many are set
        """
        initial_ids = [self.ward.id, self.other_ward.id]
        new_ids = [self.ward.id]
        self.change_locations(initial_ids)
        self.assertEqual(
            self.change_locations(new_ids),
            new_ids
        )

    def test_clearing_all(self):
        """
        Test removing all locations
        """
        initial_ids = [self.ward.id, self.other_ward.id]
        self.change_locations(initial_ids)
        self.assertEqual(
            self.change_locations([]),
            []
        )
