from openerp.tests.common import TransactionCase
from pyfakefs.fake_filesystem_unittest import Patcher
import os


class TestAddReportToBackupLocation(TransactionCase):
    """
    Test adding the printed report to the backup location
    """

    def setUp(self):
        """
        Set up tests
        """
        super(TestAddReportToBackupLocation, self).setUp()
        self.patcher = Patcher()
        self.patcher.setUp()
        self.api_model = self.env['nh.eobs.api']

    def tearDown(self):
        """
        Clean up after tests
        """
        self.patcher.tearDown()
        super(TestAddReportToBackupLocation, self).tearDown()

    def test_creates_directory(self):
        """
        Test that if the directory to back up into isn't already there then it
        creates it
        """
        self.api_model.add_report_to_backup_location(
            '/bcp/out',
            'data_to_write_to_file',
            'test_filename'
        )
        self.assertTrue(os.path.isdir('/bcp/out'))

    def test_unable_to_create_dir(self):
        """
        Test that when creating the directory (due to not already existing)
        and there's an OSError (due to permission issues) that it catches the
        exception and returns False
        """
        self.patcher.fs.CreateDirectory('/bcp', perm_bits=0o555)
        result = self.api_model.add_report_to_backup_location(
            '/bcp/out',
            'data_to_write_to_file',
            'test_filename'
        )
        self.assertFalse(result)

    def test_writes_file_to_dir(self):
        """
        Test that when the directory exists that it creates a file with the
        filename in said directory
        """
        self.patcher.fs.CreateDirectory('/bcp/out')
        self.api_model.add_report_to_backup_location(
            '/bcp/out',
            'data_to_write_to_file',
            'test_filename'
        )
        self.assertTrue(os.path.exists('/bcp/out/test_filename.pdf'))

    def test_overwrites_file(self):
        """
        Test that the file writing operation is idempotent
        """
        self.patcher.fs.CreateDirectory('/bcp/out')
        self.api_model.add_report_to_backup_location(
            '/bcp/out',
            'data_to_write_to_file',
            'test_filename'
        )
        self.assertTrue(os.path.exists('/bcp/out/test_filename.pdf'))
        result = self.api_model.add_report_to_backup_location(
            '/bcp/out',
            'data_to_write_to_file',
            'test_filename'
        )
        self.assertTrue(result)

    def test_file_content(self):
        """
        Test that the file content that's written isn't changed in anyway
        """
        self.patcher.fs.CreateDirectory('/bcp/out')
        self.api_model.add_report_to_backup_location(
            '/bcp/out',
            'data_to_write_to_file',
            'test_filename'
        )
        with open('/bcp/out/test_filename.pdf', 'r') as report_file:
            file_content = report_file.read()
            self.assertEqual(
                file_content,
                'data_to_write_to_file'
            )
