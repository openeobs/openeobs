from openerp.tests.common import SingleTransactionCase


class TestSpellManagementPatientUpdate(SingleTransactionCase):
    """
    Test that updating the name of a Patient record for a spell then updates
    the spell management board
    """

    def setUp(self):
        super(TestSpellManagementPatientUpdate, self).setUp()
        cr, uid = self.cr, self.uid
        self.patient_pool = self.registry('nh.clinical.patient')
        self.location_pool = self.registry('nh.clinical.location')
        self.user_pool = self.registry('res.users')
        self.spellboard_pool = self.registry('nh.clinical.spellboard')
        self.spell_pool = self.registry('nh.clinical.spell')
        self.api_pool = self.registry('nh.eobs.api')

        # Setup ADT if not installed
        adt = self.user_pool.search(cr, uid, [['login', '=', 'adt']])
        if not adt:
            adt = self.user_pool.create(cr, uid, {
                'login': 'adt',
                'password': 'adt',
                'name': 'ADT',
                'groups_id': [[4, 20]],
                'category_id': [[4, 1]],
                'pos_id': 1,
                'pos_ids': [[6, 0, [1]]]
            })
        else:
            adt = adt[0]

        # Create a patient
        self.api_pool.register(cr, adt, 'HOSPTESTPATIENT', {
            'given_name': 'Test',
            'family_name': 'Patient',
            'patient_identifier': 'NHSTESTPATIENT'
        })
        patient = self.patient_pool.search(cr, uid, [
            ['other_identifier', '=', 'HOSPTESTPATIENT']
        ])[0]
        self.patient_id = patient

        # Create a Ward
        self.location_pool.create(cr, uid, {
            'usage': 'ward',
            'type': 'poc',
            'name': 'Test Ward',
            'code': 'TESTWARD',
            'parent_id': 1
        })
        location = self.location_pool.search(cr, uid, [
            ['code', '=', 'TESTWARD']
        ])[0]

        # Create a patient visit
        self.spell_id = self.spellboard_pool.create(cr, adt, {
            'patient_id': patient,
            'location_id': location,
            'code': 'TESTPATIENTSPELL',
            'start_date': '2016-07-18 00:00:00'
        })

    def test_updates_patient_name(self):
        """
        Check that on updating the patient name on the patient object the
        spellboard object has the correct name
        """
        cr, uid = self.cr, self.uid
        self.patient_pool.write(cr, uid, self.patient_id, {
            'given_name': 'Updated-Test'
        })
        spell = self.spellboard_pool.read(cr, uid, self.spell_id)[0]
        self.assertEqual(
            spell.get('patient_id', [0, ''])[1],
            'Patient, Updated-Test'
        )
