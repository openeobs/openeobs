from openerp.tests.common import TransactionCase


class TestWorkloadBucketSettings(TransactionCase):

    def setUp(self):
        super(TestWorkloadBucketSettings, self).setUp()
        self.settings_pool = self.registry('nh.clinical.settings')
        self.wizard_pool = self.registry('nh.clinical.config.settings')
        self.workload_pool = self.registry('nh.clinical.settings.workload')

        def mock_wizard_read(*args, **kwargs):
            context = kwargs.get('context')
            test = context.get('test') if context else False
            if test and test in ['workload_valid', 'workload_invalid',
                                 'workload_sql']:
                return [{'workload_bucket_period': [1]}]
            else:
                return [{'workload_bucket_period': []}]

        def mock_workload_read(*args, **kwargs):
            context = kwargs.get('context')
            test = context.get('test') if context else False
            if test:
                remain_47 = {'name': '47+ minutes remain'}
                late_16 = {'name': '16+ minutes late'}
                if test in ['workload_valid', 'workload_sql']:
                    return [remain_47, late_16]
                elif test == 'workload_invalid':
                    bad = {'name': 'This will fail the test'}
                    return [remain_47, bad, late_16]
                elif test == 'workload_empty':
                    return []
            else:
                return mock_wizard_read.origin(*args, **kwargs)

        def mock_settings_write(*args, **kwargs):
            context = kwargs.get('context')
            test = context.get('test') if context else False
            if test and test == 'workload_valid':
                global wizard_write_called
                wizard_write_called = True
            if test and test == 'workload_empty':
                global wizard_write_empty
                wizard_write_empty = True
            return True

        def mock_sql_refresh(*args, **kwargs):
            context = kwargs.get('context')
            test = context.get('test') if context else False
            if test and test == 'workload_sql':
                global sql_called
                sql_called = True
            return True

        self.wizard_pool._patch_method('read', mock_wizard_read)
        self.workload_pool._patch_method('read', mock_workload_read)
        self.settings_pool._patch_method('write', mock_settings_write)
        self.wizard_pool._patch_method('refresh_workload_view',
                                       mock_sql_refresh)

    def tearDown(self):
        self.wizard_pool._revert_method('read')
        self.settings_pool._revert_method('write')
        self.workload_pool._revert_method('read')
        self.wizard_pool._revert_method('refresh_workload_view')
        super(TestWorkloadBucketSettings, self).tearDown()

    def test_workload_case_validator_raises_single(self):
        """
        Test that workload case validator takes an array of values and if
        there's invalid options then should raise an exception
        """
        test_data = ['a', '16-24']
        invalid = self.settings_pool.validate_workload_buckets(test_data)
        self.assertEqual(invalid, 'Time period in position 1 is invalid')

    def test_workload_case_validator_raises_multi(self):
        """
        Test that workload case validator takes an array of values and if
        there's invalid options then should raise an exception
        """
        test_data = ['a', '16-24 minutes late', '7',
                     '16+ minutes late', '12- minutes remain']
        invalid = self.settings_pool.validate_workload_buckets(test_data)
        self.assertEqual(invalid,
                         'Time periods in positions 1 and 3 are invalid')

    def test_workload_case_validator_valid(self):
        """
        Test returns True when valid
        """
        test_data = ['12-35 minutes late']
        self.assertTrue(
            self.settings_pool.validate_workload_buckets(test_data))

    def test_set_workload_bucket_raises(self):
        """
        Test that on setting an invalid bucket it raises an exception
        """
        with self.assertRaises(ValueError) as bucket_err:
            self.wizard_pool.set_workload_bucket_period(
                self.cr, self.uid, 1, context={'test': 'workload_invalid'})
        self.assertEqual(bucket_err.exception.message,
                         'Time period in position 2 is invalid')

    def test_set_workload_bucket_valid(self):
        """
        Test that on setting an valid bucket it writes to settings
        """
        self.wizard_pool.set_workload_bucket_period(
            self.cr, self.uid, 1, context={'test': 'workload_valid'})
        self.assertTrue(wizard_write_called)

    def test_set_workload_bucket_empty(self):
        """
        Test that on setting an valid bucket it writes to settings
        """
        self.wizard_pool.set_workload_bucket_period(
            self.cr, self.uid, 1, context={'test': 'workload_empty'})
        self.assertTrue(wizard_write_empty)

    def test_set_workload_bucket_refresh_sql(self):
        """
        Test that on setting values for the buckets that it refreshes the SQL
        view with the new values
        """
        self.wizard_pool.set_workload_bucket_period(
            self.cr, self.uid, 1, context={'test': 'workload_sql'})
        self.assertTrue(sql_called)
