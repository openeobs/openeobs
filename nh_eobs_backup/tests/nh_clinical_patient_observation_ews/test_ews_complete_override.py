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

    def test_observation_complete(self):
        """
        Test that report_printed flag is changed when a new EWS observation is
        completed
        """
        self.test_utils.spell.report_printed = True
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(self.ews_data)
        self.assertFalse(self.test_utils.spell.report_printed)
