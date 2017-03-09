from openerp.tests.common import TransactionCase


class TestSpellRapidTranqProperty(TransactionCase):
    """
    Test that the rapid_tranq column on nh.clinical.spell is present and can
    be set
    """

    def setUp(self):
        super(TestSpellRapidTranqProperty, self).setUp()
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

    def test_rapid_tranq_property(self):
        """
        Test that the rapid_tranq property is present on the nh.clinical.spell
        object
        """
        cr, uid = self.cr, self.uid
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertTrue('rapid_tranq' in spell)

    def test_rapid_tranq_defaults_to_false(self):
        """
        Test that the default value of rapid_tranq property is false
        """
        cr, uid = self.cr, self.uid
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertFalse(spell.get('rapid_tranq', True))

    def test_set_rapid_tranq_to_true(self):
        """
        Test that the rapid_tranq property can be set to 'true'
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell, {'rapid_tranq': True})
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertTrue(spell.get('rapid_tranq', False))

    def test_set_rapid_tranq_to_false(self):
        """
        Test that the rapid_tranq property can be set to 'false'
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell, {'rapid_tranq': False})
        spell = self.spell_model.read(cr, uid, self.spell)
        self.assertFalse(spell.get('rapid_tranq', True))
