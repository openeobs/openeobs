from openerp.addons.nh_eobs_mental_health\
    .tests.common.transaction_observation import TransactionObservationCase
from openerp.addons.nh_ews.tests.common.clinical_risk_sample_data import \
    REFUSED_DATA, LOW_RISK_DATA, PARTIAL_DATA
import time


class TestRefusedObsCount(TransactionObservationCase):
    """
    Test that the refused obs count SQL View on ward dashboard is correct
    """

    def setUp(self):
        super(TestRefusedObsCount, self).setUp()
        self.spell_model = self.env['nh.clinical.spell']

    def complete_observation(self, nurse, patient_ids, observation_values):
        """
        Complete the open EWS observations with the supplied values for the
        patient ids supplied
        :param patient_ids: ID of patient records
        :param observation_values: Dictionary of EWS values
        """
        cr, uid = self.cr, self.uid
        activity_model = self.registry('nh.activity')
        api_model = self.registry('nh.eobs.api')
        ews_activity_ids = activity_model.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.patient.observation.ews'],
            ['state', 'not in', ['completed', 'cancelled']],
            ['patient_id', 'in', patient_ids]
        ])
        for ews_activity_id in ews_activity_ids:
            api_model.complete(
                cr, nurse, ews_activity_id, observation_values)

    def get_refused_count_sql(self):
        return """
        SELECT rc.count::INTEGER FROM wdb_refused_obs_count AS rc
        JOIN nh_clinical_location AS loc
        ON rc.location_id = loc.id
        WHERE loc.id = {ward};
        """.format(ward=self.eobs_ward_id)

    def get_refused_count(self):
        self.cr.execute(self.get_refused_count_sql())
        count = self.cr.dictfetchall()
        return count[0].get('count') if count else 0

    def test_returns_correct_number_of_patients(self):
        """
        Test initial count is correct based on demo data.
        """
        self.assertEqual(self.get_refused_count(), 0)

    def test_returns_correct_number_of_patients_after_new_refusal(self):
        """
        Test refused obs count increments when a new patient starts refusing.
        """
        self.complete_observation(
            self.user_id, [self.patient_id], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 1)

    def test_returns_correct_number_of_patients_after_full_obs(self):
        """
        Test refused obs count decreases by 1 when a patient who was refusing
        has a full observation taken
        """
        self.complete_observation(
            self.user_id, [self.patient_id], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 1)
        self.complete_observation(
            self.user_id, [self.patient_id], LOW_RISK_DATA)
        self.assertEqual(self.get_refused_count(), 0)

    def test_returns_correct_number_of_patients_after_partial_obs(self):
        """
        Test refused obs count stays the same when a patient who was refusing
        has a partial observation taken
        """
        self.complete_observation(
            self.user_id, [self.patient_id], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 1)
        self.complete_observation(
            self.user_id, [self.patient_id], PARTIAL_DATA)
        self.assertEqual(self.get_refused_count(), 1)

    def test_returns_correct_number_of_patients_after_pme(self):
        """
        Test refused obs decreases by 1 when a patient who was refusing is
        put on PME
        """
        self.complete_observation(
            self.user_id, [self.patient_id], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 1)
        spell = self.spell_model.browse(self.spell_id)
        spell.write({'obs_stop': True})
        pme_model = self.env['nh.clinical.patient_monitoring_exception']
        activity_id = pme_model.create_activity(
            {},
            {'reason': 1, 'spell': spell.id}
        )
        activity_model = self.env['nh.activity']
        pme_activity = activity_model.browse(activity_id)
        pme_activity.spell_activity_id = spell.activity_id
        pme_model.start(activity_id)
        self.assertEqual(self.get_refused_count(), 0)

    def test_returns_correct_number_of_patients_after_transfer_in(self):
        """
        Test refused obs stays the same when a patient in another ward who
        was refusing is transferred to the ward
        """
        self.complete_observation(
            self.user_id, [self.patient_id], REFUSED_DATA)
        self.complete_observation(
            self.user_id, [self.patient_2_id], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 1)
        api_model = self.registry('nh.eobs.api')
        time.sleep(2)
        # transfer over to ward A
        api_model.transfer(
            self.cr, self.adt_id, 'TESTHN001', {'location': 'TESTWARD2'})
        api_model.transfer(
            self.cr, self.adt_id, 'TESTHN002', {'location': 'TESTWARD'})
        # place them in bed
        activity_model = self.registry('nh.activity')
        placement_id = activity_model.search(self.cr, self.sc_id, [
            ['data_model', '=', 'nh.clinical.patient.placement'],
            ['patient_id', '=', self.patient_2_id],
            ['state', 'not in', ['completed', 'cancelled']]
        ])[0]
        activity_model.submit(self.cr, self.sc_id, placement_id, {
            'suggested_location_id': self.eobs_ward_id,
            'location_id': self.bed_ids[0]
        })
        activity_model.complete(self.cr, self.sc_id, placement_id)
        # ensure count isn't changed
        self.assertEqual(self.get_refused_count(), 0)

    def test_returns_correct_number_of_patients_after_transfer_out(self):
        """
        Test refused obs stays the same when a patient who is refusing is
        transferred to another ward
        """
        self.complete_observation(
            self.user_id, [self.patient_id], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 1)
        api_model = self.registry('nh.eobs.api')
        # transfer over to ward A
        time.sleep(2)
        api_model.transfer(
            self.cr, self.adt_id, 'TESTHN001', {'location': 'TESTWARD2'})
        self.assertEqual(self.get_refused_count(), 0)

    def test_returns_correct_number_of_patients_after_obs_restart(self):
        """
        Test refused obs doesn't increase after a patient who was refusing is
        put on pme and then put on obs restart
        """
        self.complete_observation(
            self.user_id, [self.patient_id], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 1)
        time.sleep(2)
        spell = self.spell_model.browse(self.spell_id)
        spell.write({'obs_stop': True})
        wardboard_model = self.env['nh.clinical.wardboard']
        self.pme_reason = \
            self.env['nh.clinical.patient_monitoring_exception.reason']
        reason = self.pme_reason.browse(1)
        wardboard = wardboard_model.browse(spell.id)
        wardboard.start_patient_monitoring_exception(
            reason, self.spell_id, self.spell_activity_id)
        self.assertEqual(self.get_refused_count(), 0)
        wardboard.end_patient_monitoring_exception()
        self.assertEqual(self.get_refused_count(), 0)

    def test_returns_correct_number_of_patients_after_discharge(self):
        """
        Test refused obs count decreases when patient who was refused
        is discharged.
        """
        self.complete_observation(
            self.user_id, [self.patient_id], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 1)
        api_model = self.registry('nh.eobs.api')
        api_model.discharge(
            self.cr, self.adt_id, 'TESTHN001', {'location': 'DISL'})
        self.assertEqual(self.get_refused_count(), 0)
