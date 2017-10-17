from openerp.tests.common import TransactionCase


class TestSpellRefusingObsProperty(TransactionCase):
    """
    Test that the rrefusing_obs column on nh.clinical.spell is present and can
    be set
    """

    def setUp(self):
        super(TestSpellRefusingObsProperty, self).setUp()
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

    def test_refusing_obs_property(self):
        """
        Test that the refusing_obs property is present on the nh.clinical.spell
        object
        """
        cr, uid = self.cr, self.uid
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertTrue('refusing_obs' in spell)

    def test_refusing_obs_defaults_to_false(self):
        """
        Test that the default value of refusing_obs property is false
        """
        cr, uid = self.cr, self.uid
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertFalse(spell.get('refusing_obs', True))

    def test_set_refusing_obs_to_true(self):
        """
        Test that the refusing_obs property can be set to 'true'
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell, {'refusing_obs': True})
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertTrue(spell.get('refusing_obs', False))

    def test_set_refusing_obs_to_false(self):
        """
        Test that the refusing_obs property can be set to 'false'
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell, {'refusing_obs': False})
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertFalse(spell.get('refusing_obs', True))
