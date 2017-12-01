from openerp.tests.common import TransactionCase


class TestPrintReport(TransactionCase):
    """
    Test the print_report() method
    """

    def setUp(self):
        """
        Set up for the tests
        """
        super(TestPrintReport, self).setUp()
        self.api_model = self.env['nh.eobs.api']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()

        def patch_get_pdf(*args, **kwargs):
            if args[0]._context.get('fail_pdf'):
                return False
            return 0, True

        def patch_get_filename(*args, **kwargs):
            if args[0]._context.get('fail_name'):
                return False
            return True

        def patch_db_save(*args, **kwargs):
            if args[0]._context.get('fail_db'):
                return False
            return True

        def patch_fs_save(*args, **kwargs):
            if args[0]._context.get('fail_fs'):
                return False
            return True

        self.api_model._patch_method('get_report', patch_get_pdf)
        self.api_model._patch_method('get_filename', patch_get_filename)
        self.api_model._patch_method('add_report_to_database', patch_db_save)
        self.api_model._patch_method(
            'add_report_to_backup_location', patch_fs_save)

    def tearDown(self):
        """
        Clean up after tests
        """
        self.api_model._revert_method('get_report')
        self.api_model._revert_method('get_filename')
        self.api_model._revert_method('add_report_to_database')
        self.api_model._revert_method('add_report_to_backup_location')
        super(TestPrintReport, self).tearDown()

    def test_no_pdf(self):
        """
        Test that print_report returns False and doesn't change the
        report_printed flag if the PDF didn't print correctly
        """
        result = self.api_model\
            .with_context({'fail_pdf': True})\
            .print_report(self.test_utils.spell.id)
        self.assertFalse(result)
        self.assertFalse(self.test_utils.spell.report_printed)

    def test_no_filename(self):
        """
        Test that print_report returns False and doesn't change the
        report_printed flag if the filename cannot be created
        """
        result = self.api_model\
            .with_context({'fail_name': True})\
            .print_report(self.test_utils.spell.id)
        self.assertFalse(result)
        self.assertFalse(self.test_utils.spell.report_printed)

    def test_no_db_save(self):
        """
        Test that print_report returns False and doesn't change the
        report_printed flag if the report doesn't get saved to the DB
        """
        result = self.api_model\
            .with_context({'fail_db': True})\
            .print_report(self.test_utils.spell.id)
        self.assertFalse(result)
        self.assertFalse(self.test_utils.spell.report_printed)

    def test_no_fs_save(self):
        """
        Test that print_report returns False and doesn't change the
        report_printed flag if the report doesn't get saved to the filesystem
        """
        result = self.api_model\
            .with_context({'fail_fs': True})\
            .print_report(self.test_utils.spell.id)
        self.assertFalse(result)
        self.assertFalse(self.test_utils.spell.report_printed)

    def test_changes_flag(self):
        """
        Test that print_report returns True and changes the report_printed flag
        when the report is generated and saved to the db and filesystem
        """
        self.api_model.print_report(self.test_utils.spell.id)
        self.assertTrue(self.test_utils.spell.report_printed)
