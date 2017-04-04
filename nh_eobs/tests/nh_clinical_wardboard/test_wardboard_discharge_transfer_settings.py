from mock import MagicMock, patch
from openerp.tests.common import SingleTransactionCase


transfer = None
discharge = None
wardboard = None


class TestWardboardDischargeTransferSettings(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWardboardDischargeTransferSettings, cls).setUpClass()
        cls.wardboard_pool = cls.registry('nh.clinical.wardboard')
        cls.settings_pool = cls.registry('nh.clinical.settings')
        cls.nh_eobs_sql = cls.registry('nh.clinical.sql')

        def mock_settings_get(*args, **kwargs):
            return 10

        def mock_transfer(*args, **kwargs):
            global transfer
            transfer = args[1]
            return ''

        def mock_discharge(*args, **kwargs):
            global discharge
            discharge = args[1]
            return ''

        def mock_wardboard(*args, **kwargs):
            global wardboard
            wardboard = args[1]
            return ''

        cls.nh_eobs_sql._patch_method('get_last_transfer_users', mock_transfer)
        cls.nh_eobs_sql._patch_method(
            'get_last_discharge_users', mock_discharge)
        cls.nh_eobs_sql._patch_method('get_wardboard', mock_wardboard)
        cls.settings_pool._patch_method('get_setting', mock_settings_get)

    @classmethod
    def tearDownClass(cls):
        cls.settings_pool._revert_method('get_setting')
        cls.nh_eobs_sql._revert_method('get_last_transfer_users')
        cls.nh_eobs_sql._revert_method('get_last_discharge_users')
        cls.nh_eobs_sql._revert_method('get_wardboard')
        super(TestWardboardDischargeTransferSettings, cls).tearDownClass()

    def test_passes_settings_value_to_sql_view_generators(self):
        """
        Test that on the getting the value from nh.clinical.settings model
        it then uses that value to create the SQL views
        """

        with patch.object(self.cr, 'execute') as mock_cursor:
            mock_cursor.execute = MagicMock()
            self.wardboard_pool.init(mock_cursor)
            self.assertEqual(transfer, '10d')
            self.assertEqual(discharge, '10d')
            self.assertEqual(wardboard, '10d')
