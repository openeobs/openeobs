from openerp.tests.common import SingleTransactionCase
from .. import sql_statements as nh_eobs_sql
from mock import MagicMock, patch


class TestWardboardDischargeTransferSettings(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWardboardDischargeTransferSettings, cls).setUpClass()
        cls.wardboard_pool = cls.registry('nh.clinical.wardboard')
        cls.settings_pool = cls.registry('nh.clinical.settings')

        def mock_settings_get(*args, **kwargs):
            return 10

        cls.settings_pool._patch_method('get_setting', mock_settings_get)

    @classmethod
    def tearDownClass(cls):
        cls.settings_pool._revert_method('get_setting')
        super(TestWardboardDischargeTransferSettings, cls).tearDownClass()

    @patch.object(nh_eobs_sql, 'get_last_transfer_users', MagicMock())
    @patch.object(nh_eobs_sql, 'get_last_discharge_users', MagicMock())
    @patch.object(nh_eobs_sql, 'get_wardboard', MagicMock())
    def test_passes_settings_value_to_sql_view_generators(self):
        """
        Test that on the getting the value from nh.clinical.settings model
        it then uses that value to create the SQL views
        """
        with patch.object(self.cr, 'execute') as mock_cursor:
            mock_cursor.execute = MagicMock()
            self.wardboard_pool.init(mock_cursor)
            nh_eobs_sql.get_last_transfer_users.assert_called_with('10d')
            nh_eobs_sql.get_last_discharge_users.assert_called_with('10d')
            nh_eobs_sql.get_wardboard.assert_called_with('10d')
