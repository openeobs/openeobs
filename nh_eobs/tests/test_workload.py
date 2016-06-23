# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import logging
from mock import MagicMock, patch

from openerp.tests.common import SingleTransactionCase

_logger = logging.getLogger(__name__)


class TestWorkload(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestWorkload, cls).setUpClass()
        cls.settings_pool = cls.registry('nh.clinical.settings')
        cls.workload_pool = cls.registry('nh.activity.workload')
        cls.workload_settings = cls.registry('nh.clinical.settings.workload')
        cls.sql_pool = cls.registry('nh.clinical.sql')

        def mock_settings_read(*args, **kwargs):
            return {
                'workload_bucket_period': [1]
            }

        def mock_workload_read(*args, **kwargs):
            return [
                {'sequence': 1, 'name': '46+ minutes remain'},
                {'sequence': 2, 'name': '45-31 minutes remain'},
                {'sequence': 3, 'name': '30-16 minutes remain'},
                {'sequence': 4, 'name': '15-0 minutes remain'},
                {'sequence': 5, 'name': '1-15 minutes late'},
                {'sequence': 6, 'name': '16+ minutes late'}
            ]

        def mock_get_setting(*args, **kwargs):
            return [1]

        cls.settings_pool._patch_method('read', mock_settings_read)
        cls.workload_settings._patch_method('read', mock_workload_read)
        cls.settings_pool._patch_method('get_setting', mock_get_setting)

    @classmethod
    def tearDownClass(cls):
        cls.settings_pool._revert_method('read')
        cls.workload_settings._revert_method('read')
        cls.settings_pool._revert_method('get_setting')
        super(TestWorkload, cls).tearDownClass()

    def test_get_groups(self):
        cr, uid = self.cr, self.uid

        res, fold = self.workload_pool._get_groups(cr, uid, [], [])
        groups = [
            (1, '46+ minutes remain'),
            (2, '45-31 minutes remain'),
            (3, '30-16 minutes remain'),
            (4, '15-0 minutes remain'),
            (5, '1-15 minutes late'),
            (6, '16+ minutes late')
        ]
        groups.reverse()
        self.assertListEqual(res, groups)
        self.assertDictEqual(fold, {g[0]: False for g in groups})

    def test_init(self):
        buckets = self.workload_settings.read()
        view = self.sql_pool.get_workload(buckets)
        with patch.object(self.cr, 'execute') as mock_cursor:
            mock_cursor.execute = MagicMock()
            self.workload_pool.init(mock_cursor)
            mock_cursor.execute.assert_called_with(
                """create or replace view {table} as ({workload})""".format(
                    table='nh_activity_workload', workload=view))
