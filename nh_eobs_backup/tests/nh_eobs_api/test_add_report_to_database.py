from openerp.tests.common import TransactionCase
from openerp.exceptions import AccessError
import base64


class TestAddReportToDatabase(TransactionCase):
    """
    Test adding the printed report into the ir.attachment table of the database
    as a base64 string
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestAddReportToDatabase, self).setUp()
        self.api_model = self.env['nh.eobs.api']
        self.attachment_model = self.env['ir.attachment']
        self.name = 'test_report'
        self.report_content = 'report_as_pdf_string'
        self.report_filename = 'test_report_filename.pdf'
        self.report_model = 'nh.clinical.observation_report_wizard'
        self.report_id = 1

        def patch_create(*args, **kwargs):
            if kwargs.get('context'):
                if kwargs.get('context').get('fail'):
                    raise AccessError('Oops')
            return patch_create.origin(*args, **kwargs)

        self.attachment_model._patch_method('create', patch_create)

    def tearDown(self):
        """
        Clean up after tests
        """
        self.attachment_model._revert_method('create')
        super(TestAddReportToDatabase, self).tearDown()

    def add_report_to_db(self):
        """
        Helper method to add report to database

        :return: Attachment record
        """
        attachment_id = self.api_model.add_report_to_database(
            self.name,
            self.report_content,
            self.report_filename,
            self.report_model,
            self.report_id
        )
        return self.attachment_model.browse(attachment_id)

    def test_saves_attachment_name(self):
        """
        Test that the attachment is saved and the ID of the new attachment
        is returned
        """
        saved_report = self.add_report_to_db()
        self.assertEqual(
            saved_report.name,
            self.name
        )

    def test_saves_attachment_content(self):
        """
        Test that the attachment is saved and the ID of the new attachment
        is returned
        """
        saved_report = self.add_report_to_db()
        self.assertEqual(
            saved_report.datas,
            base64.encodestring(self.report_content)
        )

    def test_saves_attachment_filename(self):
        """
        Test that the attachment is saved and the ID of the new attachment
        is returned
        """
        saved_report = self.add_report_to_db()
        self.assertEqual(
            saved_report.datas_fname,
            self.report_filename
        )

    def test_saves_attachment_model(self):
        """
        Test that the attachment is saved and the ID of the new attachment
        is returned
        """
        saved_report = self.add_report_to_db()
        self.assertEqual(
            saved_report.res_model,
            self.report_model
        )

    def test_saves_attachment_id(self):
        """
        Test that the attachment is saved and the ID of the new attachment
        is returned
        """
        saved_report = self.add_report_to_db()
        self.assertEqual(
            saved_report.res_id,
            self.report_id
        )

    def test_unable_to_save(self):
        """
        Test that if an AccessError is raised that no attachment ID is returned
        """
        self.assertIsNone(
            self.api_model
            .with_context({'fail': True})
            .add_report_to_database(
                self.name,
                self.report_content,
                self.report_filename,
                self.report_model,
                self.report_id
            )
        )
