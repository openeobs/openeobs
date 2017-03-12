from openerp.tests.common import TransactionCase


class TestSpellObsStopProperty(TransactionCase):
    """
    Test that the obs_stop column on nh.clinical.spell is present and can
    be set
    """

    def setUp(self):
        super(TestSpellObsStopProperty, self).setUp()
        self.spell_model = self.registry('nh.clinical.spell')
        self.patient_model = self.registry('nh.clinical.patient')
        cr, uid = self.cr, self.uid
        patient_id = self.patient_model.create(cr, uid, {
            'given_name': 'Test',
            'family_name': 'Icicles',
            'patient_identifier': '666',
            'other_identifier': '1337'
        })

        self.spell = self.spell_model.create(cr, uid, {
            'patient_id': patient_id,
            'pos_id': 1
        })

    def test_obs_stop_property(self):
        """
        Test that the obs_stop property is present on the nh.clinical.spell
        object
        """
        cr, uid = self.cr, self.uid
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertTrue('obs_stop' in spell)

    def test_obs_stop_defaults_to_false(self):
        """
        Test that the default value of obs_stop property is false
        """
        cr, uid = self.cr, self.uid
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertFalse(spell.get('obs_stop', True))

    def test_set_obs_stop_to_true(self):
        """
        Test that the obs_stop property can be set to 'true'
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell, {'obs_stop': True})
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertTrue(spell.get('obs_stop', False))

    def test_set_obs_stop_to_false(self):
        """
        Test that the obs_stop property can be set to 'false'
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell, {'obs_stop': False})
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertFalse(spell.get('obs_stop', True))
