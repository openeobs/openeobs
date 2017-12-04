from openerp.tests.common import TransactionCase


class TestEwsCompleteOverride(TransactionCase):
    """
    Test the complete() override on the nh.clinical.patient.observation.ews
    model
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestEwsCompleteOverride, self).setUp()
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
        super(TestEwsCompleteOverride, self).tearDown()

    def test_observation_complete(self):
        """
        Test that report_printed flag is changed when a new EWS observation is
        completed
        """
        self.test_utils.spell.report_printed = True
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(self.ews_data)
        self.assertFalse(self.test_utils.spell.report_printed)
