# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase

from openerp.addons.nh_ews.tests.common import clinical_risk_sample_data


class TestGetActivitiesForSpell(TransactionCase):
    def setUp(self):
        super(TestGetActivitiesForSpell, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.create_patient_and_spell()
        self.test_utils.copy_instance_variables(self)
        self.api_model = self.env['nh.eobs.api']

    def test_returns_none_for_null_values(self):
        self.test_utils.create_and_complete_ews_obs_activity(
            self.patient.id, self.spell.id,
            clinical_risk_sample_data.HIGH_RISK_DATA
        )
        obs_activities = self.api_model.get_activities_for_spell(
            self.spell.id, 'ews'
        )

        self.assertEqual(1, len(obs_activities))
        null_values = eval(obs_activities[0]['null_values'])
        none_values = eval(obs_activities[0]['none_values'])
        all_null_field_names = set(null_values + none_values)

        expected = {i: None for i in all_null_field_names}
        actual = {i: obs_activities[0][i] for i in all_null_field_names}

        self.assertEqual(expected, actual)
