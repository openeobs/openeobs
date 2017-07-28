# Part of Open eObs. See LICENSE file for full copyright and licensing details.
from openerp.tests.common import TransactionCase


class TestReportPrintedFlags(TransactionCase):
    """ Test the report_printed flags are added to the models """

    def setUp(self):
        super(TestReportPrintedFlags, self).setUp()
        self.test_utils = self.env['nh.clinical.test_utils']
        self.spell_model = self.env['nh.clinical.spell']
        self.location_model = self.env['nh.clinical.location']

    def test_flag_set_on_spell(self):
        """
        Test that the spell model has the report_printed key and
        it's False by default
        """
        flag_present = 'report_printed' in self.spell_model
        flag_value = self.spell_model._defaults['report_printed']
        self.assertEqual(flag_present, True,
                         'Flag not set on Spell class properly')
        self.assertEqual(flag_value, False,
                         'Flag value not set correctly')

    def test_flag_set_on_location(self):
        """
        Test that the location model has the report_printed key and
        it's False by default
        """
        flag_present = 'backup_observations' in self.location_model
        flag_value = self.location_model._defaults['backup_observations']
        self.assertEqual(flag_present, True,
                         'Flag not set on location class properly')
        self.assertEqual(flag_value, False, 'Flag value not set correctly')
