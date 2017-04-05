from openerp.tests.common import TransactionCase


class TestWardboardAcuityIndex(TransactionCase):
    """
    Test that the Acuity Index field on nh.clinical.wardboard is functioning
    as intended
    """

    def setUp(self):
        """
        Ward A will have a patient with a completed PME, a patient with a
        cancelled PME and 3 patients with active PMEs
        """
        super(TestWardboardAcuityIndex, self).setUp()
        location_model = self.env['nh.clinical.location']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        spell_model = self.env['nh.clinical.spell']
        activity_model = self.env['nh.activity']
        self.refused_spell = 23
        ward_a = location_model.search([['code', '=', 'A']])[0]
        obs_stop_spells = spell_model.search([
            ['patient_id', 'in', ward_a.patient_ids.ids],
            ['location_id.usage', '=', 'bed'],
            ['obs_stop', '=', True]
        ])
        restarted_obs = activity_model.search([
            ['data_model', '=', 'nh.clinical.pme.obs_stop'],
            ['state', 'in', ['completed', 'cancelled']],
            ['spell_activity_id.patient_id', 'in', ward_a.patient_ids.ids]
        ])
        restarted_obs_spells = [
            activity.spell_activity_id.data_ref.id
            for activity in restarted_obs]
        clinical_risk_spells = spell_model.search([
            ['patient_id', 'in', ward_a.patient_ids.ids],
            ['location_id.usage', '=', 'bed'],
            ['obs_stop', '=', False],
            ['id', 'not in', restarted_obs_spells],
            ['id', '!=', self.refused_spell]
        ])

        self.obs_stop_spells = obs_stop_spells.ids
        self.restarted_obs_spells = restarted_obs_spells
        self.clinical_risk_spells = clinical_risk_spells.ids

    def test_wardboard_acuity_index_obs_stop(self):
        """
        Test that there are three patients with ObsStop acuity_index
        """
        for spell in self.obs_stop_spells:
            wardboard = self.wardboard_model.browse(spell)
            self.assertEqual(wardboard.acuity_index, 'ObsStop')

    def test_wardboard_acuity_index_restarted_obs(self):
        """
        Test that there are two patients with NoScore acuity_index
        """
        for spell in self.restarted_obs_spells:
            wardboard = self.wardboard_model.browse(spell)
            self.assertEqual(wardboard.acuity_index, 'NoScore')

    def test_wardboard_acuity_index_clinical_risk(self):
        """
        Test that the others have the acuity_index of their clinical risk
        """
        for spell in self.clinical_risk_spells:
            wardboard = self.wardboard_model.browse(spell)
            self.assertEqual(wardboard.acuity_index, wardboard.clinical_risk)

    def test_wardboard_acuity_index_refused(self):
        """
        Test that the spell with the refused status has the correct
        acuity_index
        """
        wardboard = self.wardboard_model.browse(self.refused_spell)
        self.assertEqual(wardboard.acuity_index, 'Refused')
