from openerp.tests.common import TransactionCase


class TestReportPrintedFlag(TransactionCase):
    """
    Test that the report_printed flag is set on the nh.clinical.spell model
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestReportPrintedFlag, self).setUp()
        self.spell_model = self.env['nh.clinical.spell']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.api_model = self.env['nh.eobs.api']
        self.test_utils.admit_and_place_patient()
        self.ews_data = {
            'respiration_rate': 40,
            'indirect_oxymetry_spo2': 99,
            'oxygen_administration_flag': False,
            'body_temperature': 37.0,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'pulse_rate': 55,
            'avpu_text': 'A'
        }

        def patch_add_report_to_database(*args, **kwargs):
            return True

        def patch_add_report_to_backup_location(*args, **kwargs):
            return True

        def patch_get_report(*args, **kwargs):
            return 0, True

        self.api_model._patch_method(
            'add_report_to_database',
            patch_add_report_to_database
        )
        self.api_model._patch_method(
            'add_report_to_backup_location',
            patch_add_report_to_backup_location
        )
        self.api_model._patch_method(
            'get_report',
            patch_get_report
        )

    def tearDown(self):
        """
        Clean up after test
        """
        self.api_model._revert_method('add_report_to_database')
        self.api_model._revert_method('add_report_to_backup_location')
        self.api_model._revert_method('get_report')
        super(TestReportPrintedFlag, self).tearDown()

    def test_report_printed_property(self):
        """
        Test that the report_printed flag is available on the spell
        """
        flag_present = 'report_printed' in self.spell_model
        self.assertEqual(
            flag_present,
            True,
            'Flag not set on Spell class properly'
        )

    def test_report_printed_default(self):
        """
        Test that the report_printed flag defaults to False
        """
        flag_value = self.spell_model._defaults['report_printed']
        self.assertEqual(
            flag_value,
            False,
            'Flag value not set correctly'
        )

    def test_report_printed(self):
        """
        Test that on printing the report while the report_printed flag is False
        that is sets the flag to True
        """
        self.test_utils.spell.report_printed = True
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(self.ews_data)
        self.api_model.print_report(self.test_utils.spell.id)
        self.assertTrue(self.test_utils.spell.report_printed)
