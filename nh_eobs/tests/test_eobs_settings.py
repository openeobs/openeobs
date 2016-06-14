from openerp.tests.common import SingleTransactionCase


class TestEobsSettings(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestEobsSettings, cls).setUpClass()
        cls.settings_pool = cls.registry('nh.clinical.settings')

    def test_default_settings(self):
        """
        Test that on creating a new settings object that the defaults are set
        to the acute defaults
        """
        cr, uid = self.cr, self.uid
        test_settings = self.settings_pool.read(
            cr, uid, self.settings_pool.create(cr, uid, {}))
        self.assertEqual(test_settings.get('activity_period'), 60)
        self.assertEqual(test_settings.get('discharge_transfer_period'), 3)
        self.assertEqual(test_settings.get('workload_bucket_period'), 15)

    def test_get_all_settings(self):
        """
        Test that the get_settings helper method returns dictionary containing
        the values
        """
        test_settings = self.settings_pool.get_settings(self.cr, self.uid, [
            'activity_period',
            'discharge_transfer_period',
            'workload_bucket_period'
        ])
        self.assertIn('activity_period', test_settings.keys())
        self.assertIn('discharge_transfer_period', test_settings.keys())
        self.assertIn('workload_bucket_period', test_settings.keys())

    def test_get_setting(self):
        """
        Test that the get_setting method will return the setting passed to it
        """
        cr, uid = self.cr, self.uid
        self.settings_pool.write(cr, uid, 1, {'activity_period': 120})
        test_setting = self.settings_pool.get_setting(cr, uid,
                                                      'activity_period')
        self.assertEqual(test_setting, 120)
