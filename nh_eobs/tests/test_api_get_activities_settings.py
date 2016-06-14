from openerp.tests.common import SingleTransactionCase
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class TestApiGetActivitiesSettings(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestApiGetActivitiesSettings, cls).setUpClass()
        cls.api_pool = cls.registry('nh.eobs.api')
        cls.settings_pool = cls.registry('nh.clinical.settings')
        cls.activity_pool = cls.registry('nh.activity')

        def mock_settings_get(*args, **kwargs):
            return 120

        def mock_activity_search(*args, **kwargs):
            context = kwargs.get('context')
            if context and context.get('test') == 'domain_test':
                global search_domain
                search_domain = args[3]
            return []

        cls.settings_pool._patch_method('get_setting', mock_settings_get)
        cls.activity_pool._patch_method('search', mock_activity_search)

    @classmethod
    def tearDownClass(cls):
        cls.settings_pool._revert_method('get_setting')
        cls.activity_pool._revert_method('search')
        super(TestApiGetActivitiesSettings, cls).tearDownClass()

    def test_passes_settings_value_to_domain(self):
        """
        Test that on the getting the value from nh.clinical.settings model
        it then creates a date and passes this to the search domain
        """
        test_time = datetime.now() + timedelta(minutes=120)
        self.api_pool.get_activities(self.cr, self.uid, [],
                                     context={'test': 'domain_test'})
        self.assertEqual(search_domain, [
            ('state', 'not in', ['completed', 'cancelled']), '|',
            ('date_scheduled', '<=', test_time.strftime(DTF)),
            ('date_deadline', '<=', test_time.strftime(DTF)),
            ('user_ids', 'in', [self.uid]),
            '|', ('user_id', '=', False), ('user_id', '=', self.uid)
        ])
