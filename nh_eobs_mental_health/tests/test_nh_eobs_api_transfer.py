from openerp.tests.common import SingleTransactionCase


class TestNHeObsAPITransfer(SingleTransactionCase):
    """
    Test that transferring a patient set's their obs_stop flag to False
    """

    @classmethod
    def setUpClass(cls):
        super(TestNHeObsAPITransfer, cls).setUpClass()
        cls.api_model = cls.registry('nh.eobs.api')
        cls.spell_model = cls.registry('nh.clinical.spell')
        cls.patient_model = cls.registry('nh.clinical.patient')
        cls.location_model = cls.registry('nh.clinical.location')
        cls.user_model = cls.registry('res.users')
        cls.pos_model = cls.registry('nh.clinical.pos')
        cls.activity_model = cls.registry('nh.activity')

        cr, uid = cls.cr, cls.uid
        hosp_id_search = cls.location_model.search(
            cr, uid, [['usage', '=', 'hospital']]
        )
        if hosp_id_search:
            cls.hospital_id = hosp_id_search[0]
        else:
            raise ValueError('Could not find hospital ID')

        pos_id_search = cls.pos_model.search(
            cr, uid, [['location_id', '=', cls.hospital_id]]
        )
        if pos_id_search:
            cls.pos_id = pos_id_search[0]
        else:
            raise ValueError('Could not find POS with location ID of hospital')

        cls.user_model.write(cr, uid, uid, {
            'pos_id': cls.pos_id,
            'pos_ids': [[4, cls.pos_id]]
        })

        cls.location_model.create(
            cr, uid, {
                'name': 'Ward0',
                'code': 'W0',
                'usage': 'ward',
                'parent_id': cls.hospital_id,
                'type': 'poc'
            }
        )

        cls.location_model.create(
            cr, uid, {
                'name': 'Ward1',
                'code': 'W1',
                'usage': 'ward',
                'parent_id': cls.hospital_id,
                'type': 'poc'
            }
        )

        # register, admit and place patient
        cls.patient_id = cls.api_model.register(cr, uid, 'TESTHN001', {
            'family_name': 'Testersen',
            'given_name': 'Test'
        })

        cls.api_model.admit(
            cr, uid, 'TESTHN001', {'location': 'W0'}
        )

        cls.spell_id = cls.spell_model.search(
            cr, uid, [['patient_id', '=', cls.patient_id]])[0]

        def patch_spell_search(*args, **kwargs):
            return [cls.spell_id]

        # Need to patch out the spell_search as it doesn't find the newly
        # created spell for some reason
        cls.spell_model._patch_method('search', patch_spell_search)

    @classmethod
    def tearDownClass(cls):
        cls.spell_model._revert_method('search')
        super(TestNHeObsAPITransfer, cls).tearDownClass()

    def test_transfer_changes_flag(self):
        """
        TEst that when transferring a patient with a set obs_stop flag the flag
        is changed
        """
        cr, uid = self.cr, self.uid
        self.spell_model.write(cr, uid, self.spell_id, {'obs_stop': True})
        self.api_model.transfer(
            cr, uid, 'TESTHN001', {'from_location': 'W0', 'location': 'W1'})
        spell = self.spell_model.read(cr, uid, self.spell_id, ['obs_stop'])
        self.assertFalse(spell.get('obs_stop', True))
