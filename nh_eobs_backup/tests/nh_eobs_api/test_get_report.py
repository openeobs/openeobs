from openerp.tests.common import TransactionCase
from openerp.osv import osv


class TestGetReport(TransactionCase):
    """
    Test the method that renders the HTMl and creates a PDF from it
    """

    printing_error = False
    report_args = []

    def setUp(self):
        """
        Set up the tests
        """
        super(TestGetReport, self).setUp()
        self.printing_error = False
        self.report_args = []
        self.api_model = self.env['nh.eobs.api']
        self.report_model = self.env['report']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.obs_wizard = self.env['nh.clinical.observation_report_wizard']
        self.test_utils.admit_and_place_patient()

        def mock_get_pdf(*args, **kwargs):
            """
            Mock get_pdf so can ensure correct args are passed

            :param args: Arguments passed to function
            :param kwargs: Keyword arguments passed to function
            :return: Original function call
            """
            self.report_args = args
            return mock_get_pdf.origin(*args, **kwargs)

        def patch_run_wkhtmltopdf(*args, **kwargs):
            """
            Patch out the Odoo method that handles the printing of the PDF via
            the WKHTMLtoPDF binary. We have to use self.printing_error instead
            of reading the context as Odoo's code doesn't pass a context dict
            to this method

            :param args: Args for method
            :param kwargs: Kwargs for method
            :return: origin or raise exception as needed
            """
            if self.printing_error:
                raise osv.except_osv(
                    'Report (PDF)',
                    'Wkhtmltopdf failed (error code: -11). Message:'
                )
            return '%PDF-1.4'

        self.report_model._patch_method(
            '_run_wkhtmltopdf', patch_run_wkhtmltopdf)

        self.report_model._patch_method(
            'get_pdf', mock_get_pdf
        )

    def tearDown(self):
        """
        Clear up after testing
        """
        self.report_model._revert_method('_run_wkhtmltopdf')
        self.report_model._revert_method('get_pdf')
        super(TestGetReport, self).tearDown()

    def test_no_spell_id(self):
        """
        Test that returns False is no spell_id passed
        """
        self.assertFalse(self.api_model.get_report())

    def test_wizard_id(self):
        """
        Test that returns the ID for the wizard as well as the PDF (needed for
        use in print_report)
        """
        result = self.api_model.get_report(self.test_utils.spell.id)
        wizard_count = self.obs_wizard.search([]).id
        self.assertEqual(result[0].id, wizard_count)

    def test_no_pdf(self):
        """
        Test that if an exception is raised when trying to convert to PDF (due
        to WKHTMLtoPDF error etc) then it returns False
        """
        self.printing_error = True
        result = self.api_model.get_report(self.test_utils.spell.id)
        self.assertFalse(result)

    def test_calls_get_pdf(self):
        """
        Test that a call to report.get_pdf is made by get_report with the
        correct arguments
        """
        result = self.api_model.get_report(self.test_utils.spell.id)
        self.assertEqual(
            self.report_args[3],
            [result[0].id]
        )
        self.assertEqual(
            self.report_args[4],
            'nh.clinical.observation_report'
        )

