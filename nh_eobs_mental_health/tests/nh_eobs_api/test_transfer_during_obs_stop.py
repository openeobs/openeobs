from openerp.tests.common import TransactionCase


class TestTransferDuringObsStop(TransactionCase):
    """
    Test transfers that occur whilst a patient monitoring exception is active
    on the spell.
    """
    def setUp(self):
        super(TestTransferDuringObsStop, self).setUp()
        self.test_utils_model = self.env['nh.clinical.test_utils']
        self.test_utils_model.admit_and_place_patient()

        self.spell = self.test_utils_model.spell
        self.spell_activity_id = self.test_utils_model.spell_activity_id
        self.patient = self.test_utils_model.patient
        self.hospital_number = self.test_utils_model.hospital_number

        self.api_model = self.env['nh.eobs.api']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.pme_reason = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        self.activity_model = self.env['nh.activity']

        reason = self.pme_reason.browse(1)
        wardboard = self.wardboard_model.browse(self.spell.id)
        wardboard.start_obs_stop(
            reason, self.spell.id, self.spell_activity_id
        )

    def test_transfer_changes_flag(self):
        """
        Test that when transferring a patient with a set obs_stop flag the flag
        is changed
        """
        self.api_model.transfer(
            self.hospital_number,
            {
                'from_location': 'WA',
                'location': 'WB'
            }
        )
        self.assertFalse(self.spell.obs_stop, True)

    def test_transfer_ends_current_obs_stop(self):
        """
        Test that when the patient is transferred that the currently open
        Patient Monitoring Exception is cancelled
        """
        domain = [
            ('data_model', '=', 'nh.clinical.pme.obs_stop'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        self.api_model.transfer(
            self.hospital_number,
            {
                'from_location': 'WA',
                'location': 'WB'
            }
        )
        obs_activities = self.activity_model.search(domain)
        self.assertEqual(len(obs_activities), 0)

    def test_patient_refusal_after_transfer_create_obs_due_in_15_minutes(self):
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.wardboard = self.wardboard_model.new({
            'spell_activity_id': self.spell_activity_id,
            'patient_id': self.patient.id
        })
        self.wardboard.end_obs_stop()

        self.api_model.transfer(
            self.hospital_number,
            {
                'from_location': 'WA',
                'location': 'WB'
            }
        )
        self.test_utils_model.place_patient()

        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        obs_activities = self.activity_model.search(domain)
        self.assertEqual(len(obs_activities), 1)
        obs_activity = obs_activities[0]
        self.assertEqual(obs_activity.data_ref.frequency, 15)
