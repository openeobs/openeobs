from openerp.tests.common import TransactionCase


class TestGetSpells(TransactionCase):
    """
    Test getting the ID of the spells that need printing
    """

    def setUp(self):
        """
        Set up the tests
        """
        super(TestGetSpells, self).setUp()
        self.api_model = self.env['nh.eobs.api']
        self.test_utils = self.env['nh.clinical.test_utils']
        self.test_utils.admit_and_place_patient()
        self.test_utils.ward.backup_observations = True
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

    def test_supplied_spell_id(self):
        """
        Test that when passed a spell_id that the get_spells method just
        returns that as a list
        """
        self.assertEqual(
            [1],
            self.api_model.get_spells(1)
        )

    def test_supplied_spell_ids(self):
        """
        Test that when passed a list of spell_ids that get_spells returns that
        list
        """
        self.assertEqual(
            [6, 6, 6],
            self.api_model.get_spells([6, 6, 6])
        )

    def test_finds_spells(self):
        """
        Test that when no spell_ids are passed that get_spells looks for spells
        that are in locations that have backup_observations enabled and that
        have observations that need to printed
        """
        self.test_utils.get_open_obs()
        self.test_utils.complete_obs(self.ews_data)
        self.assertEqual(
            [self.test_utils.spell.id],
            self.api_model.get_spells()
        )

    def test_finds_no_spells(self):
        """
        Test that when no spell_ids are passed that get_spells looks for spells
        that are in locations that have backup_observations enabled and that
        have observations that need to printed. If none are found it returns
        an empty list
        """
        self.test_utils.spell.report_printed = True
        self.assertEqual([], self.api_model.get_spells())
