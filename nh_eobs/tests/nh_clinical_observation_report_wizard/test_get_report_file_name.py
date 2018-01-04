from openerp.tests.common import TransactionCase
from datetime import datetime


class TestGetReportFileName(TransactionCase):
    """
    Test that the method to get the filename for the printed report returns
    the name in the correct format
    """

    def setUp(self):
        """ Set up the test """
        super(TestGetReportFileName, self).setUp()
        self.datetime_utils = self.env['datetime_utils']
        self.report_wizard_model = \
            self.env['nh.clinical.observation_report_wizard']

        def patch_get_current_time(*args, **kwargs):
            return datetime(1988, 1, 12, 23, 0, 0)

        self.datetime_utils._patch_method(
            'get_current_time',
            patch_get_current_time
        )
        self.report = self.report_wizard_model.create(
            {
                'start_time': None,
                'end_time': None
            }
        )
        self.filename = self.report.get_filename('666')

    def tearDown(self):
        """ Remove any patches setup for the test """
        self.datetime_utils._revert_method('get_current_time')
        super(TestGetReportFileName, self).tearDown()

    def test_patient_identifier(self):
        """
        Test that the supplied patient identifier is in the returned filename
        """
        self.assertEqual(
            self.filename.split('_')[0],
            '666'
        )

    def test_date_printed(self):
        """
        Test that the localised date of when the report was printed is in
        the returned filename
        """
        self.assertEqual(
            self.filename.split('_')[1],
            '19880112'
        )

    def test_date_is_localised(self):
        """
        Test that the returned date for the report is in the YYYYMMDD format
        """
        self.assertEqual(
            self.report
                .with_context({'tz': 'Etc/GMT-12'})
                .get_filename('666'),
            '666_19880113_observation_report.pdf'
        )

    def test_no_patient_identifier(self):
        """
        Test that an exception is raised if no patient identifier is passed to
        the method
        """
        with self.assertRaises(TypeError):
            self.report.get_filename()
