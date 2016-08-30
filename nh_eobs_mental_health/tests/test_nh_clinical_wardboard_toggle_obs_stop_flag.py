from openerp.tests.common import TransactionCase


class TestNHClinicalWardBoardToggleObsStopFlag(TransactionCase):
    """
    Test the toggle Stop Observation button
    """

    def setUp(self):
        super(TestNHClinicalWardBoardToggleObsStopFlag, self).setUp()
        self.spell_model = self.registry('nh.clinical.spell')
        self.patient_model = self.registry('nh.clinical.patient')
        self.wardboard_model = self.registry('nh.clinical.wardboard')
        cr, uid = self.cr, self.uid
        self.patient_id = self.patient_model.create(cr, uid, {
            'given_name': 'Test',
            'family_name': 'Icicles',
            'patient_identifier': '666',
            'other_identifier': '1337'
        })

        self.spell = self.spell_model.create(cr, uid, {
            'patient_id': self.patient_id,
            'pos_id': 1
        })

    def test_changes_flag_false_to_true(self):
        """
        Test that toggle_obs_stop raises osv exception when spell has open
        escalation tasks
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell, {'obs_stop': False})
        self.wardboard_model.toggle_obs_stop_flag(
            cr, uid, self.spell, context={'test': 'has_activities'})
        flag = self.spell_model.read(cr, uid, self.spell, ['obs_stop'])
        self.assertTrue(flag.get('obs_stop'))

    def test_changes_flag_true_to_false(self):
        """
        Test that toggle_obs_stop raises osv exception when spell has open
        escalation tasks
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell, {'obs_stop': True})
        self.wardboard_model.toggle_obs_stop_flag(
            cr, uid, self.spell, context={'test': 'has_activities'})
        flag = self.spell_model.read(cr, uid, self.spell, ['obs_stop'])
        self.assertFalse(flag.get('obs_stop'))
