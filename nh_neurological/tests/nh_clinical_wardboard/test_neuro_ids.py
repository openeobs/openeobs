# -*- coding: utf-8 -*-
from openerp.addons.nh_neurological.tests.common \
    import neurological_fixtures
from openerp.tests.common import TransactionCase


class TestNeuroIds(TransactionCase):
    """Test `neuro_ids` field on `nh.clinical.wardboard`."""
    def setUp(self):
        super(TestNeuroIds, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.wardboard_model = self.env['nh.clinical.wardboard']
        self.test_utils.admit_and_place_patient()
        self.test_utils.copy_instance_variables(self)

        self.neuro_obs_1 = self.test_utils.create_and_complete_neuro_obs(
            self.patient.id, neurological_fixtures.SAMPLE_DATA,
        )
        self.neuro_obs_2 = self.test_utils.create_and_complete_neuro_obs(
            self.patient.id, neurological_fixtures.SAMPLE_DATA,
        )
        self.neuro_obs_3 = self.test_utils.create_and_complete_neuro_obs(
            self.patient.id, neurological_fixtures.SAMPLE_DATA,
        )

    def test_neuro_ids(self):
        """
        Test `neuro_ids` field is correctly populated.
        """
        wardboard = self.wardboard_model.get_by_spell_activity_id(
            self.spell_activity.id
        )
        neuro_ids = [neuro.activity_id.id for neuro in wardboard.neuro_ids]
        neuro_ids.reverse()
        self.assertEqual(
            [self.neuro_obs_1, self.neuro_obs_2, self.neuro_obs_3],
            neuro_ids
        )
