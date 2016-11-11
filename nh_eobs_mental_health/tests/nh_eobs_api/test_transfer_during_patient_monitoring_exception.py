from openerp.addons.nh_eobs.tests.common import test_data_creator_transfer
from openerp.tests.common import TransactionCase


class TestTransferDuringPatientMonitoringException(TransactionCase):
    """
    Test transfers that occur whilst a patient monitoring exception is active
    on the spell.
    """
    def setUp(self):
        super(TestTransferDuringPatientMonitoringException, self).setUp()
        test_data_creator_transfer.admit_and_place_patient(self)

        self.pme_reason = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        reason = self.pme_reason.browse(1)
        wardboard = self.wardboard_model.browse(self.spell.id)
        wardboard.start_patient_monitoring_exception(
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

    def test_transfer_ends_current_patient_monitoring_exception(self):
        """
        Test that when the patient is transferred that the currently open
        Patient Monitoring Exception is cancelled
        """
        domain = [
            ('data_model', '=', 'nh.clinical.patient_monitoring_exception'),
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
            'patient_id': self.patient_id
        })
        self.wardboard.end_patient_monitoring_exception()

        self.api_model.transfer(
            self.hospital_number,
            {
                'from_location': 'WA',
                'location': 'WB'
            }
        )
        test_data_creator_transfer.place_patient(self)

        domain = [
            ('data_model', '=', 'nh.clinical.patient.observation.ews'),
            ('spell_activity_id', '=', self.spell_activity_id),
            ('state', 'not in', ['completed', 'cancelled'])
        ]
        obs_activities = self.activity_model.search(domain)
        self.assertEqual(len(obs_activities), 1)
        obs_activity = obs_activities[0]
        self.assertEqual(obs_activity.data_ref.frequency, 15)
