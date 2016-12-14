from openerp.tests.common import TransactionCase
from openerp.addons.nh_ews.tests.common.clinical_risk_sample_data import \
    REFUSED_DATA, LOW_RISK_DATA, PARTIAL_DATA


class TestRefusedObsCount(TransactionCase):
    """
    Test that the refused obs count SQL View on ward dashboard is correct
    """

    def setUp(self):
        super(TestRefusedObsCount, self).setUp()
        location_model = self.env['nh.clinical.location']
        self.spell_model = self.env['nh.clinical.spell']
        self.user_model = self.env['res.users']
        self.ward = location_model.search([['code', '=', 'A']]).ids[0]
        self.nurse_id = \
            self.user_model.search([['login', '=', 'nasir']]).ids[0]
        self.nurse_id2 = self.user_model.search([['login', '=', 'nat']]).ids[0]
        # there are existing refused obs in the demo data
        patient_ids = [1, 2, 3]
        self.complete_observation(self.nurse_id, patient_ids, REFUSED_DATA)

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
        """.format(ward=self.ward)

    def get_refused_count(self):
        self.cr.execute(self.get_refused_count_sql())
        count = self.cr.dictfetchall()
        return count[0].get('count') if count else None

    def test_returns_correct_number_of_patients(self):
        """
        Test initial count is correct based on demo data.
        """
        self.assertEqual(self.get_refused_count(), 4)

    def test_returns_correct_number_of_patients_after_new_refusal(self):
        """
        Test refused obs count increments when a new patient starts refusing.
        """
        self.complete_observation(self.nurse_id2, [4], REFUSED_DATA)
        self.assertEqual(self.get_refused_count(), 5)

    def test_returns_correct_number_of_patients_after_full_obs(self):
        """
        Test refused obs count decreases by 1 when a patient who was refusing
        has a full observation taken
        """
        self.complete_observation(self.nurse_id, [3], LOW_RISK_DATA)
        self.assertEqual(self.get_refused_count(), 3)

    def test_returns_correct_number_of_patients_after_partial_obs(self):
        """
        Test refused obs count stays the same when a patient who was refusing
        has a partial observation taken
        """
        self.complete_observation(self.nurse_id, [3], PARTIAL_DATA)
        self.assertEqual(self.get_refused_count(), 4)

    def test_returns_correct_number_of_patients_after_pme(self):
        """
        Test refused obs decreases by 1 when a patient who was refusing is
        put on PME
        """
        spell = self.spell_model.browse(1)
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
        self.assertEqual(self.get_refused_count(), 3)

    def test_returns_correct_number_of_patients_after_transfer(self):
        """
        Test refused obs stays the same when a patient in another ward who
        was refusing is transferred to the ward
        """
        api_model = self.registry('nh.eobs.api')
        # get patient from ward B
        nurse_id = self.user_model.search([['login', '=', 'neely']])[0].id
        self.complete_observation(nurse_id, [41], REFUSED_DATA)
        # transfer over to ward A
        adt_user = self.user_model.search([['login', '=', 'adt']])[0].id
        api_model.transfer(self.cr, adt_user, 'HOSNUM0041', {'location': 'A'})
        # place them in bed
        sc_id = self.user_model.search([['login', '=', 'waino']])[0].id
        activity_model = self.registry('nh.activity')
        placement_id = activity_model.search(self.cr, self.uid, [
            ['data_model', '=', 'nh.clinical.patient.placement'],
            ['patient_id', '=', 41],
            ['state', 'not in', ['completed', 'cancelled']]
        ])[0]
        api_model.complete(self.cr, sc_id, placement_id, {
            'suggested_location_id': 3,
            'location_id': 32
        })
        # ensure count isn't changed
        self.assertEqual(self.get_refused_count(), 4)

    def test_returns_correct_number_of_patients_after_obs_restart(self):
        """
        Test refused obs doesn't increase after a patient who was refusing is
        put on pme and then put on obs restart
        """
        spell = self.spell_model.browse(1)
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
        wardboard_model = self.env['nh.clinical.wardboard']
        wardboard = wardboard_model.browse(spell.id)
        wardboard.end_patient_monitoring_exception()
        self.assertEqual(self.get_refused_count(), 3)
