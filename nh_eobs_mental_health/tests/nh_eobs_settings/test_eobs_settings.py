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
        self.assertEqual(test_settings.get('activity_period'), 360)
        self.assertEqual(test_settings.get('discharge_transfer_period'), 10)
