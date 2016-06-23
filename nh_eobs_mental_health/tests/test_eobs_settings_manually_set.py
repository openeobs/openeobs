from openerp.tests.common import SingleTransactionCase


class TestEobsSettings(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestEobsSettings, cls).setUpClass()
        cls.settings_pool = cls.registry('nh.clinical.settings')
        cls.config_pool = cls.registry('nh.clinical.config.settings')
        cls.workload_pool = cls.registry('nh.clinical.settings.workload')

        def mock_settings_read(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'non_manual':
                return {
                    'manually_set': False
                }
            return {
                'manually_set': True
            }

        def mock_settings_write(*args, **kwargs):
            global writes_counter
            writes_counter += 1
            return True

        def mock_config_browse(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'wizard':
                return cls.config_pool.new(cls.cr, cls.uid, {
                    'discharge_transfer_period': 10,
                    'workload_bucket_period': [],
                    'activity_period': 600,
                })
            return mock_config_browse.origin(*args, **kwargs)

        def mock_config_read(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'wizard':
                return [{
                    'discharge_transfer_period': 10,
                    'workload_bucket_period': [1, 2, 3],
                    'activity_period': 600
                }]
            return []

        def mock_workload_read(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'wizard':
                return [
                    {'sequence': 1, 'name': '480+ minutes remain'},
                    {'sequence': 2, 'name': '241-360 minutes remain'},
                    {'sequence': 3, 'name': '121-240 minutes remain'},
                    {'sequence': 4, 'name': '0-120 minutes remain'},
                    {'sequence': 5, 'name': '1-120 minutes late'},
                    {'sequence': 6, 'name': '240+ minutes late'}
                ]

        cls.settings_pool._patch_method('read', mock_settings_read)
        cls.settings_pool._patch_method('write', mock_settings_write)
        cls.config_pool._patch_method('browse', mock_config_browse)
        cls.config_pool._patch_method('read', mock_config_read)
        cls.workload_pool._patch_method('read', mock_workload_read)

    @classmethod
    def tearDownClass(cls):
        cls.settings_pool._revert_method('read')
        cls.settings_pool._revert_method('write')
        cls.config_pool._revert_method('browse')
        cls.config_pool._revert_method('read')
        cls.workload_pool._revert_method('read')
        super(TestEobsSettings, cls).tearDownClass()

    def test_init_non_manual(self):
        """
        Test that on setting up the model and there has been no manual setting
        that the defaults are applied
        """
        global writes_counter
        writes_counter = 0
        self.settings_pool.init(self.cr, context={'test': 'non_manual'})
        self.assertEqual(writes_counter, 1)

    def test_init_manual(self):
        """
        Test that on setting up the model adn there has been manual setting
        that the defaults are not applied
        """
        global writes_counter
        writes_counter = 0
        self.settings_pool.init(self.cr, context={'test': 'manual'})
        self.assertEqual(writes_counter, 0)

    def test_set_activity_period(self):
        """
        Test that on setting up the model adn there has been manual setting
        that the defaults are not applied
        """
        global writes_counter
        writes_counter = 0
        self.config_pool.set_activity_period(
            self.cr, self.uid, 1, context={'test': 'wizard'})
        self.settings_pool.init(self.cr)
        self.assertEqual(writes_counter, 1)

    def test_set_discharge_transfer_period(self):
        """
        Test that on setting up the model adn there has been manual setting
        that the defaults are not applied
        """
        global writes_counter
        writes_counter = 0
        self.config_pool.set_discharge_transfer_period(
            self.cr, self.uid, 1, context={'test': 'wizard'})
        self.settings_pool.init(self.cr)
        self.assertEqual(writes_counter, 1)

    def test_set_workload_bucket_period(self):
        """
        Test that on setting up the model adn there has been manual setting
        that the defaults are not applied
        """
        global writes_counter
        writes_counter = 0
        self.config_pool.set_workload_bucket_period(
            self.cr, self.uid, 1, context={'test': 'wizard'})
        self.settings_pool.init(self.cr)
        self.assertEqual(writes_counter, 1)
